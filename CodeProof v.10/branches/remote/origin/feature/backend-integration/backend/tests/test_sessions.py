"""Exercise real Guardian/AI services; mock only external provider and Docker transports."""
import ast
import hashlib
import json
import re
import socket
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import MagicMock

import httpx
import pytest
import uvicorn
from fastapi.testclient import TestClient

from ai.providers import AIProviderConfig, OpenRouterProvider
from backend.main import create_app
from backend.session_models import SessionView
from backend.services import patch_lab

TOKEN = 'test-pairing-token-not-a-secret-123456789'
PATCH = '--- a/main.py\n+++ b/main.py\n@@ -1 +1 @@\n-value = 1\n+value = 2\n'


class ProviderTransport:
    def __init__(self):
        self.calls = []
        self.score = .95
        self.fail = False

    def __call__(self, request):
        if self.fail:
            return httpx.Response(500, text='private-provider-error-and-key')
        body = json.loads(request.content)
        prompt = body['messages'][-1]['content']
        schema = ast.literal_eval(prompt.split('Respond with valid JSON matching this schema:\n')[-1])
        title = schema['title']
        self.calls.append((title, prompt))
        response = {
            'ProjectAnalysis': {'project_id': 'test', 'summary': 'Observed value issue',
                'technologies': ['Python'], 'issues': ['Wrong value'], 'skills': ['Debugging']},
            'EngineeringSkillMap': {'project_id': 'test', 'skill_estimates': [
                {'category': 'Debugging', 'relevance': .8, 'confidence': .9, 'evidence': ['main.py']}]},
            'ExplanationEvaluation': {'user_explanation': 'The value is wrong', 'classification': 'CORRECT',
                'score': self.score, 'feedback': 'Review the value assignment.', 'passed': True},
            'Patch': {'patch_id': 'test', 'description': 'Correct the value assignment.', 'diff': PATCH,
                'affected_files': ['main.py'], 'risk_level': 'low', 'validation_warnings': []},
        }
        if title == 'HintResponse':
            level = int(re.search(r'HINT LEVEL: (\d)', prompt).group(1))
            data = {'hint_level': level, 'hint_content': f'Inspect the value, level {level}', 'next_level_available': level < 4}
        else:
            data = response[title]
        return httpx.Response(200, json={'choices': [{'message': {'content': json.dumps(data)}}]})

    @asynccontextmanager
    async def factory(self):
        provider = OpenRouterProvider(AIProviderConfig(api_key='test-transport-only', model='test'))
        await provider.client.aclose()
        provider.client = httpx.AsyncClient(transport=httpx.MockTransport(self))
        try:
            yield provider
        finally:
            await provider.close()


@pytest.fixture
def project(tmp_path):
    root = tmp_path / 'source'
    root.mkdir()
    (root / 'main.py').write_text('value = 1\n')
    (root / 'test_value.py').write_text('def test_value(): assert True\n')
    (root / '.env').write_text('password=private-password')
    (root / 'config.py').write_text('api_key = "abcdefghijklmnopqrstuvwxyz123456"\n')
    return root


@pytest.fixture(params=['testclient', 'tcp'])
def live(request):
    transport = ProviderTransport()
    app = create_app(TOKEN, transport.factory)
    if request.param == 'testclient':
        with TestClient(app, raise_server_exceptions=False, headers={'Authorization': 'Bearer ' + TOKEN}) as client:
            yield client, app, transport
    else:
        sock = socket.socket()
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(app, log_level='error'))
        thread = threading.Thread(target=server.run, kwargs={'sockets': [sock]}, daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 10
            while not server.started and time.monotonic() < deadline and thread.is_alive():
                time.sleep(.02)
            assert server.started, 'Uvicorn failed to start'
            with httpx.Client(base_url=f'http://127.0.0.1:{port}', trust_env=False,
                              headers={'Authorization': 'Bearer ' + TOKEN}, timeout=15) as client:
                yield client, app, transport
        finally:
            server.should_exit = True
            thread.join(timeout=10)
            sock.close()
            assert not thread.is_alive(), 'Uvicorn did not shut down'
    assert not app.state.sessions


def fingerprint(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def post(client, path, payload=None, expected=200):
    response = client.post(path, json=payload or {})
    assert response.status_code == expected, response.text
    if expected == 200:
        SessionView.model_validate(response.json())
    return response.json()


def test_complete_http_flow(live, project, monkeypatch):
    import docker
    client, app, transport = live
    docker_client = MagicMock()
    container = docker_client.containers.create.return_value
    container.wait.return_value = {'StatusCode': 0}
    container.logs.side_effect = lambda **kw: iter([b'1 passed in 0.01s\n'])
    monkeypatch.setattr(docker, 'from_env', lambda **kw: docker_client)
    before = fingerprint(project)
    assert client.get('/health').status_code == 200
    opened = post(client, '/v1/sessions', {'path': str(project)})
    base = '/v1/sessions/' + opened['id']
    copy = Path(app.state.sessions[opened['id']].copy)
    assert '.env' not in opened['files']
    assert 'abcdefghijklmnopqrstuvwxyz123456' not in str(opened)
    assert not transport.calls
    post(client, base + '/challenge', {'issue': 'Wrong value', 'target_file': 'main.py'}, 409)
    analysis = post(client, base + '/analysis', {'use_ai': True})
    assert analysis['skills'][0]['category'] == 'Debugging'
    post(client, base + '/challenge', {'issue': 'Wrong value', 'target_file': 'main.py'})
    for level in range(1, 5):
        hinted = post(client, base + '/hint')
        assert len(hinted['hints']) == level
    post(client, base + '/hint', expected=409)
    transport.score = .2
    rejected = post(client, base + '/explanation', {'explanation': 'The value is wrong; inspect its assignment.'})
    assert rejected['evaluation']['passed'] is False and rejected['patch'] is None
    post(client, base + '/patch', expected=409)
    transport.score = .95
    accepted = post(client, base + '/explanation', {'explanation': 'The value should be two; correct the assignment.'})
    assert accepted['phase'] == 'review' and accepted['patch']['diff'] == PATCH
    applied = post(client, base + '/patch')
    assert applied['files']['main.py'] == 'value = 2\n'
    assert (copy / 'main.py').read_text() == 'value = 2\n'
    validated = post(client, base + '/validation', {'runner': 'python-pytest'})
    assert validated['phase'] == 'validated'
    assert validated['validation']['original_unchanged'] is True
    assert client.get(base + '/report').json()['readiness'] == 'READY'
    assert fingerprint(project) == before
    expected_models = {'ProjectAnalysis', 'EngineeringSkillMap', 'HintResponse', 'ExplanationEvaluation', 'Patch'}
    assert {title for title, _ in transport.calls} == expected_models
    assert all(str(project) not in prompt and 'abcdefghijklmnopqrstuvwxyz123456' not in prompt for _, prompt in transport.calls)
    # A later external edit invalidates readiness; the backend did not make it.
    (project / 'main.py').write_text('value = 99\n')
    assert client.get(base + '/report').json()['readiness'] == 'BLOCKED'
    assert client.delete(base).json() == {'closed': True}
    assert not copy.exists()
    assert client.get(base + '/report').status_code == 404


def test_provider_failure_preserves_state_and_hides_details(live, project):
    client, app, transport = live
    opened = post(client, '/v1/sessions', {'path': str(project)})
    transport.fail = True
    response = client.post('/v1/sessions/' + opened['id'] + '/analysis', json={'use_ai': True})
    assert response.status_code == 500
    assert 'private-provider' not in response.text
    assert not app.state.sessions[opened['id']].use_ai


def test_auth_origin_and_validation(project):
    app = create_app(TOKEN)
    with TestClient(app) as client:
        assert client.post('/v1/sessions', json={'path': str(project)}).status_code == 401
        headers = {'Authorization': 'Bearer ' + TOKEN}
        assert client.post('/v1/sessions', json={}, headers={**headers, 'Origin': 'https://example.com'}).status_code == 403
        assert client.post('/v1/sessions', json={'path': 4}, headers=headers).status_code == 422
        assert client.post('/v1/sessions', json={}, headers={**headers, 'Host': 'evil.example'}).status_code == 400


def test_no_configured_ai_is_explicit(project, monkeypatch):
    monkeypatch.delenv('OPENROUTER_API_KEY', raising=False)
    monkeypatch.delenv('CODEPROOF_MODEL', raising=False)
    with TestClient(create_app(TOKEN), headers={'Authorization': 'Bearer ' + TOKEN}) as client:
        opened = post(client, '/v1/sessions', {'path': str(project)})
        post(client, '/v1/sessions/' + opened['id'] + '/analysis', {'use_ai': True}, 503)


def test_session_limit_and_shutdown_cleanup(project):
    app = create_app(TOKEN)
    with TestClient(app, headers={'Authorization': 'Bearer ' + TOKEN}) as client:
        for _ in range(8):
            post(client, '/v1/sessions', {'path': str(project)})
        post(client, '/v1/sessions', {'path': str(project)}, 409)
        paths = [Path(s.copy) for s in app.state.sessions.values()]
    assert all(not path.exists() for path in paths)
    assert not patch_lab._copies
