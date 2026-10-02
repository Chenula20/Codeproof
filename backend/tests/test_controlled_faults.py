"""Public API guarantees for controlled real-project faults and local hints."""
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import create_app
from backend.models import SandboxResult, TestCounts as Counts
from backend.services import patch_lab, sessions

TOKEN = 'controlled-fault-test-pairing-token-1234567890'


@pytest.fixture
def workspace(tmp_path):
    root = tmp_path / 'selected-project'
    root.mkdir()
    (root / 'main.py').write_text('value = 1\n')
    (root / 'test_value.py').write_text('from main import value\ndef test_value(): assert value == 1\n')
    (root / '.env').write_text('SECRET=not-for-the-snapshot\n')
    return root


@pytest.fixture
def connected(workspace):
    app = create_app(TOKEN)
    @asynccontextmanager
    async def forbidden_provider():
        pytest.fail('Local controlled faults and hints must not contact an AI provider')
        yield
    app.state.provider_factory = forbidden_provider
    with TestClient(app, headers={'Authorization': 'Bearer ' + TOKEN}) as client:
        data = client.post('/v1/sessions', json={'path': str(workspace)}).json()
        session = app.state.sessions[data['id']]
        base = '/v1/sessions/' + data['id']
        incident = next(item for item in data['supported_incidents'] if 'python-pytest' in item['title'])
        yield client, session, base, incident
        client.delete(base)


def healthy():
    return SandboxResult(status='passed', test_counts=Counts(total=1, passed=1, failed=0, skipped=0), output='1 passed in 0.01s')


def detected(copy, runner):
    source = patch_lab.copy_files(copy)['main.py']
    return SandboxResult(status='failed', output='main.py\n' + source.splitlines()[-1] + '\nSyntaxError: invalid syntax')


def reproduce(monkeypatch, second=detected):
    calls = []
    def run(copy, runner):
        calls.append((copy, runner))
        return healthy() if len(calls) == 1 else second(copy, runner)
    monkeypatch.setattr(sessions.sandbox, 'run_managed_copy', run)
    return calls


def test_real_copy_fault_four_local_hints_and_cleanup(connected, workspace, monkeypatch):
    client, session, base, incident = connected
    original = {p.name: p.read_bytes() for p in workspace.iterdir()}
    old_copy = session.copy
    calls = reproduce(monkeypatch)
    response = client.post(base + '/challenge', json={'incident_id': incident['id']})
    assert response.status_code == 200, response.text
    data = response.json()
    assert [runner for _, runner in calls] == ['python-pytest', 'python-pytest']
    assert not Path(old_copy).exists()
    assert session.copy != old_copy and Path(session.copy).exists()
    assert '.env' not in data['files']
    assert 'CODEPROOF_FAULT_' in data['files']['main.py']
    assert data['files']['test_value.py'] == session.snapshot.files['test_value.py']
    assert data['sample'] is False and data['validation']['simulated'] is False
    assert data['validation']['status'] == 'failed'
    assert data['validation']['test_counts'] is None  # collection failures have no invented counts
    assert data['active_incident']['id'] == incident['id']
    assert client.get(base + '/report').json()['readiness'] == 'BLOCKED'
    assert client.post(base + '/patch').status_code == 409
    assert client.post(base + '/explanation', json={'explanation': 'The module has invalid syntax.'}).status_code == 409
    for level in range(1, 5):
        response = client.post(base + '/hint')
        assert response.status_code == 200, response.text
        assert len(response.json()['hints']) == level
    hints = response.json()['hints']
    assert 'main.py' in hints[1] and 'line 2' in hints[2]
    assert 'CODEPROOF_FAULT_' in hints[3]
    assert client.post(base + '/hint').status_code == 409
    assert client.post(base + '/challenge', json={'incident_id': incident['id']}).status_code == 409
    assert {p.name: p.read_bytes() for p in workspace.iterdir()} == original
    broken_copy = session.copy
    assert client.delete(base).status_code == 200
    assert not Path(broken_copy).exists()
    assert {p.name: p.read_bytes() for p in workspace.iterdir()} == original


@pytest.mark.parametrize('baseline', [
    SandboxResult(status='unavailable'), SandboxResult(status='timeout'),
    SandboxResult(status='failed'), SandboxResult(status='error'),
    SandboxResult(status='passed'),
    SandboxResult(status='passed', test_counts=Counts(total=0, passed=0, failed=0, skipped=0)),
    SandboxResult(status='passed', test_counts=Counts(total=2, passed=1, failed=0, skipped=1)),
    SandboxResult(status='passed', test_counts=Counts(total=1, passed=1, failed=0, skipped=0), runtime_errors=['Cleanup failed']),
])
def test_baseline_failures_do_not_mutate_session(connected, monkeypatch, baseline):
    client, session, base, incident = connected
    before = patch_lab.copy_files(session.copy)
    old_copy = session.copy
    calls = []
    def run(copy, runner):
        calls.append(copy)
        return baseline
    monkeypatch.setattr(sessions.sandbox, 'run_managed_copy', run)
    result = client.post(base + '/challenge', json={'incident_id': incident['id']})
    assert result.status_code == 409
    assert 'Healthy Docker baseline required' in result.json()['detail']
    assert calls == [old_copy]
    assert session.view.phase == 'analyzed' and session.view.active_incident is None
    assert session.copy == old_copy and patch_lab.copy_files(old_copy) == before


