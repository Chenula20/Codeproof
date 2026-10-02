"""Project and skills endpoints."""

from fastapi import APIRouter

from backend.models import ProjectResponse, SkillsResponse
from backend.services import project_service

router = APIRouter(tags=["project"])


@router.get("/project", response_model=ProjectResponse)
async def get_project() -> ProjectResponse:
    """Get project metadata (name, languages, frameworks)."""
    return project_service.get_project_info()


@router.get("/analysis", response_model=SkillsResponse)
async def get_analysis() -> SkillsResponse:
    """Get engineering skill analysis for the current project."""
    return project_service.get_skills()


@router.get("/skills", response_model=SkillsResponse)
async def get_skills() -> SkillsResponse:
    """Get engineering skill estimates."""
    return project_service.get_skills()
