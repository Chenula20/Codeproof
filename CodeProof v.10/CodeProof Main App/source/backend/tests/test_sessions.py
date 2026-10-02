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
        self.payloads = []
        self.score = .95
        self.fail = False
        self.evaluation_payload = None
        self.evaluation_raw = None
        self.patch_raw = None

    def __call__(self, request):
        if self.fail:
            return httpx.Response(500, text='private-provider-error-and-key')
        body = json.loads(request.content)
        self.payloads.append(body)
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
        if title == 'ExplanationEvaluation' and self.evaluation_payload is not None:
            data = self.evaluation_payload
        content = self.evaluation_raw if title == 'ExplanationEvaluation' and self.evaluation_raw is not None else json.dumps(data)
        if title == 'Patch' and self.patch_raw is not None:
            content = self.patch_raw
        return httpx.Response(200, json={'choices': [{'message': {'content': content}}]})

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
    (root / 'auth.py').write_text('SECRET_KEY = "signing-fixture!short"\nALGORITHM = "HS256"\n')
    (root / 'package.json').write_text(json.dumps({
        "name": "public-fixture", "version": "1.0.0",
        "signingKey": "config-signing-fixture!", "dependencies": {"public-package": "1.0"}
    }))
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
                              headers={'Authorization': 'Bearer ' + TOKEN}, timeout=15,
                              limits=httpx.Limits(max_keepalive_connections=0)) as client:
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
    assert 'signing-fixture!short' not in json.dumps(opened)
    assert 'config-signing-fixture!' not in json.dumps(opened)
    assert 'HS256' in opened['files']['auth.py']
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
    # Intercepted real OpenRouter HTTP payloads across all AI services must be sanitized.
    for payload in transport.payloads:
        prompt = json.dumps(payload)
        assert 'signing-fixture!short' not in prompt
        assert 'config-signing-fixture!' not in prompt
    assert any('HS256' in prompt for _, prompt in transport.calls)
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


@pytest.mark.parametrize('classification', ['CORRECT', 'PARTIALLY_CORRECT', 'INCORRECT'])
@pytest.mark.parametrize('score', [.69, .7, .95])
def test_three_way_provider_gate(live, project, classification, score):
    client, app, transport = live
    before = fingerprint(project)
    opened = post(client, '/v1/sessions', {'path': str(project)})
    base = '/v1/sessions/' + opened['id']
    try:
        post(client, base + '/explanation', {'explanation': 'An explanation before investigation.'}, 409)
        post(client, base + '/patch', expected=409)
        post(client, base + '/analysis', {'use_ai': True})
        post(client, base + '/challenge', {'issue': 'Wrong value', 'target_file': 'main.py'})
        transport.evaluation_payload = {'user_explanation': 'Safe fixture explanation',
            'classification': classification, 'score': score, 'feedback': 'Deterministic provider fixture.',
            'passed': classification != 'CORRECT'}  # Deliberately contradict the provider flag.
        patch_calls = sum(title == 'Patch' for title, _ in transport.calls)
        view = post(client, base + '/explanation', {'explanation': 'The assignment has the wrong value.'})
        expected = classification == 'CORRECT' and score >= .7
        assert view['evaluation'] == {'classification': classification, 'score': score,
            'feedback': 'Deterministic provider fixture.', 'passed': expected}
        assert (view['patch'] is not None) == expected
        assert view['phase'] == ('review' if expected else 'investigating')
        assert sum(title == 'Patch' for title, _ in transport.calls) - patch_calls == int(expected)
        post(client, base + '/patch', expected=200 if expected else 409)
        assert fingerprint(project) == before
    finally:
        client.delete(base)


@pytest.mark.parametrize('bad', ['partial', 'incorrect', 'enum', 'missing', 'string_score',
    'bool_score', 'nan', 'inf', 'range', 'blank_feedback', 'missing_feedback', 'passed_string', 'json', 'transport_error', 'patch_error', 'missing_score', 'negative', 'missing_passed'])
def test_reevaluation_revokes_old_approval(live, project, bad):
    client, app, transport = live
    before = fingerprint(project)
    opened = post(client, '/v1/sessions', {'path': str(project)})
    base = '/v1/sessions/' + opened['id']
    try:
        post(client, base + '/analysis', {'use_ai': True})
        post(client, base + '/challenge', {'issue': 'Wrong value', 'target_file': 'main.py'})
        post(client, base + '/explanation', {'explanation': 'The assignment has the wrong value.'})
        data = {'user_explanation': 'Safe fixture explanation', 'classification': 'CORRECT',
            'score': .95, 'feedback': 'Safe provider feedback.', 'passed': True}
        if bad == 'partial': data['classification'] = 'PARTIALLY_CORRECT'
        elif bad == 'incorrect': data['classification'] = 'INCORRECT'
        elif bad == 'enum': data['classification'] = 'MAYBE'
        elif bad == 'missing': del data['classification']
        elif bad == 'string_score': data['score'] = '0.95'
        elif bad == 'bool_score': data['score'] = True
        elif bad == 'nan': data['score'] = float('nan')
        elif bad == 'inf': data['score'] = float('inf')
        elif bad == 'range': data['score'] = 1.1
        elif bad == 'negative': data['score'] = -.1
        elif bad == 'missing_score': del data['score']
        elif bad == 'missing_passed': del data['passed']
        elif bad == 'patch_error': transport.patch_raw = '{bad-patch'
        elif bad == 'blank_feedback': data['feedback'] = '  '
        elif bad == 'missing_feedback': del data['feedback']
        elif bad == 'passed_string': data['passed'] = 'true'
        elif bad == 'json': transport.evaluation_raw = '{not-json'
        transport.evaluation_payload = data
        if bad == 'transport_error':
            transport.fail = True  # Provider transport failure also revokes prior approval.
        response = client.post(base + '/explanation', json={'explanation': 'A new attempt must replace prior approval.'})
        assert response.status_code == (200 if bad in ('partial', 'incorrect') else 500)
        if response.status_code == 500:
            assert response.json() == {'detail': 'Operation failed; check local service configuration.'}
        session = app.state.sessions[opened['id']]
        assert session.view.phase == 'investigating'
        assert session.view.patch is None
        assert session.view.evaluation is None or not session.view.evaluation.passed
        post(client, base + '/patch', expected=409)
        assert fingerprint(project) == before
    finally:
        client.delete(base)

