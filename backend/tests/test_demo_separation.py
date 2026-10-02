"""Main app isolation: no bundled demo, implicit selection, or demo mutation."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from backend.main import create_app
from backend.services import sessions

TOKEN = 'main-separation-test-token-12345678901234567890'
ROOT = Path(__file__).resolve().parents[2]


def test_main_openapi_and_routes_do_not_expose_demo_services():
    with TestClient(create_app(TOKEN)) as client:
        paths = client.get('/openapi.json').json()['paths']
        assert set(paths) == {
            '/health', '/v1/sessions', '/v1/sessions/{session_id}',
            '/v1/sessions/{session_id}/analysis', '/v1/sessions/{session_id}/challenge',
            '/v1/sessions/{session_id}/hint', '/v1/sessions/{session_id}/explanation',
            '/v1/sessions/{session_id}/patch', '/v1/sessions/{session_id}/validation',
            '/v1/sessions/{session_id}/report',
        }
        for route in ('/demo/overview', '/project', '/analysis', '/skills',
                      '/challenges', '/release-readiness'):
            assert client.get(route).status_code == 404
        for route in ('/demo/patch/apply', '/sandbox/run', '/patch/validate'):
            assert client.post(route, json={}).status_code == 404
        assert client.get('/health').json()['status'] == 'healthy'
        assert client.post('/v1/sessions', json={}).status_code == 401


@pytest.mark.parametrize('body', [{}, {'path': ''}, {'path': ' \t\n'}])
def test_empty_project_rejected_before_guardian_or_copy(body, monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail('Blank paths must not inspect any implicit directory')
    monkeypatch.setattr(sessions, 'open_guardian', unexpected)
    monkeypatch.setattr(sessions.patch_lab, 'materialize', unexpected)
    app = create_app(TOKEN)
    with TestClient(app, headers={'Authorization': 'Bearer ' + TOKEN}) as client:
        result = client.post('/v1/sessions', json=body)
        assert result.status_code == 400
        assert 'Select a project folder' in result.json()['detail']
        assert not app.state.sessions


def test_explicit_project_uses_only_its_selected_files_and_rejects_incidents(tmp_path):
    original = tmp_path / 'actual-project'
    original.mkdir()
    source = original / 'main.py'
    source.write_text('value = 1\n')
    before = source.read_bytes()
    app = create_app(TOKEN)
    with TestClient(app, headers={'Authorization': 'Bearer ' + TOKEN}) as client:
        result = client.post('/v1/sessions', json={'path': str(original)})
        assert result.status_code == 200
        data = result.json()
        assert data['name'] == 'actual-project'
        assert data['sample'] is False
        assert all(item['target_file'] == 'main.py' for item in data['supported_incidents'])
        assert data['active_incident'] is None
        assert data['files'] == {'main.py': 'value = 1\n'}
        session = app.state.sessions[data['id']]
        session.use_ai = True
        copy = Path(session.copy)
        result = client.post('/v1/sessions/' + data['id'] + '/challenge',
                             json={'incident_id': 'request-field'})
        assert result.status_code == 400
        assert 'demo incidents are unavailable' in result.json()['detail']
        assert session.view.phase == 'analyzed'
        assert source.read_bytes() == before
        assert client.delete('/v1/sessions/' + data['id']).status_code == 200
        assert not copy.exists()
    assert source.read_bytes() == before


def test_main_sources_have_no_demo_components():
    for name in ('demo-project', 'training-project', 'frontend', 'remediation',
                 'backend/routers/demo.py', 'backend/services/demo_fixtures.py',
                 'desktop/lib/services/practice_service.dart'):
        assert not (ROOT / name).exists(), name
    desktop = ROOT / 'desktop/lib'
    assert not any('PracticeWorkspaceService' in p.read_text(encoding='utf-8')
                   for p in desktop.rglob('*.dart'))
