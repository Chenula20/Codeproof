"""Pydantic models for CodeProof Backend API contracts."""

from pydantic import BaseModel, Field
from typing import Optional


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


# ── Challenges ───────────────────────────────────────────────────────

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


class HintResponse(BaseModel):
    challenge_id: str
    hint: str
    level: int


class ExplanationRequest(BaseModel):
    challenge_id: str
    explanation: str
    user_id: Optional[str] = None


class ExplanationResponse(BaseModel):
    challenge_id: str
    classification: str
    feedback: str


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


class SandboxResult(BaseModel):
    status: str  # "passed" | "failed" | "error"
    tests_total: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    runtime_errors: list[str] = []
    security_warnings: list[str] = []
    output: str = ""
    duration_ms: int = 0


# ── Release Readiness ────────────────────────────────────────────────

class ReleaseReadiness(BaseModel):
    status: str  # "READY" | "WARNING" | "BLOCKED"
    critical_issues: int = 0
    warnings: int = 0
    tests_passed: int = 0
    tests_total: int = 0
