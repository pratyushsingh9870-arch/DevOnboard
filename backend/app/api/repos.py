from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

from ..services.github_service import GitHubService
from ..database import get_db
from ..models.repository import Repository

router = APIRouter(
    prefix="/api/repos",
    tags=["repositories"]
)

github_service = GitHubService()


# -----------------------------
# Request Model
# -----------------------------
class AnalyzeRepoRequest(BaseModel):
    repo_url: str


# -----------------------------
# Response Model
# -----------------------------
class RepoAnalysisResponse(BaseModel):
    success: bool
    repository: Optional[Dict] = None
    tech_stack: Optional[Dict] = None
    file_count: Optional[int] = None
    saved_to_db: bool = False
    error: Optional[str] = None


# -----------------------------
# Analyze Repository
# -----------------------------
@router.post("/analyze", response_model=RepoAnalysisResponse)
async def analyze_repository(
    request: AnalyzeRepoRequest,
    db: Session = Depends(get_db)
):

    try:

        # Fetch repository info
        repo_info = github_service.get_repository(
            request.repo_url
        )

        if not repo_info:

            return RepoAnalysisResponse(
                success=False,
                error="Could not fetch repository"
            )

        # Detect tech stack
        tech_stack = github_service.detect_tech_stack(
            request.repo_url
        )

        # Get repository structure
        structure = github_service.get_repository_structure(
            request.repo_url
        )

        file_count = len(structure) if structure else 0

        # Check if repo already exists
        existing_repo = db.query(Repository).filter(
            Repository.full_name == repo_info["full_name"]
        ).first()

        if existing_repo:

            # Update existing repo
            existing_repo.description = repo_info["description"]

            existing_repo.primary_language = repo_info["primary_language"]

            existing_repo.languages = repo_info["languages"]

            existing_repo.detected_stack = tech_stack

            existing_repo.stars = repo_info["stars"]

            existing_repo.forks = repo_info["forks"]

            existing_repo.file_count = file_count

            existing_repo.last_analyzed = datetime.utcnow()

            db.commit()

            saved_to_db = True

        else:

            # Create new repo
            new_repo = Repository(
                name=repo_info["name"],
                full_name=repo_info["full_name"],
                github_url=repo_info["url"],
                description=repo_info["description"],
                primary_language=repo_info["primary_language"],
                languages=repo_info["languages"],
                detected_stack=tech_stack,
                stars=repo_info["stars"],
                forks=repo_info["forks"],
                file_count=file_count,
                last_analyzed=datetime.utcnow()
            )

            db.add(new_repo)

            db.commit()

            saved_to_db = True

        return RepoAnalysisResponse(
            success=True,
            repository=repo_info,
            tech_stack=tech_stack,
            file_count=file_count,
            saved_to_db=saved_to_db
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# -----------------------------
# List Saved Repositories
# -----------------------------
@router.get("/list")
async def list_repositories(
    db: Session = Depends(get_db)
):

    repos = db.query(Repository).all()

    return {
        "count": len(repos),

        "repositories": [

            {
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "primary_language": repo.primary_language,
                "stars": repo.stars,
                "file_count": repo.file_count,
                "last_analyzed": (
                    repo.last_analyzed.isoformat()
                    if repo.last_analyzed
                    else None
                )
            }

            for repo in repos
        ]
    }


# -----------------------------
# Test GitHub Connection
# -----------------------------
@router.get("/test")
async def test_github():

    try:

        test_repo = "facebook/react"

        repo_info = github_service.get_repository(
            test_repo
        )

        if repo_info:

            return {
                "status": "success",
                "message": "GitHub API connected successfully",
                "test_repo": repo_info["full_name"]
            }

        else:

            return {
                "status": "error",
                "message": "Could not connect to GitHub API"
            }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }