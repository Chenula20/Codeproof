"""Ephemeral connected-project sessions using the stable Guardian and AI contracts."""
import asyncio
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path

from fastapi import HTTPException
from backend.config import provider_settings
from ai.models import ChallengeContext, HintRequest, ExplanationEvaluationRequest, PatchRequest
from ai.services import ProjectAnalyzer, HintEngine, ExplanationEvaluator, PatchGenerator
from workspace import WorkspaceGuardian
from workspace.models import ProjectSnapshot
from backend.session_models import SessionView, Skill, Evaluation, PatchView, Validation
from .guardian import capture, hashes, open_guardian
from .diff import apply_diff
from . import patch_lab, sandbox, release_readiness, incidents


@asynccontextmanager
async def configured_provider():
    from ai.providers import AIProviderConfig, OpenRouterProvider
    try:
        key, model = provider_settings()
    except ValueError as exc:
        raise HTTPException(503, str(exc)) from None
    provider = OpenRouterProvider(AIProviderConfig(api_key=key, model=model, timeout=60))
    try:
        yield provider
    finally:
        await provider.close()


@dataclass
class Session:
    guardian: WorkspaceGuardian
    snapshot: ProjectSnapshot
    original_hashes: dict[str, str]
    copy: str
    view: SessionView
    created: float = field(default_factory=time.monotonic)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    use_ai: bool = False
    closed: bool = False
    readiness: str = 'BLOCKED'

    def check(self):
        if self.closed:
            raise HTTPException(404, 'Session is closed')
        patch_lab.copy_files(self.copy)

    def original_unchanged(self):
        return hashes(self.guardian) == self.original_hashes

    def close(self):
        patch_lab.cleanup_temporary_copy(self.copy)
        self.closed = True

    def context(self):
        view = self.view
        return ChallengeContext(challenge_id=view.id, title=view.challenge_title,
            description=view.challenge_description, difficulty='medium', target_skill='Debugging',
            problem_statement=view.challenge_description, relevant_files=view.relevant_files,
            relevant_code_excerpts=[view.files[p] for p in view.relevant_files],
            expected_concepts=list(incidents.INCIDENTS[view.active_incident.id].concepts) if view.active_incident else ['Explain the root cause, affected code, and a testable correction.'],
            project_summary=view.summary)


def open_session(path: str) -> Session:
    root = Path(path or patch_lab.get_demo_project_path()).expanduser().resolve()
    if root == Path(root.anchor):
        raise ValueError('Select a project directory, not a drive root')
    guardian = open_guardian(str(root))
    snapshot, original_hashes = capture(guardian)
    if not snapshot.files:
        raise ValueError('No supported non-secret files in snapshot')
    copy = patch_lab.materialize(snapshot)
    try:
        view = SessionView(id=uuid.uuid4().hex, name=root.name, sample=False,
            files=dict(snapshot.files), summary=f'Guardian snapshot: {len(snapshot.files)} filtered text files. Enable AI analysis to investigate.',
            technologies=[], issues=[], skills=[], supported_incidents=incidents.supported(snapshot.files, original_hashes), activity=['Opened a redacted Guardian snapshot.'])
        return Session(guardian, snapshot, original_hashes, copy, view)
    except Exception:
        patch_lab.cleanup_temporary_copy(copy)
        raise


async def analyze(session, use_ai, provider_factory):
    if session.view.phase != 'analyzed':
        raise HTTPException(409, 'Analyze before starting an investigation')
    if use_ai:
        async with provider_factory() as provider:
            engine = ProjectAnalyzer(provider)
            analysis = await engine.analyze(session.snapshot.model_copy(deep=True))
            skills = await engine.map_skills(session.snapshot.model_copy(deep=True))
        session.view.summary = analysis.summary
        session.view.technologies = analysis.technologies
        session.view.issues = analysis.issues
        session.view.skills = [Skill(**s.model_dump()) for s in skills.skill_estimates]
        session.view.provider = 'AI provider'
        session.use_ai = True
        session.view.activity.append('AI analyzed the redacted snapshot.')


