"""Deterministic demo fixtures for the CodeProof browser workspace.

Everything here is in-memory practice data for the unversioned demo routes:
no disk writes, no AI calls, no Docker. The original project on disk is only
ever read (via the demo dataset below), never modified.
"""

import threading
from dataclasses import dataclass, field

from backend.demo_models import (
    ChallengeStartResponse,
    DemoReadinessResponse,
    DemoStateResponse,
    FileContentResponse,
    FileNode,
    FileTreeResponse,
    HintResponse,
    OverviewResponse,
    PatchApplyResponse,
    PatchProposalResponse,
    ReadinessCheck,
    SimulatedTest,
    SkillEntry,
    SkillMapResponse,
    ValidationResponse,
)

# ── Project dataset ──────────────────────────────────────────────────

LOGIN_JS_FIXED = """export async function login(username, password) {
  const response = await fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: username, password })
  });
  if (!response.ok) throw new Error('Login request failed');
  return response.json();
}
"""

LOGIN_JS_CHALLENGE = LOGIN_JS_FIXED.replace(
    "JSON.stringify({ username: username, password })",
    "JSON.stringify({ email: username, password })",
)

HANDLER_PY = """@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing credentials'}), 422

    user = User.query.filter_by(username=username).first()
    if not user or not verify_password(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = generate_token(user.id)
    return jsonify({'token': token, 'user': user.to_dict()})
"""

EVENTS_PY = """from flask import jsonify

from src.database.repository import list_events


@app.route('/api/events', methods=['GET'])
def events():
    return jsonify([event.to_dict() for event in list_events()])
"""

REPOSITORY_PY = """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///events.db')
Session = sessionmaker(bind=engine)


def list_events():
    session = Session()
    try:
        return session.query(Event).order_by(Event.date).all()
    finally:
        session.close()
"""

TEST_AUTH_PY = """import pytest


def test_valid_credentials_accepted(client):
    response = client.post('/api/login', json={'username': 'ada', 'password': 'correct'})
    assert response.status_code == 200
    assert 'token' in response.get_json()


def test_invalid_credentials_rejected(client):
    response = client.post('/api/login', json={'username': 'ada', 'password': 'wrong'})
    assert response.status_code == 401


def test_missing_credentials_return_422(client):
    response = client.post('/api/login', json={})
    assert response.status_code == 422
"""

README_MD = """# Student Event Management System

A small web application for student events.

## Structure

- `src/api/events.py` - Flask routes for event listings
- `src/auth/handler.py` - login route and credential validation
- `src/database/repository.py` - SQLAlchemy storage for events
- `src/frontend/login.js` - browser login client
- `tests/test_auth.py` - authentication and regression tests
"""

ORIGINAL_FILES: dict[str, str] = {
    'README.md': README_MD,
    'src/api/events.py': EVENTS_PY,
    'src/auth/handler.py': HANDLER_PY,
    'src/database/repository.py': REPOSITORY_PY,
    'src/frontend/login.js': LOGIN_JS_FIXED,
    'tests/test_auth.py': TEST_AUTH_PY,
}

CHALLENGE_FILES: dict[str, str] = {
    **ORIGINAL_FILES,
    'src/frontend/login.js': LOGIN_JS_CHALLENGE,
}

ERROR_OUTPUT = """[demo] POST /api/login \u2192 HTTP 422 / validation error
Login request failed
Response: Missing credentials
Password values are omitted from these demo logs.
"""

PATCH_DIFF = """--- a/src/frontend/login.js
+++ b/src/frontend/login.js
@@ -2,6 +2,6 @@
     const response = await fetch('/api/login', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
-      body: JSON.stringify({ email: username, password })
+      body: JSON.stringify({ username: username, password })
     });
"""

HINTS: list[tuple[str, str]] = [
    ('Direction', 'Trace the data crossing the login boundary. Is this a validation failure or a password-check failure?'),
    ('Component', 'Compare the browser login request with the authentication route that receives it.'),
    ('Mechanism', "The handler reads data.get('username') and rejects the request when it is missing. Which key does the client actually send?"),
    ('Fix', 'Send the credentials under the username key so the handler validation receives them.'),
]

# Keywords of the expected root cause for deterministic explanation scoring.
EXPECTED_KEYWORDS = ['email', 'username', 'key', 'handler', 'missing', 'credentials', '422']

