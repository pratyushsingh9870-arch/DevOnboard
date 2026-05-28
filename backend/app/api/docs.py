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

# Initialize services
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
        print(f"\n🚀 Generating for: {request.repo_url}")

        # ✅ STEP 1: Get actual repo info from GitHub
        repo_info = github_service.get_repository(request.repo_url)
        if not repo_info:
            return CompleteOnboardingResponse(
                success=False,
                error="Could not fetch repository. Check the URL!"
            )

        print(f"✅ Repo found: {repo_info['name']}")

        # ✅ STEP 2: Read actual file contents
        print("📂 Reading file contents...")
        repo_context = github_service.get_repository_context(request.repo_url)

        # ✅ STEP 3: Detect real tech stack
        print("🔍 Detecting tech stack...")
        tech_stack = github_service.detect_tech_stack(request.repo_url)
        print(f"   Languages: {repo_context.get('languages', [])}")
        print(f"   Frameworks: {tech_stack.get('frameworks', [])}")

       # ONE call instead of THREE - 3x faster!
        # ONE call instead of THREE - 3x faster!
        print("🤖 Generating all docs in one AI call...")

        all_docs = ai_service.generate_all_docs(repo_context)

        readme = all_docs["readme"]
        setup_guide = all_docs["setup_guide"]
        architecture = all_docs["architecture"]
        # ✅ STEP 5: Generate platform-specific scripts
        print("⚡ Generating scripts...")
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

        # ✅ STEP 6: Save to database
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

            # Save documentation
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
            print("✅ Saved to database!")

        except Exception as db_error:
            print(f"⚠️ DB save failed (continuing): {db_error}")

        print("\n✅ Complete! Returning results.")

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
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-scripts", response_model=ScriptResponse)
async def generate_setup_scripts(request: GenerateDocsRequest):
    try:
        # ✅ Use real GitHub data
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