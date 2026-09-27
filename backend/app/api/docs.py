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


router = APIRouter(
    prefix="/api/docs",
    tags=["documentation"]
)

ai_service = AIService()
github_service = GitHubService()
script_generator = ScriptGenerator()


# ============================================================
# REQUEST / RESPONSE MODELS
# ============================================================

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


# ============================================================
# HELPER: INJECT REAL REPOSITORY STATS
# ============================================================

def inject_repo_stats(
    readme: str,
    repo_context: dict
) -> str:
    """
    Inject real repository statistics into the generated README.

    Statistics come directly from GitHub repository data.
    """

    stars = repo_context.get("stars", 0)
    forks = repo_context.get("forks", 0)
    watchers = repo_context.get("watchers", 0)
    contributors = repo_context.get("contributors", 1)

    license_name = repo_context.get(
        "license",
        "MIT"
    )

    updated = repo_context.get(
        "last_updated",
        ""
    )

    primary_language = repo_context.get(
        "primary_language",
        "Unknown"
    )

    # --------------------------------------------------------
    # Build badges
    # --------------------------------------------------------

    badges = (
        f"![Stars](https://img.shields.io/badge/"
        f"stars-{stars:,}-yellow?style=flat-square) "

        f"![Forks](https://img.shields.io/badge/"
        f"forks-{forks:,}-blue?style=flat-square) "

        f"![Language](https://img.shields.io/badge/"
        f"language-{primary_language}-green?style=flat-square) "

        f"![License](https://img.shields.io/badge/"
        f"license-{license_name.replace(' ', '_')}-orange?style=flat-square)"
    )

    # --------------------------------------------------------
    # Build statistics table
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Inject badges after first H1
    # --------------------------------------------------------

    if "img.shields.io" not in readme:

        lines = readme.split("\n")

        for i, line in enumerate(lines):

            if line.startswith("# "):

                lines.insert(
                    i + 1,
                    "\n" + badges + "\n"
                )

                break

        readme = "\n".join(lines)

    # --------------------------------------------------------
    # Inject repository statistics
    # --------------------------------------------------------

    if "Repository Stats" not in readme:

        if "## 🤝 Contributing" in readme:

            readme = readme.replace(
                "## 🤝 Contributing",
                stats_table + "## 🤝 Contributing"
            )

        elif "##  Contributing" in readme:

            readme = readme.replace(
                "##  Contributing",
                stats_table + "##  Contributing"
            )

        elif "## Contributing" in readme:

            readme = readme.replace(
                "## Contributing",
                stats_table + "## Contributing"
            )

        else:

            readme += "\n" + stats_table

    return readme


# ============================================================
# HELPER: DETECT DOCKER EVIDENCE
# ============================================================

def has_docker_evidence(
    repo_context: dict
) -> bool:
    """
    Determine whether the repository contains actual Docker
    configuration files.

    Docker Compose should NOT be generated merely because the
    project uses JavaScript, Python, or another language.
    """

    all_files = repo_context.get(
        "all_files",
        []
    )

    docker_files = {
        "dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "compose.yml",
        "compose.yaml"
    }

    for file in all_files:

        filename = str(file).strip().lower()

        # Handle paths such as:
        # backend/Dockerfile
        # docker/Dockerfile
        # deployment/docker-compose.yml

        basename = filename.split("/")[-1]

        if basename in docker_files:
            return True

    return False


# ============================================================
# TEST AI CONNECTION
# ============================================================