def challenge(session, issue, target, incident_id=None):
    if session.view.phase != 'analyzed' or not session.use_ai:
        raise HTTPException(409, 'Enable AI analysis before project investigation')
    view = session.view
    if incident_id is not None:
        session.check()
        if not session.original_unchanged():
            raise ValueError('Original changed externally; reopen the session')
        current = patch_lab.copy_files(session.copy)
        if current != session.snapshot.files:
            raise ValueError('Temporary copy differs from the analyzed snapshot')
        incident, files = incidents.inject(current, session.original_hashes, incident_id)
        updated = session.snapshot.model_copy(deep=True)
        updated.files = files
        new_copy = patch_lab.materialize(updated)
        try:
            if patch_lab.copy_files(new_copy) != files:
                raise ValueError('Controlled incident copy verification failed')
            patch_lab.cleanup_temporary_copy(session.copy)
        except Exception:
            patch_lab.cleanup_temporary_copy(new_copy)
            raise
        session.copy, session.snapshot = new_copy, updated
        view.files = dict(files)
        view.active_incident = incident.view()
        view.supported_incidents = []
        view.challenge_title = incident.title
        view.challenge_description = incident.description
        view.relevant_files = [incident.target_file]
        view.activity.append('Controlled incident introduced only in a registered temporary copy.')
    else:
        if not issue.strip() or target not in session.snapshot.files:
            raise ValueError('Describe the issue and select a snapshot file')
        view.challenge_title = 'Project investigation'
        view.challenge_description = issue
        view.relevant_files = [target]
    view.phase = 'investigating'


async def hint(session, provider_factory):
    view = session.view
    if view.phase != 'investigating' or len(view.hints) >= 4:
        raise HTTPException(409, 'No further hints available')
    level = len(view.hints) + 1
    async with provider_factory() as provider:
        result = await HintEngine(provider).generate_hint(HintRequest(challenge_id=view.id,
            hint_level=level, developer_progress='Investigating snapshot evidence', challenge_context=session.context()))
    if result.hint_level != level:
        raise ValueError('Provider returned the wrong hint level')
    view.hints.append(result.hint_content)


async def explain(session, explanation, provider_factory):
    view = session.view
    if view.phase not in ('investigating', 'review'):
        raise HTTPException(409, 'Start an investigation first')
    # A new attempt revokes old approval even if the provider or patch fails.
    view.evaluation = None
    view.patch = None
    view.phase = 'investigating'
    session.readiness = 'BLOCKED'
    context = session.context()
    async with provider_factory() as provider:
        result = await ExplanationEvaluator(provider).evaluate(ExplanationEvaluationRequest(
            challenge_context=context, developer_explanation=explanation,
            expected_concepts=context.expected_concepts))
        proposed = None
        if result.passed:
            proposal = await PatchGenerator(provider).generate_patch(PatchRequest(
                issue_description=view.challenge_description,
                project_snapshot=session.snapshot.model_copy(deep=True), target_files=view.relevant_files))
            apply_diff(view.files, proposal.diff, set(view.relevant_files))
            proposed = PatchView(**proposal.model_dump())
    view.evaluation = Evaluation(classification=result.classification, passed=result.passed,
                                 feedback=result.feedback, score=result.score)
    view.patch = proposed
    view.phase = 'review' if result.passed else 'investigating'


def apply(session):
    view = session.view
    if (view.phase != 'review' or not view.patch or not view.evaluation
            or not view.evaluation.passed or view.evaluation.classification != 'CORRECT'
            or view.evaluation.score < 0.7):
        raise HTTPException(409, 'A passed explanation and reviewed patch are required')
    ok, message = patch_lab.apply_patch(session.copy, view.patch.diff, set(view.relevant_files))
    if not ok:
        raise ValueError(message)
    view.files = patch_lab.copy_files(session.copy)
    view.phase = 'applied'
    view.validation = Validation()
    session.readiness = 'BLOCKED'
    view.activity.append('Patch applied only to the disposable copy.')


async def validate(session, runner):
    result = await asyncio.to_thread(sandbox.run_managed_copy, session.copy, runner)
    unchanged = session.original_unchanged()
    ready = release_readiness.evaluate_release_readiness(result)
    status = result.status if result.status in {'passed', 'failed', 'error', 'timeout', 'unavailable'} else 'error'
    checks = ['Docker execution only', 'Guardian snapshot integrity checked']
    if not unchanged:
        checks.append('Original changed externally; reopen the session.')
    session.view.validation = Validation(status=status, test_counts=result.test_counts, simulated=False,
        output=result.output or '\n'.join(result.runtime_errors), duration_ms=result.duration_ms,
        original_unchanged=unchanged, checks=checks)
    if session.view.phase in ('applied', 'validated'):
        session.readiness = ready.status if unchanged else 'BLOCKED'
        session.view.phase = 'validated' if session.readiness == 'READY' else 'applied'
    session.view.activity.append(f'Docker validation: {status}.')
