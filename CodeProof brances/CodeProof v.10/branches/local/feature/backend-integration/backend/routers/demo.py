"""Deterministic demo-mode API for the CodeProof UI screenshots.

All data comes from in-memory fixtures (backend/services/demo_fixtures.py).
No disk writes, no AI calls, no Docker — results are simulated and labeled.
"""
from fastapi import APIRouter, HTTPException, Query

from backend.demo_models import (
    ChallengeStartResponse, DemoExplanationRequest, DemoExplanationResponse,
    DemoReadinessResponse, DemoStateResponse, FileContentResponse,
    FileTreeResponse, HintRequest, HintResponse, OverviewResponse,
    PatchApplyResponse, PatchProposalResponse, SkillMapResponse,
    ValidationResponse,
)
from backend.services import demo_fixtures

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/overview", response_model=OverviewResponse)
async def demo_overview() -> OverviewResponse:
    return demo_fixtures.get_overview()


@router.get("/skill-map", response_model=SkillMapResponse)
async def demo_skill_map() -> SkillMapResponse:
    return demo_fixtures.get_skill_map()


@router.get("/files", response_model=FileTreeResponse)
async def demo_files(source: str = Query(default="original", pattern="^(original|challenge)$")) -> FileTreeResponse:
    return demo_fixtures.get_file_tree(source)


@router.get("/file", response_model=FileContentResponse)
async def demo_file(path: str, source: str = Query(default="original", pattern="^(original|challenge)$")) -> FileContentResponse:
    content = demo_fixtures.get_file_content(path, source)
    if content is None:
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    return content


@router.post("/challenge/start", response_model=ChallengeStartResponse)
async def demo_start_challenge() -> ChallengeStartResponse:
    return demo_fixtures.start_challenge()


@router.get("/challenge", response_model=ChallengeStartResponse)
async def demo_get_challenge() -> ChallengeStartResponse:
    return demo_fixtures.start_challenge()


@router.post("/hint", response_model=HintResponse)
async def demo_hint(payload: HintRequest) -> HintResponse:
    return demo_fixtures.get_hint(payload.level)


@router.post("/explanation", response_model=DemoExplanationResponse)
async def demo_explanation(payload: DemoExplanationRequest) -> DemoExplanationResponse:
    classification, feedback, unlocked = demo_fixtures.evaluate_explanation(payload.explanation)
    return DemoExplanationResponse(classification=classification, feedback=feedback, patch_unlocked=unlocked)


@router.get("/patch", response_model=PatchProposalResponse)
async def demo_patch() -> PatchProposalResponse:
    try:
        return demo_fixtures.get_patch_proposal()
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.post("/patch/apply", response_model=PatchApplyResponse)
async def demo_patch_apply() -> PatchApplyResponse:
    try:
        return demo_fixtures.apply_patch()
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.post("/validation", response_model=ValidationResponse)
async def demo_validation() -> ValidationResponse:
    return demo_fixtures.run_validation()


@router.get("/release-readiness", response_model=DemoReadinessResponse)
async def demo_release_readiness() -> DemoReadinessResponse:
    return demo_fixtures.get_readiness()


@router.get("/state", response_model=DemoStateResponse)
async def demo_state() -> DemoStateResponse:
    return demo_fixtures.get_state()


@router.post("/reset", response_model=DemoStateResponse)
async def demo_reset() -> DemoStateResponse:
    demo_fixtures.reset()
    return demo_fixtures.get_state()
