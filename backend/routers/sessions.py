"""The versioned local API consumed by the existing Flutter client."""
import hmac
import time
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from backend.session_models import OpenProject, AnalysisRequest, ChallengeRequest, ExplanationRequest, RunRequest, SessionView
from backend.services import sessions as service


def authorized(request: Request, authorization: str = Header(default='')):
    token = request.app.state.token
    if len(token) < 32:
        raise HTTPException(503, 'Set CODEPROOF_TOKEN to at least 32 characters, or use python -m backend.')
    if not hmac.compare_digest(authorization.encode(), ('Bearer ' + token).encode()):
        raise HTTPException(401, 'Invalid local service token')


router = APIRouter(prefix='/v1', tags=['connected sessions'], dependencies=[Depends(authorized)])


def get_session(request, session_id):
    session = request.app.state.sessions.get(session_id)
    if not session:
        raise HTTPException(404, 'Session not found')
    return session


@router.post('/sessions', response_model=SessionView)
async def open_project(request: Request, body: OpenProject):
    sessions = request.app.state.sessions
    for key, existing in list(sessions.items()):
        if time.monotonic() - existing.created > 7200 and not existing.lock.locked():
            existing.close()
            del sessions[key]
    if len(sessions) >= 8:
        raise HTTPException(409, 'Close an existing session first')
    session = service.open_session(body.path)
    sessions[session.view.id] = session
    return session.view


@router.delete('/sessions/{session_id}')
async def close_project(request: Request, session_id: str):
    session = get_session(request, session_id)
    async with session.lock:
        session.close()
        request.app.state.sessions.pop(session_id, None)
    return {'closed': True}


@router.post('/sessions/{session_id}/analysis', response_model=SessionView)
async def analysis(request: Request, session_id: str, body: AnalysisRequest):
    session = get_session(request, session_id)
    async with session.lock:
        session.check()
        await service.analyze(session, body.use_ai, request.app.state.provider_factory)
        return session.view


@router.post('/sessions/{session_id}/challenge', response_model=SessionView)
async def challenge(request: Request, session_id: str, body: ChallengeRequest):
    session = get_session(request, session_id)
    async with session.lock:
        session.check()
        if body.incident_id is not None:
            await service.break_app(session, body.incident_id)
        else:
            service.challenge(session, body.issue, body.target_file)
        return session.view


@router.post('/sessions/{session_id}/hint', response_model=SessionView)
async def hint(request: Request, session_id: str):
    session = get_session(request, session_id)
    async with session.lock:
        session.check()
        await service.hint(session, request.app.state.provider_factory)
        return session.view


@router.post('/sessions/{session_id}/explanation', response_model=SessionView)
async def explanation(request: Request, session_id: str, body: ExplanationRequest):
    session = get_session(request, session_id)
    async with session.lock:
        session.check()
        await service.explain(session, body.explanation, request.app.state.provider_factory)
        return session.view


@router.post('/sessions/{session_id}/patch', response_model=SessionView)
async def patch(request: Request, session_id: str):
    session = get_session(request, session_id)
    async with session.lock:
        session.check()
        service.apply(session)
        return session.view


@router.post('/sessions/{session_id}/validation', response_model=SessionView)
async def validation(request: Request, session_id: str, body: RunRequest):
    session = get_session(request, session_id)
    async with session.lock:
        session.check()
        await service.validate(session, body.runner)
        return session.view


@router.get('/sessions/{session_id}/report')
async def report(request: Request, session_id: str):
    session = get_session(request, session_id)
    async with session.lock:
        session.check()
        if not session.original_unchanged():
            session.readiness = 'BLOCKED'
            session.view.validation.original_unchanged = False
        return {'project': session.view.name, 'phase': session.view.phase,
            'readiness': session.readiness, 'validation': session.view.validation.model_dump(),
            'activity': session.view.activity,
            'notice': 'Test evidence from a filtered snapshot, not production certification.'}
