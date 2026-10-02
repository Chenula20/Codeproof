"""Connected OpenRouter failure regressions; HTTP transport is deterministic, never live."""
import json
import httpx
import pytest
from fastapi.testclient import TestClient
from backend.main import create_app
from backend.tests.test_sessions import ProviderTransport, TOKEN, fingerprint, project

PRIVATE_FIXTURE_DETAIL = 'synthetic-provider-detail-not-for-client'

class FaultTransport(ProviderTransport):
    failure = None
    def __call__(self, request):
        if self.failure is None:
            return super().__call__(request)
        if self.failure == 'timeout':
            raise httpx.ReadTimeout(PRIVATE_FIXTURE_DETAIL, request=request)
        if self.failure == 'connection':
            raise httpx.ConnectError(PRIVATE_FIXTURE_DETAIL, request=request)
        codes = {'auth':401, 'missing-model':404, 'unavailable':503}
        if self.failure in codes:
            return httpx.Response(codes[self.failure], json={'error':PRIVATE_FIXTURE_DETAIL})
        content = {'malformed':'{invalid-json', 'invalid-schema':'{"score":9}', 'empty-envelope':None}[self.failure]
        data = {'choices':[]} if content is None else {'choices':[{'message':{'content':content}}]}
        return httpx.Response(200, json=data)

@pytest.mark.parametrize('failure', ['auth','missing-model','unavailable','timeout','connection','malformed','invalid-schema','empty-envelope'])
@pytest.mark.parametrize('stage', ['analysis','explanation'])
def test_connected_failure_hides_details_preserves_original_and_revokes_gate(project, failure, stage):
    transport = FaultTransport()
    app = create_app(TOKEN, transport.factory)
    before = fingerprint(project)
    with TestClient(app, raise_server_exceptions=False, headers={'Authorization':'Bearer '+TOKEN}) as client:
        opened = client.post('/v1/sessions',json={'path':str(project)})
        assert opened.status_code == 200
        sid = opened.json()['id']; base = '/v1/sessions/'+sid
        try:
            if stage == 'explanation':
                assert client.post(base+'/analysis',json={'use_ai':True}).status_code == 200
                assert client.post(base+'/challenge',json={'issue':'Wrong value','target_file':'main.py'}).status_code == 200
                approved = client.post(base+'/explanation',json={'explanation':'The assignment uses the wrong value.'})
                assert approved.status_code == 200 and approved.json()['evaluation']['passed']
            transport.failure = failure
            body = {'use_ai':True} if stage == 'analysis' else {'explanation':'This replaces the old approval.'}
            response = client.post(base+'/'+stage,json=body)
            assert response.status_code == 500  # Established safe API error contract.
            assert response.json() == {'detail':'Operation failed; check local service configuration.'}
            assert PRIVATE_FIXTURE_DETAIL not in response.text
            session = app.state.sessions[sid]
            assert session.view.patch is None
            assert session.view.evaluation is None
            assert client.post(base+'/patch',json={}).status_code == 409
            assert fingerprint(project) == before
        finally:
            assert client.delete(base).status_code == 200
    assert not app.state.sessions