@pytest.mark.parametrize('classification,score', [('PARTIALLY_CORRECT', .95), ('INCORRECT', .95), ('CORRECT', .69)])
def test_apply_rechecks_classification_and_score(live, project, classification, score):
    client, app, transport = live
    opened = post(client, '/v1/sessions', {'path': str(project)})
    base = '/v1/sessions/' + opened['id']
    before = fingerprint(project)
    try:
        post(client, base + '/analysis', {'use_ai': True})
        post(client, base + '/challenge', {'issue': 'Wrong value', 'target_file': 'main.py'})
        post(client, base + '/explanation', {'explanation': 'The assignment has the wrong value.'})
        evaluation = app.state.sessions[opened['id']].view.evaluation
        evaluation.classification = classification
        evaluation.score = score
        evaluation.passed = True  # Simulate contradictory stored authorization.
        post(client, base + '/patch', expected=409)
        assert fingerprint(project) == before
    finally:
        client.delete(base)

@pytest.mark.parametrize('status,counts', [
    ('passed', {'total':2,'passed':2,'failed':0,'skipped':0}),
    ('failed', {'total':2,'passed':1,'failed':1,'skipped':0}),
    ('passed', {'total':2,'passed':1,'failed':0,'skipped':1}),
    ('failed', {'total':0,'passed':0,'failed':0,'skipped':0}),
    ('unavailable', None), ('timeout', None), ('error', None), ('passed', None),
])
def test_connected_count_propagation_and_readiness(live, project, monkeypatch, status, counts):
    from backend.models import SandboxResult
    from backend.services import sandbox
    client, app, transport = live
    opened = post(client, '/v1/sessions', {'path':str(project)})
    base='/v1/sessions/'+opened['id']
    before=fingerprint(project)
    try:
        post(client,base+'/analysis',{'use_ai':True})
        post(client,base+'/challenge',{'issue':'Wrong value','target_file':'main.py'})
        post(client,base+'/explanation',{'explanation':'The assignment has the wrong value.'})
        post(client,base+'/patch')
        result=SandboxResult(status=status,test_counts=counts,output='Synthetic sandbox transport fixture.')
        monkeypatch.setattr(sandbox,'run_managed_copy',lambda *args:result)
        view=post(client,base+'/validation',{'runner':'python-pytest'})
        assert view['validation']['test_counts']==counts
        assert view['validation']['simulated'] is False
        assert view['validation']['status']==status
        report=client.get(base+'/report').json()
        expected='READY' if status=='passed' and counts and counts['passed']==counts['total'] and counts['total']>0 else 'BLOCKED'
        assert report['readiness']==expected
        assert report['validation']['test_counts']==counts
        # Replace prior result with unknown/unavailable; stale validated phase must not win.
        monkeypatch.setattr(sandbox,'run_managed_copy',lambda *args:SandboxResult(status='unavailable'))
        changed=post(client,base+'/validation',{'runner':'python-pytest'})
        assert changed['phase']=='applied'
        assert changed['validation']['test_counts'] is None
        assert client.get(base+'/report').json()['readiness']=='BLOCKED'
        assert fingerprint(project)==before
    finally:
        client.delete(base)


def test_credential_literals_never_reach_provider_and_snapshot_code_parses(live,project):
    client,app,transport=live
    literals=['credential-context-fixture','api-context-fixture']
    (project/'user_fixture.py').write_text('hashed_password = get_password_hash("credential-context-fixture")\nPUBLIC = 42\n')
    (project/'settings.json').write_text('{"api_key":"api-context-fixture","public":42}')
    before=fingerprint(project)
    view=client.post('/v1/sessions',json={'path':str(project)}).json();sid=view['id'];url='/v1/sessions/'+sid
    ast.parse(view['files']['user_fixture.py'])
    assert 'get_password_hash(' in view['files']['user_fixture.py']
    assert client.post(url+'/analysis',json={'use_ai':True}).status_code==200
    assert client.post(url+'/challenge',json={'issue':'Wrong value in main.py','target_file':'main.py'}).status_code==200
    for _ in range(4):assert client.post(url+'/hint').status_code==200
    assert client.post(url+'/explanation',json={'explanation':'The value assignment is wrong and must change from one to two.'}).status_code==200
    serialized=json.dumps(transport.payloads)
    assert all(value not in serialized for value in literals)
    assert fingerprint(project)==before
    assert client.delete(url).status_code==200
