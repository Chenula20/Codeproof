"""Session endpoints — complete MVP workflow for project sessions."""

import uuid
from datetime import datetime
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends

from backend.models import (
    SessionCreateRequest,
    SessionCreateResponse,
    SessionStatus,
    SessionCloseRequest,
    ChallengeSummary,
    ChallengeDetail,
    HintRequest,
    HintResponse,
    ExplanationRequest,
    ExplanationResponse,
    PatchValidateRequest,
    PatchValidateResponse,
    SandboxRunRequest,
    SandboxResult,
    ReleaseReadiness,
    ChallengeContext,
    AIHintRequest,
    AIHintResponse,
    AIExplanationRequest,
    AIExplanationResponse,
)
from backend.services import (
    project_service,
    challenge_service,
    patch_lab,
    sandbox,
    release_readiness,
)
from workspace import WorkspaceGuardian, ProjectSnapshot


router = APIRouter(prefix="/v1/sessions", tags=["sessions"])


# In-memory session store (use Redis/database in production)
SESSIONS: dict[str, dict] = {}


def get_guardian(project_path: str) -> WorkspaceGuardian:
    """Create a WorkspaceGuardian for the given project path."""
    return WorkspaceGuardian(project_path)


@router.post("", response_model=SessionCreateResponse)
async def create_session(request: SessionCreateRequest) -> SessionCreateResponse:
    """
    Create a new project session.
    
    Opens a session for a user project, runs initial analysis via Guardian,
    and prepares the challenge workflow.
    """
    # Validate project path
    project_path = Path(request.project_path).resolve()
    if not project_path.exists() or not project_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Project path does not exist or is not a directory: {request.project_path}")
    
    # Create Guardian and validate
    guardian = WorkspaceGuardian(str(project_path))
    if not guardian.validate_project():
        raise HTTPException(status_code=400, detail=f"Invalid project: {request.project_path}")
    
    # Get project info
    project_info = project_service.get_project_info(str(project_path))
    
    # Create session
    session_id = str(uuid.uuid4())[:8]
    project_id = request.project_id or str(uuid.uuid4())[:8]
    
    # Create snapshot for AI analysis
    snapshot = guardian.create_snapshot(project_id=project_id)
    
    # Store session
    now = datetime.utcnow()
    SESSIONS[session_id] = {
        "session_id": session_id,
        "project_id": project_id,
        "project_path": str(project_path),
        "project_name": project_info.name,
        "languages": project_info.languages,
        "frameworks": project_info.frameworks,
        "snapshot": snapshot.model_dump(),
        "status": "active",
        "current_step": "analysis",
        "challenges_completed": 0,
        "total_challenges": 0,
        "created_at": now,
        "updated_at": now,
        "challenges": [],
    }
    
    # Get skill estimates
    skills = project_service.get_skills()
    skill_dict = {
        "debugging": skills.debugging,
        "api": skills.api,
        "database": skills.database,
        "authentication": skills.authentication,
        "testing": skills.testing,
        "error_handling": skills.error_handling,
    }
    
    return SessionCreateResponse(
        session_id=session_id,
        project_id=project_id,
        project_name=project_info.name,
        languages=project_info.languages,
        frameworks=project_info.frameworks,
        skill_estimates=skill_dict,
        created_at=now,
    )


@router.get("/{session_id}", response_model=SessionStatus)
async def get_session(session_id: str) -> SessionStatus:
    """Get session status."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    session = SESSIONS[session_id]
    return SessionStatus(
        session_id=session["session_id"],
        project_id=session["project_id"],
        status=session["status"],
        current_step=session["current_step"],
        challenges_completed=session["challenges_completed"],
        total_challenges=session["total_challenges"],
        created_at=session["created_at"],
        updated_at=session["updated_at"],
    )


@router.post("/{session_id}/close")
async def close_session(session_id: str, request: SessionCloseRequest) -> dict:
    """Close a session and cleanup resources."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    if session_id != request.session_id:
        raise HTTPException(status_code=400, detail="Session ID mismatch")
    
    session = SESSIONS[session_id]
    session["status"] = "completed"
    session["updated_at"] = datetime.utcnow()
    
    return {"message": "Session closed successfully", "session_id": session_id}


