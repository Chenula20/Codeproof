"""Verify preserved timestamp wire format, UTC construction and legacy ordering."""
from datetime import datetime, timezone, timedelta
import json,pytest
from workspace.models import ProjectIndex,ProjectSnapshot
from ai.models.analysis import ProjectAnalysis,EngineeringSkillMap
from ai.models.patch import Patch
from backend.models import SessionCreateResponse,AIPatchResponse

CASES=[
(ProjectIndex,dict(project_root='fixture'),'indexed_at'),
(ProjectSnapshot,dict(project_id='fixture',project_root='fixture'),'created_at'),
(ProjectAnalysis,dict(project_id='fixture',summary='safe'),'analyzed_at'),
(EngineeringSkillMap,dict(project_id='fixture'),'generated_at'),
(Patch,dict(patch_id='fixture',description='safe',diff='safe',risk_level='low'),'created_at'),
(SessionCreateResponse,dict(session_id='s',project_id='p',project_name='safe',languages=[],frameworks=[]),'created_at'),
(AIPatchResponse,dict(patch_id='p',description='safe',diff='safe',affected_files=[],risk_level='low'),'created_at')]

@pytest.mark.parametrize('model,args,field',CASES)
def test_timestamp_defaults_preserve_naive_utc_and_round_trip(model,args,field):
    before=datetime.now(timezone.utc).replace(tzinfo=None)
    instance=model(**args); value=getattr(instance,field)
    after=datetime.now(timezone.utc).replace(tzinfo=None)
    assert before<=value<=after and value.tzinfo is None
    serialized=json.loads(instance.model_dump_json())[field]
    assert serialized==value.isoformat() and not serialized.endswith('Z')
    assert getattr(model.model_validate_json(instance.model_dump_json()),field)==value
    old=model(**args,**{field:'2025-01-01T00:00:00'})
    assert getattr(old,field).tzinfo is None and getattr(old,field)<value
