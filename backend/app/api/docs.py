from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict

from ..services.ai_service import AIService
from ..services.github_service import GitHubService
from ..services.script_generator import ScriptGenerator
from ..database import get_db
from ..models.repository import Repository
from ..models.documentation import Documentation

router = APIRouter(prefix="/api/docs", tags=["documentation"])

ai_service = AIService()
github_service = GitHubService()
script_generator = ScriptGenerator()


class GenerateDocsRequest(BaseModel):
    repo_url: str

class ScriptResponse(BaseModel):
    success: bool
    bash_script: Optional[str] = None
    powershell_script: Optional[str] = None
    docker_compose: Optional[str] = None
    error: Optional[str] = None

class CompleteOnboardingResponse(BaseModel):
    success: bool
    documentation: Optional[Dict] = None
    scripts: Optional[Dict] = None
    repository: Optional[Dict] = None
    error: Optional[str] = None


def inject_repo_stats(readme: str, repo_context: dict) -> str:
    """
    Inject real repository stats into the README.
    This guarantees stars/forks/contributors always appear,
    regardless of what the AI generated.
    """
    stars = repo_context.get('stars', 0)
    forks = repo_context.get('forks', 0)
    watchers = repo_context.get('watchers', 0)
    contributors = repo_context.get('contributors', 1)
    license_name = repo_context.get('license', 'MIT')
    updated = repo_context.get('last_updated', '')
    primary_language = repo_context.get('primary_language', 'Python')
    full_name = repo_context.get('full_name', '')

    # Build badges
    badges = (
        f"![Stars](https://img.shields.io/badge/stars-{stars:,}-yellow?style=flat-square) "
        f"![Forks](https://img.shields.io/badge/forks-{forks:,}-blue?style=flat-square) "
        f"![Language](https://img.shields.io/badge/language-{primary_language}-green?style=flat-square) "
        f"![License](https://img.shields.io/badge/license-{license_name.replace(' ', '_')}-orange?style=flat-square)"
    )

    # Build stats table
    stats_table = (
        "\n## Repository Stats\n\n"
        "| Metric | Value |\n"
        "|--------|-------|\n"
        f"| Stars | {stars:,} |\n"
        f"| Forks | {forks:,} |\n"
        f"| Watchers | {watchers:,} |\n"
        f"| Contributors | {contributors} |\n"
        f"| License | {license_name} |\n"
        f"| Last Updated | {updated} |\n\n"
    )

    # Inject badges after the first heading
    if "img.shields.io" not in readme:
        lines = readme.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("# "):
                lines.insert(i + 1, "\n" + badges + "\n")
                break
        readme = "\n".join(lines)

    # Inject stats table before Contributing section
    if "Repository Stats" not in readme:
        if "## 🤝 Contributing" in readme:
            readme = readme.replace(
                "## 🤝 Contributing",
                stats_table + "## 🤝 Contributing"
            )
        elif "## Contributing" in readme:
            readme = readme.replace(
                "## Contributing",
                stats_table + "## Contributing"
            )
        else:
            readme += "\n" + stats_table

    return readme