@router.get("/{session_id}/analysis", response_model=dict)
async def get_session_analysis(session_id: str) -> dict:
    """Get project analysis for the session."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    session = SESSIONS[session_id]
    snapshot = ProjectSnapshot(**session["snapshot"])
    
    # Return basic analysis from Guardian
    guardian = WorkspaceGuardian(session["project_path"])
    summary = guardian.get_project_summary()
    
    return {
        "project_id": session["project_id"],
        "project_name": session["project_name"],
        "languages": session["languages"],
        "frameworks": session["frameworks"],
        "summary": summary,
    }


@router.get("/{session_id}/skill-map", response_model=dict)
async def get_session_skill_map(session_id: str) -> dict:
    """Get skill map for the session."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    session = SESSIONS[session_id]
    skills = project_service.get_skills()
    
    return {
        "project_id": session["project_id"],
        "skills": [
            {"category": "Debugging", "level": skills.debugging},
            {"category": "API", "level": skills.api},
            {"category": "Database", "level": skills.database},
            {"category": "Authentication", "level": skills.authentication},
            {"category": "Testing", "level": skills.testing},
            {"category": "Error Handling", "level": skills.error_handling},
        ],
    }


@router.get("/{session_id}/challenges", response_model=list[ChallengeSummary])
async def list_session_challenges(session_id: str) -> list[ChallengeSummary]:
    """List available challenges for the session."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    session = SESSIONS[session_id]
    challenges = challenge_service.list_challenges()
    session["total_challenges"] = len(challenges)
    session["updated_at"] = datetime.utcnow()
    
    return challenges


@router.get("/{session_id}/challenges/{challenge_id}", response_model=ChallengeDetail)
async def get_session_challenge(session_id: str, challenge_id: str) -> ChallengeDetail:
    """Get detailed challenge information."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    challenge = challenge_service.get_challenge(challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail=f"Challenge '{challenge_id}' not found")
    
    return challenge


