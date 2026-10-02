"""Challenge endpoints."""

from fastapi import APIRouter, HTTPException

from backend.models import (
    ChallengeSummary,
    ChallengeDetail,
    HintRequest,
    HintResponse,
    ExplanationRequest,
    ExplanationResponse,
)
from backend.services import challenge_service

router = APIRouter(prefix="/challenges", tags=["challenges"])


@router.get("", response_model=list[ChallengeSummary])
async def list_challenges() -> list[ChallengeSummary]:
    """List all available challenges."""
    return challenge_service.list_challenges()


@router.get("/{challenge_id}", response_model=ChallengeDetail)
async def get_challenge(challenge_id: str) -> ChallengeDetail:
    """Get detailed information about a specific challenge."""
    challenge = challenge_service.get_challenge(challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail=f"Challenge '{challenge_id}' not found")
    return challenge


@router.post("/{challenge_id}/hint", response_model=HintResponse)
async def get_hint(challenge_id: str, request: HintRequest) -> HintResponse:
    """Get a progressive hint for a challenge."""
    hint = challenge_service.get_hint(challenge_id, level=1)
    if not hint:
        raise HTTPException(status_code=404, detail=f"Challenge '{challenge_id}' not found")
    return hint


@router.post("/{challenge_id}/explanation", response_model=ExplanationResponse)
async def evaluate_explanation(challenge_id: str, request: ExplanationRequest) -> ExplanationResponse:
    """Evaluate a user's explanation of the challenge."""
    result = challenge_service.evaluate_explanation(challenge_id, request.explanation)
    return result
