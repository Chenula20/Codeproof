from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ProjectAnalysis(BaseModel):
    """Represents the analysis of a user's project."""
    project_id: str = Field(..., description="Unique identifier for the project")
    summary: str = Field(..., description="High-level summary of the project")
    technologies: List[str] = Field(default_factory=list, description="Technologies detected in the project")
    issues: List[str] = Field(default_factory=list, description="Issues identified during analysis")
    skills: List[str] = Field(default_factory=list, description="Engineering skills relevant to the project")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of analysis")


class EngineeringSkillMap(BaseModel):
    """Maps engineering skills required for a project."""
    project_id: str = Field(..., description="Unique identifier for the project")
    skills: List[str] = Field(default_factory=list, description="Required engineering skills")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of skill map generation")