SIMULATED_TESTS: list[tuple[str, str, int]] = [
    ('Authentication test', 'Valid username and password accepted.', 245),
    ('Login API test', 'Invalid credentials rejected; missing fields return 422.', 180),
    ('Existing regression tests', 'Event routes and existing login cases remain unchanged.', 1200),
]

READINESS_NOTE = ('Simulated demo results \u2014 nothing was executed on disk. Readiness is '
                  'evidence for review, not a guarantee of production readiness.')


# ── Demo session state ───────────────────────────────────────────────

@dataclass
class DemoState:
    challenge_started: bool = False
    hints_revealed: int = 0
    patch_unlocked: bool = False
    patch_applied: bool = False
    validated: bool = False
    validation_passed: bool = False


_lock = threading.Lock()
_state = DemoState()


def reset() -> None:
    with _lock:
        _state.challenge_started = False
        _state.hints_revealed = 0
        _state.patch_unlocked = False
        _state.patch_applied = False
        _state.validated = False
        _state.validation_passed = False


def get_state() -> DemoStateResponse:
    with _lock:
        return DemoStateResponse(
            challenge_started=_state.challenge_started,
            hints_revealed=_state.hints_revealed,
            patch_unlocked=_state.patch_unlocked,
            patch_applied=_state.patch_applied,
            validated=_state.validated,
            validation_passed=_state.validation_passed,
        )


# ── Overview and skill map ───────────────────────────────────────────

def get_overview() -> OverviewResponse:
    return OverviewResponse(
        name='Student Event Management System',
        tagline='A small web application for student events.',
        description=('A small web application for student events. A browser client calls Flask '
                     'routes; authentication guards requests, and a SQLAlchemy repository stores events.'),
        technologies=['Python', 'Flask', 'SQLAlchemy', 'JavaScript', 'JWT', 'Pytest'],
        review_focus='Request validation, authentication behavior, and regression coverage.',
    )


def get_skill_map() -> SkillMapResponse:
    return SkillMapResponse(skills=[
        SkillEntry(key='debugging', label='Debugging', relevance=90, confidence=85,
                   evidence=['src/auth/handler.py', 'tests/test_auth.py']),
        SkillEntry(key='api', label='API', relevance=80, confidence=80,
                   evidence=['src/api/events.py']),
        SkillEntry(key='database', label='Database', relevance=75, confidence=70,
                   evidence=['src/database/repository.py']),
        SkillEntry(key='authentication', label='Authentication', relevance=95, confidence=90,
                   evidence=['src/auth/handler.py', 'src/frontend/login.js']),
        SkillEntry(key='testing', label='Testing', relevance=68, confidence=62,
                   evidence=['tests/test_auth.py']),
        SkillEntry(key='error_handling', label='Error Handling', relevance=72, confidence=66,
                   evidence=['src/auth/handler.py']),
    ])


# ── Files ────────────────────────────────────────────────────────────

def _tree(files: dict[str, str], source: str) -> FileTreeResponse:
    nodes: dict[str, FileNode] = {}
    for path in files:
        parts = path.split('/')
        for i in range(1, len(parts)):
            directory = '/'.join(parts[:i])
            nodes.setdefault(directory, FileNode(path=directory, name=parts[i - 1], kind='dir'))
        nodes[path] = FileNode(path=path, name=parts[-1], kind='file')
    return FileTreeResponse(source=source, nodes=sorted(nodes.values(), key=lambda n: (n.path.count('/'), n.path)))


def get_file_tree(source: str) -> FileTreeResponse:
    files = CHALLENGE_FILES if source == 'challenge' else ORIGINAL_FILES
    return _tree(files, source)


def get_file_content(path: str, source: str) -> FileContentResponse | None:
    files = CHALLENGE_FILES if source == 'challenge' else ORIGINAL_FILES
    if path not in files:
        return None
    highlights = []
    if source == 'challenge' and path == 'src/frontend/login.js':
        highlights = [5]
    return FileContentResponse(path=path, source=source, content=files[path], highlights=highlights)


# ── Challenge flow ───────────────────────────────────────────────────

def start_challenge() -> ChallengeStartResponse:
    with _lock:
        _state.challenge_started = True
    return ChallengeStartResponse(
        id='auth-422',
        title='Authentication Failure',
        difficulty='Beginner / Intermediate',
        skill='Authentication',
        description=('Valid users cannot sign in. The login endpoint responds with HTTP 422 before '
                     'authentication completes. Trace the request and explain the root cause.'),
        investigation_files=['src/frontend/login.js', 'src/auth/handler.py'],
        error_output=ERROR_OUTPUT,
    )


