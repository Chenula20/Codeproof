"""Controlled incidents: real Guardian/copy gates and explicit provider fixtures."""
import asyncio
import difflib
from pathlib import Path
from contextlib import asynccontextmanager
import pytest
from fastapi import HTTPException
from backend.services import incidents, patch_lab, sessions, sandbox, release_readiness
from backend.main import create_app
from backend.session_models import IncidentView
from fastapi.testclient import TestClient
from backend.tests.test_sessions import ProviderTransport, TOKEN
import ast,json,httpx,re

ROOT = Path(__file__).resolve().parents[2] / 'training-project'

@pytest.fixture
def training(tmp_path):
    for name in incidents.BASELINE_MANIFEST:
        dest=tmp_path/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes((ROOT/name).read_bytes())
    return tmp_path

@pytest.mark.parametrize('incident_id', list(incidents.INCIDENTS))
def test_injection_is_deterministic_owned_and_restores_on_reopen(training,incident_id):
    session=sessions.open_session(str(training))
    baseline=dict(session.snapshot.files)
    old=session.copy
    try:
        assert len(session.view.supported_incidents)==3
        session.use_ai=True
        sessions.challenge(session,'','',incident_id)
        item=incidents.INCIDENTS[incident_id]
        assert session.copy!=old and not Path(old).exists()
        assert session.view.files==session.snapshot.files==patch_lab.copy_files(session.copy)
        assert item.after in session.view.files[item.target_file]
        assert item.before not in session.view.files[item.target_file]
        assert session.context().expected_concepts==list(item.concepts)
        assert session.context().relevant_code_excerpts==[session.view.files[item.target_file]]
        assert session.original_unchanged()
        assert incidents.inject(baseline,session.original_hashes,incident_id)[1]==session.view.files
        with pytest.raises(HTTPException): sessions.challenge(session,'','',incident_id)
    finally: session.close()
    reopened=sessions.open_session(str(training))
    try: assert reopened.snapshot.files==baseline and reopened.view.active_incident is None
    finally: reopened.close()
    assert not Path(session.copy).exists()

@pytest.mark.parametrize('change', ['extra','modified','unknown','missing-ai','tampered-copy'])
def test_ineligible_challenge_leaves_session_untouched(training,change):
    if change=='extra': (training/'extra.py').write_text('value = 42\n')
    if change=='modified': (training/'app.py').write_text('value = 42\n')
    session=sessions.open_session(str(training))
    try:
        old=session.copy; before=session.view.model_dump()
        session.use_ai=change!='missing-ai'
        if change=='tampered-copy': (Path(old)/'app.py').write_text('value = 42\n')
        with pytest.raises((ValueError,HTTPException)):
            sessions.challenge(session,'','', 'unknown' if change=='unknown' else 'request-field')
        assert session.copy==old and session.view.model_dump()==before
        assert session.original_unchanged()
    finally: session.close()

def test_materialization_failure_is_transactional(training,monkeypatch):
    session=sessions.open_session(str(training));session.use_ai=True
    old=session.copy;before=session.view.model_dump()
    def fail(_): raise OSError('synthetic allocation failure')
    monkeypatch.setattr(patch_lab,'materialize',fail)
    try:
        with pytest.raises(OSError): sessions.challenge(session,'','','request-field')
        assert session.copy==old and session.view.model_dump()==before
        assert patch_lab.copy_files(old)==session.snapshot.files and session.original_unchanged()
    finally: session.close()