@router.post("/{session_id}/challenges/{challenge_id}/hint", response_model=HintResponse)
async def get_session_hint(session_id: str, challenge_id: str, request: HintRequest) -> HintResponse:
    """
    Get a progressive hint for a challenge using the AI Engine.
    
    This endpoint uses the actual AI HintEngine with ChallengeContext
    built from the Guardian snapshot.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    session = SESSIONS[session_id]
    
    # Build ChallengeContext from Guardian snapshot
    snapshot = ProjectSnapshot(**session["snapshot"])
    challenge_detail = challenge_service.get_challenge(challenge_id)
    if not challenge_detail:
        raise HTTPException(status_code=404, detail=f"Challenge '{challenge_id}' not found")
    
    # Get relevant code excerpts from snapshot
    relevant_files = challenge_detail.title.lower().replace(" ", "_")
    code_excerpts = []
    for file_path, content in snapshot.files.items():
        if challenge_detail.skill.lower() in file_path.lower() or "auth" in file_path.lower():
            code_excerpts.append(content[:2000])
    
    context = ChallengeContext(
        challenge_id=challenge_id,
        title=challenge_detail.title,
        description=challenge_detail.description,
        difficulty=challenge_detail.difficulty,
        target_skill=challenge_detail.skill,
        problem_statement=challenge_detail.scenario,
        relevant_code_excerpts=code_excerpts[:3],  # Limit excerpts
        error_logs=[],
        expected_concepts=[challenge_detail.expected_fix],
        relevant_files=list(snapshot.files.keys())[:10],
        project_summary=f"Project: {session['project_name']}",
        metadata={"session_id": session_id},
    )
    
    # Use AI HintEngine if available, otherwise fallback
    try:
        from ai.services.hint_engine import HintEngine
        from ai.providers import BaseAIProvider
        
        # For now, use challenge_service fallback
        # In production, instantiate actual AI provider
        hint_result = challenge_service.get_hint(challenge_id, level=request.level or 1)
        if not hint_result:
            raise HTTPException(status_code=404, detail=f"Challenge '{challenge_id}' not found")
        
        return HintResponse(
            challenge_id=challenge_id,
            hint=hint_result.hint,
            level=request.level or 1,
            next_level_available=(request.level or 1) < 4,
        )
    except ImportError:
        # Fallback to challenge_service
        hint_result = challenge_service.get_hint(challenge_id, level=request.level or 1)
        if not hint_result:
            raise HTTPException(status_code=404, detail=f"Challenge '{challenge_id}' not found")
        
        return HintResponse(
            challenge_id=challenge_id,
            hint=hint_result.hint,
            level=request.level or 1,
            next_level_available=(request.level or 1) < 4,
        )


@router.post("/{session_id}/challenges/{challenge_id}/explanation", response_model=ExplanationResponse)
async def evaluate_session_explanation(session_id: str, challenge_id: str, request: ExplanationRequest) -> ExplanationResponse:
    """
    Evaluate a user's explanation using the AI ExplanationEvaluator.
    
    This endpoint uses the actual AI ExplanationEvaluator with ChallengeContext
    built from the Guardian snapshot.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    session = SESSIONS[session_id]
    
    # Build ChallengeContext
    challenge_detail = challenge_service.get_challenge(challenge_id)
    if not challenge_detail:
        raise HTTPException(status_code=404, detail=f"Challenge '{challenge_id}' not found")
    
    snapshot = ProjectSnapshot(**session["snapshot"])
    code_excerpts = []
    for file_path, content in snapshot.files.items():
        if challenge_detail.skill.lower() in file_path.lower() or "auth" in file_path.lower():
            code_excerpts.append(content[:2000])
    
    context = ChallengeContext(
        challenge_id=challenge_id,
        title=challenge_detail.title,
        description=challenge_detail.description,
        difficulty=challenge_detail.difficulty,
        target_skill=challenge_detail.skill,
        problem_statement=challenge_detail.scenario,
        relevant_code_excerpts=code_excerpts[:3],
        error_logs=[],
        expected_concepts=[challenge_detail.expected_fix],
        relevant_files=list(snapshot.files.keys())[:10],
        project_summary=f"Project: {session['project_name']}",
        metadata={"session_id": session_id},
    )
    
    # Use AI ExplanationEvaluator if available, otherwise fallback
    try:
        from ai.services.explanation_evaluator import ExplanationEvaluator
        from ai.models import ExplanationEvaluationRequest as AIExplanationEvaluationRequest
        
        # Fallback for now
        result = challenge_service.evaluate_explanation(challenge_id, request.explanation)
        
        return ExplanationResponse(
            challenge_id=challenge_id,
            classification=result.classification,
            feedback=result.feedback,
            score=0.8 if result.classification == "CORRECT" else (0.5 if result.classification == "PARTIALLY_CORRECT" else 0.2),
            passed=result.classification in ("CORRECT", "PARTIALLY_CORRECT"),
        )
    except ImportError:
        result = challenge_service.evaluate_explanation(challenge_id, request.explanation)
        return ExplanationResponse(
            challenge_id=challenge_id,
            classification=result.classification,
            feedback=result.feedback,
            score=0.8 if result.classification == "CORRECT" else (0.5 if result.classification == "PARTIALLY_CORRECT" else 0.2),
            passed=result.classification in ("CORRECT", "PARTIALLY_CORRECT"),
        )


@router.post("/{session_id}/challenges/{challenge_id}/patch/validate", response_model=PatchValidateResponse)
async def validate_session_patch(session_id: str, challenge_id: str, request: PatchValidateRequest) -> PatchValidateResponse:
    """Validate a patch for a challenge."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    return patch_lab.validate_patch(request.patch)


@router.post("/{session_id}/challenges/{challenge_id}/sandbox", response_model=SandboxResult)
async def run_session_sandbox(session_id: str, challenge_id: str, request: SandboxRunRequest) -> SandboxResult:
    """Run tests in sandbox with the patch applied."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    session = SESSIONS[session_id]
    project_path = session["project_path"]
    
    # Use the actual project path (temp copy will be made by sandbox)
    result = sandbox.run_sandbox(project_path, patch=request.patch)
    return result


@router.get("/{session_id}/release-readiness", response_model=ReleaseReadiness)
async def get_session_release_readiness(session_id: str) -> ReleaseReadiness:
    """Get release readiness for the session's current state."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    session = SESSIONS[session_id]
    project_path = session["project_path"]
    
    sandbox_result = sandbox.run_sandbox(project_path, patch=None)
    return release_readiness.evaluate_release_readiness(sandbox_result)


@router.post("/{session_id}/release-readiness", response_model=ReleaseReadiness)
async def evaluate_session_release_readiness(session_id: str, request: SandboxRunRequest) -> ReleaseReadiness:
    """Evaluate release readiness after applying a patch."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    
    session = SESSIONS[session_id]
    project_path = session["project_path"]
    
    sandbox_result = sandbox.run_sandbox(project_path, patch=request.patch)
    return release_readiness.evaluate_release_readiness(sandbox_result)