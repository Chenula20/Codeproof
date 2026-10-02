from typing import Literal

from pydantic import BaseModel, Field
from ai.models import ExplanationClassification
from backend.models import TestCounts


class OpenProject(BaseModel):
    path: str = Field(default="", max_length=4096)


class AnalysisRequest(BaseModel):
    use_ai: bool = False


class ChallengeRequest(BaseModel):
    issue: str = Field(default="", max_length=4000)
    target_file: str = Field(default="", max_length=512)
    incident_id: str | None = Field(default=None, max_length=128)


class ExplanationRequest(BaseModel):
    explanation: str = Field(min_length=10, max_length=8000)


class RunRequest(BaseModel):
    runner: Literal["python-unittest", "python-pytest", "node-test"] = "python-unittest"


class Skill(BaseModel):
    category: str
    relevance: float
    confidence: float
    evidence: list[str]


class Evaluation(BaseModel):
    classification: ExplanationClassification
    passed: bool
    feedback: str = Field(min_length=1)
    score: float = Field(strict=True, allow_inf_nan=False, ge=0.0, le=1.0)


class PatchView(BaseModel):
    description: str
    diff: str
    affected_files: list[str]
    risk_level: str = "medium"
    validation_warnings: list[str] = Field(default_factory=list)


class Validation(BaseModel):
    status: Literal["passed", "failed", "error", "unavailable", "timeout", "not_run"] = "not_run"
    test_counts: TestCounts | None = None
    simulated: bool = False
    output: str = "Validation has not run."
    duration_ms: int = 0
    original_unchanged: bool | None = None
    checks: list[str] = Field(default_factory=list)


class IncidentView(BaseModel):
    id: str
    title: str
    goal: str
    target_file: str


class SessionView(BaseModel):
    id: str
    name: str
    sample: bool
    mode: str = "Local backend"
    provider: str = "Local inspection"
    phase: str = "analyzed"
    files: dict[str, str]
    summary: str
    technologies: list[str]
    issues: list[str]
    skills: list[Skill]
    supported_incidents: list[IncidentView] = Field(default_factory=list)
    active_incident: IncidentView | None = None
    challenge_title: str = ""
    challenge_description: str = ""
    relevant_files: list[str] = Field(default_factory=list)
    hints: list[str] = Field(default_factory=list)
    evaluation: Evaluation | None = None
    patch: PatchView | None = None
    validation: Validation = Field(default_factory=Validation)
    activity: list[str] = Field(default_factory=list)