@router.get("/test")
async def test_ai():
    try:
        if ai_service.test_connection():
            return {
                "status": "success",
                "message": "OpenRouter AI connected successfully",
                "model": ai_service.model
            }
        return {"status": "error", "message": "Could not connect to OpenRouter AI"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/generate-complete", response_model=CompleteOnboardingResponse)
async def generate_complete_onboarding(
    request: GenerateDocsRequest,
    db: Session = Depends(get_db)
):
    try:
        print(f"Generating for: {request.repo_url}")

        # Step 1: Get repo info
        repo_info = github_service.get_repository(request.repo_url)
        if not repo_info:
            return CompleteOnboardingResponse(
                success=False,
                error="Could not fetch repository. Check the URL!"
            )

        print(f"Repo found: {repo_info['name']}")

        # Step 2: Read file contents and build context
        repo_context = github_service.get_repository_context(request.repo_url)

        # Step 3: Detect tech stack
        tech_stack = github_service.detect_tech_stack(request.repo_url)
        print(f"Languages: {repo_context.get('languages', [])}")
        print(f"Frameworks: {tech_stack.get('frameworks', [])}")

        # Step 4: Generate all documentation in one AI call
        print("Generating documentation...")
        all_docs = ai_service.generate_all_docs(repo_context)

        readme = all_docs.get("readme", "")
        setup_guide = all_docs.get("setup_guide", "")
        architecture = all_docs.get("architecture", "")

        # Step 5: Inject real stats into README (guaranteed accuracy)
        if readme:
            readme = inject_repo_stats(readme, repo_context)

        # Step 6: Generate platform scripts
        print("Generating scripts...")
        bash_script = script_generator.generate_bash_script(
            repo_name=repo_context["name"],
            languages=repo_context["languages"],
            frameworks=tech_stack.get("frameworks", [])
        )

        powershell_script = script_generator.generate_powershell_script(
            repo_name=repo_context["name"],
            languages=repo_context["languages"],
            frameworks=tech_stack.get("frameworks", [])
        )

        docker_compose = script_generator.generate_docker_compose(
            repo_name=repo_context["name"],
            languages=repo_context["languages"],
            frameworks=tech_stack.get("frameworks", []),
            has_database=len(tech_stack.get("databases", [])) > 0
        )

        # Step 7: Save to database
        try:
            repo_db = db.query(Repository).filter(
                Repository.full_name == repo_info["full_name"]
            ).first()

            if not repo_db:
                repo_db = Repository(
                    name=repo_info["name"],
                    full_name=repo_info["full_name"],
                    github_url=repo_info["url"],
                    description=repo_info["description"],
                    primary_language=repo_info["primary_language"],
                    languages=repo_info["languages"],
                    detected_stack=tech_stack,
                    stars=repo_info["stars"],
                    forks=repo_info["forks"],
                    file_count=len(repo_context.get("all_files", []))
                )
                db.add(repo_db)
                db.commit()
                db.refresh(repo_db)

            for doc_type, content in [
                ("readme", readme),
                ("setup", setup_guide),
                ("architecture", architecture)
            ]:
                if content:
                    db.query(Documentation).filter(
                        Documentation.repo_id == repo_db.id,
                        Documentation.doc_type == doc_type
                    ).delete()
                    db.add(Documentation(
                        repo_id=repo_db.id,
                        doc_type=doc_type,
                        content=content
                    ))
            db.commit()
            print("Saved to database.")

        except Exception as db_error:
            print(f"DB save failed (continuing): {db_error}")

        return CompleteOnboardingResponse(
            success=True,
            documentation={
                "readme": readme,
                "setup_guide": setup_guide,
                "architecture": architecture
            },
            scripts={
                "bash": bash_script,
                "powershell": powershell_script,
                "docker_compose": docker_compose
            },
            repository={
                "name": repo_info["name"],
                "languages": repo_context["languages"],
                "frameworks": tech_stack.get("frameworks", []),
                "databases": tech_stack.get("databases", []),
                "stars": repo_info["stars"],
                "file_count": len(repo_context.get("all_files", []))
            }
        )

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-scripts", response_model=ScriptResponse)
async def generate_setup_scripts(request: GenerateDocsRequest):
    try:
        repo_info = github_service.get_repository(request.repo_url)
        if not repo_info:
            return ScriptResponse(success=False, error="Could not fetch repository")

        tech_stack = github_service.detect_tech_stack(request.repo_url)

        bash_script = script_generator.generate_bash_script(
            repo_name=repo_info["name"],
            languages=repo_info["languages"],
            frameworks=tech_stack.get("frameworks", [])
        )

        powershell_script = script_generator.generate_powershell_script(
            repo_name=repo_info["name"],
            languages=repo_info["languages"],
            frameworks=tech_stack.get("frameworks", [])
        )

        docker_compose = script_generator.generate_docker_compose(
            repo_name=repo_info["name"],
            languages=repo_info["languages"],
            frameworks=tech_stack.get("frameworks", []),
            has_database=len(tech_stack.get("databases", [])) > 0
        )

        return ScriptResponse(
            success=True,
            bash_script=bash_script,
            powershell_script=powershell_script,
            docker_compose=docker_compose
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/repo/{repo_full_name:path}")
async def get_repository_docs(
    repo_full_name: str,
    db: Session = Depends(get_db)
):
    repo = db.query(Repository).filter(
        Repository.full_name == repo_full_name
    ).first()

    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    docs = db.query(Documentation).filter(
        Documentation.repo_id == repo.id
    ).all()

    return {
        "repository": repo.full_name,
        "documentation": {
            doc.doc_type: doc.content for doc in docs
        }
    }