@pytest.mark.parametrize('failure', [
    SandboxResult(status='passed', output='SyntaxError CODEPROOF_FAULT_fake'),
    SandboxResult(status='failed', output='AssertionError: unrelated test failed'),
    SandboxResult(status='failed', output='SyntaxError: elsewhere'),
    SandboxResult(status='timeout'), SandboxResult(status='unavailable'), SandboxResult(status='error'),
])
def test_unreproduced_fault_rolls_back_candidate(connected, monkeypatch, failure):
    client, session, base, incident = connected
    before = patch_lab.copy_files(session.copy)
    old_copy = session.copy
    calls = reproduce(monkeypatch, lambda *_: failure)
    response = client.post(base + '/challenge', json={'incident_id': incident['id']})
    assert response.status_code == 409
    assert session.copy == old_copy and patch_lab.copy_files(old_copy) == before
    assert not Path(calls[1][0]).exists()
    assert session.view.phase == 'analyzed'


def test_changed_original_prevents_fault(connected, workspace, monkeypatch):
    client, session, base, incident = connected
    (workspace / 'main.py').write_text('value = 2\n')
    def forbidden(*args):
        pytest.fail('Do not run a stale project baseline')
    monkeypatch.setattr(sessions.sandbox, 'run_managed_copy', forbidden)
    response = client.post(base + '/challenge', json={'incident_id': incident['id']})
    assert response.status_code == 409
    assert session.view.phase == 'analyzed'


def test_original_change_during_checks_discards_fault(connected, workspace, monkeypatch):
    client, session, base, incident = connected
    old_copy = session.copy
    def failure(copy, runner):
        (workspace / 'main.py').write_text('value = 3\n')
        return detected(copy, runner)
    calls = reproduce(monkeypatch, failure)
    response = client.post(base + '/challenge', json={'incident_id': incident['id']})
    assert response.status_code == 409
    assert session.copy == old_copy and not Path(calls[1][0]).exists()
    assert session.view.phase == 'analyzed'


def test_forged_incident_never_reaches_docker(connected, monkeypatch):
    client, session, base, _ = connected
    def forbidden(*args):
        pytest.fail('Unknown or arbitrary paths cannot reach Docker')
    monkeypatch.setattr(sessions.sandbox, 'run_managed_copy', forbidden)
    for value in ('../../outside.py', 'request-field', 'syntax-not-this-session'):
        assert client.post(base + '/challenge', json={'incident_id': value}).status_code == 400
    assert session.view.phase == 'analyzed'


def test_ai_analysis_can_be_explicitly_enabled_after_controlled_fault(connected, monkeypatch):
    from backend.tests.test_sessions import ProviderTransport
    client, session, base, incident = connected
    reproduce(monkeypatch)
    assert client.post(base + '/challenge', json={'incident_id': incident['id']}).status_code == 200
    transport = ProviderTransport()
    client.app.state.provider_factory = transport.factory
    response = client.post(base + '/analysis', json={'use_ai': True})
    assert response.status_code == 200, response.text
    assert session.use_ai and session.view.phase == 'investigating'
    assert len(transport.calls) == 2
    assert client.post(base + '/hint').status_code == 200
    assert len(transport.calls) == 2  # controlled hints stay local after AI opt-in


def test_catalog_filters_artifacts_tests_and_unsupported_languages():
    from backend.services.controlled_faults import catalog
    files = {'main.py': 'x=1', 'app.mjs': 'export const x=1;', 'screen.dart': 'void main() {}',
             'test_main.py': 'x=1', 'tests/helper.py': 'x=1', '.pytest-tmp/main.py': 'x=1',
             'node_modules/app.js': 'x=1', 'app.test.js': 'x=1', 'empty.py': ''}
    choices = catalog(files)
    assert {item.incident.target_file for item in choices} == {'main.py', 'app.mjs'}
    assert len({item.incident.id for item in choices}) == len(choices)
    assert len(catalog({f'module_{i}.py': 'x=1' for i in range(100)})) == 60


def test_controlled_fault_review_patch_and_validation_stay_scoped(connected, workspace, monkeypatch):
    import difflib
    import json
    from backend.tests.test_sessions import ProviderTransport
    client, session, base, incident = connected
    calls = reproduce(monkeypatch)
    assert client.post(base + '/challenge', json={'incident_id': incident['id']}).status_code == 200
    broken = session.view.files['main.py']
    transport = ProviderTransport()
    repair = ''.join(difflib.unified_diff(broken.splitlines(True), ['value = 1\n'], fromfile='a/main.py', tofile='b/main.py'))
    transport.patch_raw = json.dumps({'patch_id': 'controlled-repair', 'description': 'Restore the tested syntax.',
        'diff': repair, 'affected_files': ['main.py'], 'risk_level': 'low', 'validation_warnings': []})
    client.app.state.provider_factory = transport.factory
    assert client.post(base + '/analysis', json={'use_ai': True}).status_code == 200
    result = client.post(base + '/explanation', json={'explanation': 'The appended conditional has invalid syntax; removing it restores module loading.'})
    assert result.status_code == 200, result.text
    assert result.json()['phase'] == 'review'
    assert (workspace / 'main.py').read_text() == 'value = 1\n'
    assert client.post(base + '/patch').status_code == 200
    assert patch_lab.copy_files(session.copy)['main.py'] == 'value = 1\n'
    monkeypatch.setattr(sessions.sandbox, 'run_managed_copy', lambda *_: healthy())
    assert client.post(base + '/validation', json={'runner': 'python-pytest'}).status_code == 200
    assert client.get(base + '/report').json()['readiness'] == 'READY'
    assert (workspace / 'main.py').read_text() == 'value = 1\n'