@pytest.mark.parametrize('incident_id',list(incidents.INCIDENTS))
def test_real_docker_baseline_failure_repair(training,incident_id):
    session=sessions.open_session(str(training))
    try:
        good=sandbox.run_managed_copy(session.copy,'python-pytest')
        if good.status=='unavailable': pytest.skip('Real Docker/image unavailable: '+good.output)
        assert good.status=='passed' and good.test_counts.model_dump()==dict(total=3,passed=3,failed=0,skipped=0)
        baseline=dict(session.snapshot.files);session.use_ai=True
        sessions.challenge(session,'','',incident_id)
        bad=sandbox.run_managed_copy(session.copy,'python-pytest')
        assert bad.status=='failed' and bad.test_counts.model_dump()==dict(total=3,passed=2,failed=1,skipped=0)
        assert release_readiness.evaluate_release_readiness(bad).status=='BLOCKED'
        diff=''.join(difflib.unified_diff(session.view.files['app.py'].splitlines(True),baseline['app.py'].splitlines(True),fromfile='a/app.py',tofile='b/app.py'))
        ok,message=patch_lab.apply_patch(session.copy,diff,{'app.py'})
        assert ok,message
        repaired=sandbox.run_managed_copy(session.copy,'python-pytest')
        assert repaired.status=='passed' and repaired.test_counts.passed==3
        assert release_readiness.evaluate_release_readiness(repaired).status=='READY'
        assert session.original_unchanged()
    finally: session.close()

class IncidentTransport(ProviderTransport):
    def __init__(self, incident_id):
        super().__init__();self.incident_id=incident_id
        source={name:(ROOT/name).read_text(encoding='utf-8') for name in incidents.BASELINE_MANIFEST}
        _,broken=incidents.inject(source,incidents.BASELINE_MANIFEST,incident_id)
        self.diff=''.join(difflib.unified_diff(broken['app.py'].splitlines(True),source['app.py'].splitlines(True),fromfile='a/app.py',tofile='b/app.py'))
    def __call__(self,request):
        body=json.loads(request.content);self.payloads.append(body)
        prompt=body['messages'][-1]['content']
        title=ast.literal_eval(prompt.split('Respond with valid JSON matching this schema:\n')[-1])['title']
        self.calls.append((title,prompt))
        if title=='Patch': data={'patch_id':'fixture','description':'Restore agreed baseline','diff':self.diff,'affected_files':['app.py'],'risk_level':'low','validation_warnings':[]}
        elif title=='ExplanationEvaluation': data={'user_explanation':'fixture explanation','classification':'CORRECT','score':.95,'feedback':'Fixture evaluation','passed':True}
        elif title=='HintResponse':
            level=int(re.search(r'HINT LEVEL: (\d)',prompt).group(1));data={'hint_level':level,'hint_content':f'Fixture hint {level}','next_level_available':level<4}
        elif title=='ProjectAnalysis': data={'project_id':'fixture','summary':'Training fixture','technologies':['Python'],'issues':[],'skills':['Debugging']}
        else: data={'project_id':'fixture','skill_estimates':[{'category':'Debugging','relevance':.9,'confidence':.9,'evidence':['app.py']}]}
        return httpx.Response(200,json={'choices':[{'message':{'content':json.dumps(data)}}]})

@pytest.mark.parametrize('incident_id',list(incidents.INCIDENTS))
def test_connected_four_hints_and_patch_context_is_actual_incident(training,incident_id):
    transport=IncidentTransport(incident_id)
    app=create_app(TOKEN,transport.factory)
    with TestClient(app,headers={'Authorization':'Bearer '+TOKEN}) as client:
        view=client.post('/v1/sessions',json={'path':str(training)}).json(); sid=view['id'];url='/v1/sessions/'+sid
        assert len(view['supported_incidents'])==3
        assert client.post(url+'/analysis',json={'use_ai':True}).status_code==200
        response=client.post(url+'/challenge',json={'incident_id':incident_id})
        assert response.status_code==200 and response.json()['active_incident']['id']==incident_id
        for _ in range(4): assert client.post(url+'/hint').status_code==200
        assert client.post(url+'/hint').status_code==409
        response=client.post(url+'/explanation',json={'explanation':'A deterministic fixture explanation of the incident.'})
        assert response.status_code==200 and response.json()['phase']=='review'
        assert client.post(url+'/patch').status_code==200
        item=incidents.INCIDENTS[incident_id]
        for title,prompt in transport.calls:
            if title in ('HintResponse','ExplanationEvaluation','Patch'):
                assert item.after.strip() in prompt
            if title in ('HintResponse','ExplanationEvaluation'):
                assert item.concepts[0] in prompt
        assert app.state.sessions[sid].original_unchanged()
        assert client.delete(url).status_code==200
    assert not app.state.sessions