def get_hint(level: int) -> HintResponse:
    with _lock:
        if not _state.challenge_started:
            raise ValueError('Start a challenge before requesting hints.')
        index = max(1, min(level, len(HINTS))) - 1
        if level > _state.hints_revealed:
            _state.hints_revealed = index + 1
        title, text = HINTS[index]
        return HintResponse(level=index + 1, total=len(HINTS), title=title, hint=text)


def evaluate_explanation(explanation: str) -> tuple[str, str, bool]:
    with _lock:
        if not _state.challenge_started:
            raise ValueError('Start a challenge before evaluating an explanation.')
        _state.patch_unlocked = False
        text = explanation.lower()
        matches = sum(1 for keyword in EXPECTED_KEYWORDS if keyword in text)
        ratio = matches / len(EXPECTED_KEYWORDS)
        if ratio >= 0.6:
            classification = 'CORRECT'
            feedback = ('You traced the contract mismatch: the client sends the credential under '
                        '"email" while the handler reads "username", so validation fails with 422 '
                        'before any password check. A patch proposal is ready for review.')
            _state.patch_unlocked = True
        elif ratio >= 0.3:
            classification = 'PARTIALLY_CORRECT'
            feedback = ('You have part of the cause. Pin down which side of the login boundary '
                        'drops the credential, then re-evaluate to unlock the patch.')
        else:
            classification = 'INCORRECT'
            feedback = ('That does not match the evidence. Compare the request body keys in '
                        'login.js with the keys the handler reads before judging the failure.')
        return classification, feedback, _state.patch_unlocked


def get_patch_proposal() -> PatchProposalResponse:
    with _lock:
        if not _state.patch_unlocked:
            raise ValueError('Explain the root cause to unlock the proposed patch.')
    return PatchProposalResponse(
        title='Align the login request credential key with the existing handler contract.',
        affected_file='src/frontend/login.js',
        risk='LOW',
        notes=[
            'Demo proposal only. No disk files will be changed.',
            'Verify valid, invalid and missing credentials against the real API before adoption.',
        ],
        diff=PATCH_DIFF,
    )


def apply_patch() -> PatchApplyResponse:
    with _lock:
        if not _state.patch_unlocked:
            raise ValueError('Explain the root cause to unlock the proposed patch.')
        _state.patch_applied = True
        return PatchApplyResponse(
            applied=True,
            file='src/frontend/login.js',
            content=LOGIN_JS_FIXED,
            message='Patch applied to challenge copy: 1 file(s). The original project is unchanged.',
        )


# ── Simulated validation and readiness ───────────────────────────────

def run_validation() -> ValidationResponse:
    with _lock:
        if not _state.patch_applied:
            tests = [SimulatedTest(name=n, detail=d, status='failed', duration_ms=ms)
                     for n, d, ms in SIMULATED_TESTS]
            return ValidationResponse(
                status='failed', simulated=True, tests=tests,
                output=('Starting sandbox ...\nRunning tests ...\n'
                        '[demo] POST /api/login \u2192 HTTP 422 / validation error\n'
                        'Login request failed\nResponse: Missing credentials'),
                duration_ms=1625,
            )
        _state.validated = True
        _state.validation_passed = True
        tests = [SimulatedTest(name=n, detail=d, status='passed', duration_ms=ms)
                 for n, d, ms in SIMULATED_TESTS]
        return ValidationResponse(
            status='passed', simulated=True, tests=tests,
            output=('Starting sandbox ...\nRunning tests ...\n'
                    '3 passed, 0 failed in 1.62s (simulated demo results)'),
            duration_ms=1625,
        )


def get_readiness() -> DemoReadinessResponse:
    with _lock:
        checks = [
            ReadinessCheck(key='challenge_resolved', label='Challenge Resolved', passed=_state.patch_applied),
            ReadinessCheck(key='tests_passed', label='Tests Passed', passed=_state.validation_passed),
            ReadinessCheck(key='security_checks', label='Security Checks Passed', passed=True),
            ReadinessCheck(key='original_unchanged', label='Original Project Unchanged', passed=True),
            ReadinessCheck(key='patch_tested', label='Patch Tested in Temporary Copy',
                           passed=_state.patch_applied and _state.validation_passed),
        ]
        ready = all(check.passed for check in checks)
        return DemoReadinessResponse(
            status='READY_FOR_REVIEW' if ready else 'IN_PROGRESS',
            simulated=True,
            checks=checks,
            note=READINESS_NOTE,
        )
