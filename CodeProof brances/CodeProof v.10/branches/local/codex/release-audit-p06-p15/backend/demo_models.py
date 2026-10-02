"""Pydantic models for the deterministic CodeProof demo UI API.

These contracts serve the browser demo workspace only. All coaching and
assessment values are deterministic fixtures, never AI results, and no
endpoint in this module performs disk writes.
"""

from pydantic import BaseModel


class OverviewResponse(BaseModel):
    name: str
    tagline: str
    description: str
    technologies: list[str]
    review_focus: str


class SkillEntry(BaseModel):
    key: str
    label: str
    relevance: int
    confidence: int
    evidence: list[str]


class SkillMapResponse(BaseModel):
    skills: list[SkillEntry]


class FileNode(BaseModel):
    path: str
    name: str
    kind: str  # "file" | "dir"


class FileTreeResponse(BaseModel):
    source: str  # "original" | "challenge"
    nodes: list[FileNode]


class FileContentResponse(BaseModel):
    path: str
    source: str
    content: str
    highlights: list[int] = []


class ChallengeStartResponse(BaseModel):
    id: str
    title: str
    difficulty: str
    skill: str
    description: str
    investigation_files: list[str]
    error_output: str


class HintRequest(BaseModel):
    level: int


class HintResponse(BaseModel):
    level: int
    total: int
    title: str
    hint: str


class DemoExplanationRequest(BaseModel):
    explanation: str


class DemoExplanationResponse(BaseModel):
    classification: str  # "CORRECT" | "PARTIALLY_CORRECT" | "INCORRECT"
    feedback: str
    patch_unlocked: bool


class PatchProposalResponse(BaseModel):
    title: str
    affected_file: str
    risk: str
    notes: list[str]
    diff: str


class PatchApplyResponse(BaseModel):
    applied: bool
    file: str
    content: str
    message: str


class SimulatedTest(BaseModel):
    name: str
    detail: str
    status: str  # "passed"
    duration_ms: int


class ValidationResponse(BaseModel):
    status: str
    simulated: bool
    tests: list[SimulatedTest]
    output: str
    duration_ms: int


class ReadinessCheck(BaseModel):
    key: str
    label: str
    passed: bool


class DemoReadinessResponse(BaseModel):
    status: str  # "READY_FOR_REVIEW" | "IN_PROGRESS"
    simulated: bool
    checks: list[ReadinessCheck]
    note: str


class DemoStateResponse(BaseModel):
    challenge_started: bool
    hints_revealed: int
    patch_unlocked: bool
    patch_applied: bool
    validated: bool
    validation_passed: bool
