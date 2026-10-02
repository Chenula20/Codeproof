"""Pydantic models for CodeProof Backend API contracts."""

from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import datetime, timezone

# Keep legacy naive-UTC wire timestamps until a separately approved format migration.


# ── Project ──────────────────────────────────────────────────────────

class ProjectResponse(BaseModel):
    name: str
    languages: list[str]
    frameworks: list[str]


# ── Skills ───────────────────────────────────────────────────────────

class SkillsResponse(BaseModel):
    debugging: int
    api: int
    database: int
    authentication: int
    testing: int
    error_handling: int


# ── Sessions ─────────────────────────────────────────────────────────

class SessionCreateRequest(BaseModel):
    project_path: str = Field(..., description="Absolute path to the user's project")
    project_id: Optional[str] = Field(None, description="Optional project identifier")


class SessionCreateResponse(BaseModel):
    session_id: str
    project_id: str
    project_name: str
    languages: list[str]
    frameworks: list[str]
    skill_estimates: dict[str, int] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))


class SessionStatus(BaseModel):
    session_id: str
    project_id: str
    status: str  # "active" | "completed" | "error"
    current_step: Optional[str] = None
    challenges_completed: int = 0
    total_challenges: int = 0
    created_at: datetime
    updated_at: datetime


class SessionCloseRequest(BaseModel):
    session_id: str


# ── Challenges (for session workflow) ────────────────────────────────

class ChallengeSummary(BaseModel):
    id: str
    title: str
    difficulty: str
    skill: str


class ChallengeDetail(ChallengeSummary):
    description: str
    scenario: str
    expected_fix: str
    hints: list[str] = []


class HintRequest(BaseModel):
    challenge_id: str
    user_id: Optional[str] = None
    level: int = 1
    developer_progress: str = "Not started"
    developer_question: Optional[str] = None


class HintResponse(BaseModel):
    challenge_id: str
    hint: str
    level: int
    next_level_available: bool = True


class ExplanationRequest(BaseModel):
    challenge_id: str
    explanation: str
    user_id: Optional[str] = None


class ExplanationResponse(BaseModel):
    challenge_id: str
    classification: str
    feedback: str
    score: float
    passed: bool


# ── Patch Lab ────────────────────────────────────────────────────────

class PatchValidateRequest(BaseModel):
    challenge_id: str
    patch: str  # unified diff format


class PatchValidateResponse(BaseModel):
    valid: bool
    files_changed: int = 0
    message: str


# ── Sandbox ──────────────────────────────────────────────────────────

class SandboxRunRequest(BaseModel):
    challenge_id: str
    patch: str  # unified diff format


class TestCounts(BaseModel):
    """Completed test outcomes; failed includes test errors, skipped is not passing."""
    total: int = Field(strict=True, ge=0)
    passed: int = Field(strict=True, ge=0)
    failed: int = Field(strict=True, ge=0)
    skipped: int = Field(strict=True, ge=0)

    @model_validator(mode="after")
    def consistent_total(self):
        if self.total != self.passed + self.failed + self.skipped:
            raise ValueError("Test outcome counts do not match total")
        return self


class TestCountProjection(BaseModel):
    # Legacy integers are compatibility placeholders when test_counts is None.
    test_counts: TestCounts | None = None
    tests_total: int = 0
    tests_passed: int = 0
    tests_failed: int = 0

    @model_validator(mode="after")
    def project_known_counts(self):
        if self.test_counts is not None:
            self.tests_total = self.test_counts.total
            self.tests_passed = self.test_counts.passed
            self.tests_failed = self.test_counts.failed
        return self


class SandboxResult(TestCountProjection):
    status: str  # "passed" | "failed" | "error"
    tests_total: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    runtime_errors: list[str] = []
    security_warnings: list[str] = []
    output: str = ""
    duration_ms: int = 0


# ── Release Readiness ────────────────────────────────────────────────

class ReleaseReadiness(TestCountProjection):
    status: str  # "READY" | "WARNING" | "BLOCKED"
    critical_issues: int = 0
    warnings: int = 0
    tests_passed: int = 0
    tests_total: int = 0


# ── Analysis (for AI integration) ────────────────────────────────────

class AnalysisRequest(BaseModel):
    project_path: str


class AnalysisResponse(BaseModel):
    project_id: str
    summary: str
    technologies: list[str]
    issues: list[str]
    skills: list[str]


class SkillMapResponse(BaseModel):
    project_id: str
    skills: list[str]
    skill_estimates: list[dict]


# ── AI Coaching Contract Models (re-export for session workflow) ──────

class ChallengeContext(BaseModel):
    """Structured context for a coding challenge (matches AI contract)."""
    challenge_id: str
    title: str
    description: str
    difficulty: str
    target_skill: str
    problem_statement: str
    relevant_code_excerpts: list[str] = []
    error_logs: list[str] = []
    expected_concepts: list[str] = []
    relevant_files: list[str] = []
    project_summary: Optional[str] = None
    metadata: dict = {}


class AIHintRequest(BaseModel):
    challenge_id: str
    hint_level: int
    developer_progress: str = "Not started"
    developer_question: Optional[str] = None
    challenge_context: ChallengeContext


class AIHintResponse(BaseModel):
    hint_level: int
    hint_content: str
    next_level_available: bool


class AIExplanationRequest(BaseModel):
    challenge_context: ChallengeContext
    developer_explanation: str
    expected_concepts: list[str]


class AIExplanationResponse(BaseModel):
    user_explanation: str
    classification: str
    score: float
    feedback: str
    passed: bool


class AIPatchRequest(BaseModel):
    issue_description: str
    project_snapshot: dict  # ProjectSnapshot as dict
    target_files: list[str]


class AIPatchResponse(BaseModel):
    patch_id: str
    description: str
    diff: str
    affected_files: list[str]
    validation_warnings: list[str] = []
    risk_level: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))