@router.get("/test")
async def test_ai():

    try:

        if ai_service.test_connection():

            return {
                "status": "success",
                "message": "OpenRouter AI connected successfully",
                "model": ai_service.model
            }

        return {
            "status": "error",
            "message": "Could not connect to OpenRouter AI"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================
# GENERATE COMPLETE ONBOARDING
# ============================================================

@router.post(
    "/generate-complete",
    response_model=CompleteOnboardingResponse
)
async def generate_complete_onboarding(
    request: GenerateDocsRequest,
    db: Session = Depends(get_db)
):

    try:

        print("=" * 60)
        print(
            f"Generating onboarding for: "
            f"{request.repo_url}"
        )
        print("=" * 60)

        # ====================================================
        # STEP 1: GET BASIC REPOSITORY INFORMATION
        # ====================================================

        print(
            "\n[1/7] Fetching repository information..."
        )

        repo_info = github_service.get_repository(
            request.repo_url
        )

        if not repo_info:

            return CompleteOnboardingResponse(
                success=False,
                error=(
                    "Could not fetch repository. "
                    "Please check the GitHub URL and token."
                )
            )

        # ----------------------------------------------------
        # Validate required fields
        # ----------------------------------------------------

        required_repo_fields = [
            "name",
            "full_name",
            "url",
            "description",
            "primary_language",
            "languages",
            "stars",
            "forks"
        ]

        missing_fields = [
            field
            for field in required_repo_fields
            if field not in repo_info
        ]

        if missing_fields:

            return CompleteOnboardingResponse(
                success=False,
                error=(
                    "Repository information is incomplete. "
                    f"Missing fields: {missing_fields}"
                )
            )

        print(
            f"Repository found: "
            f"{repo_info['name']}"
        )

        print(
            f"Full name: "
            f"{repo_info['full_name']}"
        )

        print(
            f"Languages: "
            f"{repo_info['languages']}"
        )

        print(
            f"Stars: "
            f"{repo_info['stars']}"
        )

        print(
            f"Forks: "
            f"{repo_info['forks']}"
        )

        # ====================================================
        # STEP 2: BUILD DETAILED REPOSITORY CONTEXT
        # ====================================================

        print(
            "\n[2/7] Building repository context..."
        )

        repo_context = github_service.get_repository_context(
            request.repo_url
        )

        if not repo_context:

            return CompleteOnboardingResponse(
                success=False,
                error=(
                    "Could not build repository context. "
                    "GitHub file information could not be read."
                )
            )

        print(
            f"Context fields received: "
            f"{list(repo_context.keys())}"
        )

        # ----------------------------------------------------
        # Fill missing basic fields from repo_info
        # ----------------------------------------------------

        repo_context.setdefault(
            "name",
            repo_info["name"]
        )

        repo_context.setdefault(
            "full_name",
            repo_info["full_name"]
        )

        repo_context.setdefault(
            "url",
            repo_info["url"]
        )

        repo_context.setdefault(
            "description",
            repo_info["description"]
        )

        repo_context.setdefault(
            "primary_language",
            repo_info["primary_language"]
        )

        repo_context.setdefault(
            "languages",
            repo_info["languages"]
        )

        repo_context.setdefault(
            "stars",
            repo_info["stars"]
        )

        repo_context.setdefault(
            "forks",
            repo_info["forks"]
        )

        repo_context.setdefault(
            "all_files",
            []
        )

        print(
            f"Final context repository: "
            f"{repo_context.get('name')}"
        )

        # ====================================================
        # STEP 3: DETECT TECHNOLOGY STACK
        # ====================================================

        print(
            "\n[3/7] Detecting technology stack..."
        )

        tech_stack = github_service.detect_tech_stack(
            request.repo_url
        )

        if not tech_stack:

            tech_stack = {
                "languages": repo_info.get(
                    "languages",
                    []
                ),
                "frameworks": [],
                "databases": [],
                "tools": []
            }

        tech_stack.setdefault(
            "languages",
            []
        )

        tech_stack.setdefault(
            "frameworks",
            []
        )

        tech_stack.setdefault(
            "databases",
            []
        )

        tech_stack.setdefault(
            "tools",
            []
        )

        print(
            f"Languages: "
            f"{repo_context.get('languages', [])}"
        )

        print(
            f"Frameworks: "
            f"{tech_stack.get('frameworks', [])}"
        )

        print(
            f"Databases: "
            f"{tech_stack.get('databases', [])}"
        )

        # ----------------------------------------------------
        # Detect Docker evidence
        # ----------------------------------------------------

        docker_detected = has_docker_evidence(
            repo_context
        )

        print(
            f"Docker evidence detected: "
            f"{docker_detected}"
        )

        # ====================================================
        # STEP 4: GENERATE AI DOCUMENTATION
        # ====================================================

        print(
            "\n[4/7] Generating documentation with AI..."
        )

        all_docs = ai_service.generate_all_docs(
            repo_context
        )

        if not all_docs:

            return CompleteOnboardingResponse(
                success=False,
                error=(
                    "AI documentation generation "
                    "returned no result."
                )
            )

        readme = all_docs.get(
            "readme",
            ""
        )

        setup_guide = all_docs.get(
            "setup_guide",
            ""
        )

        architecture = all_docs.get(
            "architecture",
            ""
        )

        print(
            f"README generated: "
            f"{bool(readme)}"
        )

        print(
            f"Setup guide generated: "
            f"{bool(setup_guide)}"
        )

        print(
            f"Architecture generated: "
            f"{bool(architecture)}"
        )

        # ====================================================
        # STEP 5: INJECT REAL GITHUB STATS
        # ====================================================

        print(
            "\n[5/7] Injecting real repository statistics..."
        )

        if readme:

            readme = inject_repo_stats(
                readme,
                repo_context
            )

        # ====================================================
        # STEP 6: GENERATE PLATFORM SCRIPTS
        # ====================================================

        print(
            "\n[6/7] Generating setup scripts..."
        )

        # ----------------------------------------------------
        # Bash
        # ----------------------------------------------------

        bash_script = (
            script_generator.generate_bash_script(
                repo_name=repo_info["name"],
                languages=repo_info["languages"],
                frameworks=tech_stack.get(
                    "frameworks",
                    []
                ),
                dependencies_file=(
                    "package.json"
                    if repo_context.get("package_json")
                    else (
                        "requirements.txt"
                        if repo_context.get("requirements")
                        else ""
                    )
                )
            )
        )

        # ----------------------------------------------------
        # PowerShell
        # ----------------------------------------------------

        powershell_script = (
            script_generator.generate_powershell_script(
                repo_name=repo_info["name"],
                languages=repo_info["languages"],
                frameworks=tech_stack.get(
                    "frameworks",
                    []
                ),
                dependencies_file=(
                    "package.json"
                    if repo_context.get("package_json")
                    else (
                        "requirements.txt"
                        if repo_context.get("requirements")
                        else ""
                    )
                )
            )
        )

        # ----------------------------------------------------
        # Docker Compose
        #
        # ONLY generate when Docker evidence exists.
        # ----------------------------------------------------

        docker_compose = None

        if docker_detected:

            docker_compose = (
                script_generator.generate_docker_compose(
                    repo_name=repo_info["name"],
                    languages=repo_info["languages"],
                    frameworks=tech_stack.get(
                        "frameworks",
                        []
                    ),
                    has_database=(
                        len(
                            tech_stack.get(
                                "databases",
                                []
                            )
                        ) > 0
                    )
                )
            )

            print(
                "Docker Compose generated."
            )

        else:

            print(
                "Docker Compose skipped: "
                "no Docker evidence found."
            )

        print(
            "Scripts generated successfully."
        )

        # ====================================================
        # STEP 7: SAVE TO DATABASE
        # ====================================================

        print(
            "\n[7/7] Saving results to database..."
        )

        try:

            repo_db = (
                db.query(Repository)
                .filter(
                    Repository.full_name
                    == repo_info["full_name"]
                )
                .first()
            )

            # ------------------------------------------------
            # Create repository record
            # ------------------------------------------------

            if not repo_db:

                repo_db = Repository(
                    name=repo_info["name"],
                    full_name=repo_info["full_name"],
                    github_url=repo_info["url"],
                    description=repo_info["description"],
                    primary_language=(
                        repo_info["primary_language"]
                    ),
                    languages=repo_info["languages"],
                    detected_stack=tech_stack,
                    stars=repo_info["stars"],
                    forks=repo_info["forks"],
                    file_count=len(
                        repo_context.get(
                            "all_files",
                            []
                        )
                    )
                )

                db.add(repo_db)

                db.commit()

                db.refresh(repo_db)

            # ------------------------------------------------
            # Save generated documentation
            # ------------------------------------------------

            documents = [
                ("readme", readme),
                ("setup", setup_guide),
                ("architecture", architecture)
            ]

            for doc_type, content in documents:

                if content:

                    db.query(
                        Documentation
                    ).filter(
                        Documentation.repo_id
                        == repo_db.id,
                        Documentation.doc_type
                        == doc_type
                    ).delete()

                    db.add(
                        Documentation(
                            repo_id=repo_db.id,
                            doc_type=doc_type,
                            content=content
                        )
                    )

            db.commit()

            print(
                "Documentation saved to database."
            )

        except Exception as db_error:

            # Database failure should not prevent the user
            # from receiving generated documentation.

            print(
                f"DB save failed "
                f"(continuing): {db_error}"
            )

        # ====================================================
        # RETURN COMPLETE RESPONSE
        # ====================================================

        print(
            "\nGeneration completed successfully."
        )

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
                "languages": repo_info["languages"],
                "frameworks": tech_stack.get(
                    "frameworks",
                    []
                ),
                "databases": tech_stack.get(
                    "databases",
                    []
                ),
                "stars": repo_info["stars"],
                "file_count": len(
                    repo_context.get(
                        "all_files",
                        []
                    )
                )
            }
        )

    except Exception as e:

        print(
            f"ERROR in generate_complete_onboarding: "
            f"{e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# GENERATE ONLY SCRIPTS
# ============================================================

@router.post(
    "/generate-scripts",
    response_model=ScriptResponse
)
async def generate_setup_scripts(
    request: GenerateDocsRequest
):

    try:

        # ----------------------------------------------------
        # Repository information
        # ----------------------------------------------------

        repo_info = github_service.get_repository(
            request.repo_url
        )

        if not repo_info:

            return ScriptResponse(
                success=False,
                error="Could not fetch repository"
            )

        # ----------------------------------------------------
        # Technology stack
        # ----------------------------------------------------

        tech_stack = github_service.detect_tech_stack(
            request.repo_url
        )

        if not tech_stack:

            tech_stack = {
                "languages": repo_info.get(
                    "languages",
                    []
                ),
                "frameworks": [],
                "databases": [],
                "tools": []
            }

        # ----------------------------------------------------
        # Get detailed repository context
        # ----------------------------------------------------

        repo_context = (
            github_service.get_repository_context(
                request.repo_url
            )
        )

        if not repo_context:

            repo_context = {
                "all_files": []
            }

        # ----------------------------------------------------
        # Docker detection
        # ----------------------------------------------------

        docker_detected = has_docker_evidence(
            repo_context
        )

        # ----------------------------------------------------
        # Bash
        # ----------------------------------------------------

        bash_script = (
            script_generator.generate_bash_script(
                repo_name=repo_info["name"],
                languages=repo_info["languages"],
                frameworks=tech_stack.get(
                    "frameworks",
                    []
                ),
                dependencies_file=(
                    "package.json"
                    if repo_context.get("package_json")
                    else (
                        "requirements.txt"
                        if repo_context.get("requirements")
                        else ""
                    )
                )
            )
        )

        # ----------------------------------------------------
        # PowerShell
        # ----------------------------------------------------

        powershell_script = (
            script_generator.generate_powershell_script(
                repo_name=repo_info["name"],
                languages=repo_info["languages"],
                frameworks=tech_stack.get(
                    "frameworks",
                    []
                ),
                dependencies_file=(
                    "package.json"
                    if repo_context.get("package_json")
                    else (
                        "requirements.txt"
                        if repo_context.get("requirements")
                        else ""
                    )
                )
            )
        )

        # ----------------------------------------------------
        # Docker Compose
        # ----------------------------------------------------

        docker_compose = None

        if docker_detected:

            docker_compose = (
                script_generator.generate_docker_compose(
                    repo_name=repo_info["name"],
                    languages=repo_info["languages"],
                    frameworks=tech_stack.get(
                        "frameworks",
                        []
                    ),
                    has_database=(
                        len(
                            tech_stack.get(
                                "databases",
                                []
                            )
                        ) > 0
                    )
                )
            )

        return ScriptResponse(

            success=True,

            bash_script=bash_script,

            powershell_script=powershell_script,

            docker_compose=docker_compose
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# GET SAVED REPOSITORY DOCUMENTATION
# ============================================================

@router.get(
    "/repo/{repo_full_name:path}"
)
async def get_repository_docs(
    repo_full_name: str,
    db: Session = Depends(get_db)
):

    repo = (
        db.query(Repository)
        .filter(
            Repository.full_name
            == repo_full_name
        )
        .first()
    )

    if not repo:

        raise HTTPException(
            status_code=404,
            detail="Repository not found"
        )

    docs = (
        db.query(Documentation)
        .filter(
            Documentation.repo_id
            == repo.id
        )
        .all()
    )

    return {
        "repository": repo.full_name,

        "documentation": {
            doc.doc_type: doc.content
            for doc in docs
        }
    }