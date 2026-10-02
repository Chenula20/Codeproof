"""Canonical count and connected mapping regressions; transport mocks are explicit."""
import pytest
from pydantic import ValidationError
from backend.models import TestCounts as Counts, SandboxResult
from backend.services import sandbox, release_readiness

@pytest.mark.parametrize('runner,logs,code,status,counts,readiness', [
 ('python-pytest','3 passed in 0.02s',0,'passed',(3,3,0,0),'READY'),
 ('python-pytest','1 failed, 2 passed in 0.02s',1,'failed',(3,2,1,0),'BLOCKED'),
 ('python-pytest','2 passed, 1 skipped in 0.02s',0,'passed',(3,2,0,1),'BLOCKED'),
 ('python-pytest','2 skipped in 0.02s',0,'failed',(2,0,0,2),'BLOCKED'),
 ('python-pytest','no tests ran in 0.02s',5,'failed',(0,0,0,0),'BLOCKED'),
 ('python-pytest','2 passed, 1 warning in 0.02s',0,'passed',(2,2,0,0),'READY'),
 ('python-pytest','ERROR collecting test_a.py\n1 error in 0.02s',2,'failed',None,'BLOCKED'),
 ('python-pytest','1 passed, 1 xfailed in 0.02s',0,'error',None,'BLOCKED'),
 ('python-pytest','garbled output',0,'error',None,'BLOCKED'),
 ('python-unittest','Ran 3 tests in 0.01s\nFAILED (failures=1)',1,'failed',(3,2,1,0),'BLOCKED'),
 ('python-unittest','Ran 3 tests in 0.01s\nFAILED (errors=1, skipped=1)',1,'failed',(3,1,1,1),'BLOCKED'),
 ('python-unittest','Ran 3 tests in 0.01s\nOK',0,'passed',(3,3,0,0),'READY'),
 ('python-unittest','Ran 3 tests in 0.01s\nOK (skipped=1)',0,'passed',(3,2,0,1),'BLOCKED'),
 ('python-unittest','Ran 0 tests in 0.01s\nOK',0,'failed',(0,0,0,0),'BLOCKED'),
 ('python-unittest','Ran 1 test in 0.01s\nFAILED (failures=2)',1,'error',None,'BLOCKED'),
 ('python-unittest','Ran 1 test in 0.01s\nOK (expected failures=1)',0,'error',None,'BLOCKED'),
 ('node-test','# tests 3\n# pass 2\n# fail 0\n# skipped 1\n# cancelled 0\n# todo 0',0,'passed',(3,2,0,1),'BLOCKED'),
 ('node-test','# tests 2\n# pass 1\n# fail 1\n# skipped 0\n# cancelled 0\n# todo 0',1,'failed',(2,1,1,0),'BLOCKED'),
 ('node-test','# tests 0\n# pass 0\n# fail 0\n# skipped 0\n# cancelled 0\n# todo 0',0,'failed',(0,0,0,0),'BLOCKED'),
 ('node-test','# tests 9\n# pass 1\n# fail 0\n# skipped 0\n# cancelled 0\n# todo 0',0,'error',None,'BLOCKED'),
 ('node-test','# tests 1\n# pass 0\n# fail 0\n# skipped 0\n# cancelled 1\n# todo 0',1,'error',None,'BLOCKED'),
])
def test_completed_summary_contract(runner,logs,code,status,counts,readiness):
 result=sandbox._parse_test_results(logs,code,runner)
 assert result.status==status
 expected=None if counts is None else dict(zip(('total','passed','failed','skipped'),counts))
 assert (result.test_counts.model_dump() if result.test_counts else None)==expected
 ready=release_readiness.evaluate_release_readiness(result)
 assert ready.status==readiness
 assert ready.test_counts==result.test_counts
 if counts is not None:
  assert (result.tests_total,result.tests_passed,result.tests_failed)==counts[:3]

@pytest.mark.parametrize('bad',[{'total':-1}, {'passed':True}, {'failed':1.5}, {'skipped':'0'}, {'total':2}])
def test_strict_consistent_counts(bad):
 with pytest.raises(ValidationError): Counts(**{'total':1,'passed':1,'failed':0,'skipped':0,**bad})

@pytest.mark.parametrize('status',['passed','unavailable','error','timeout'])
def test_unknown_counts_never_ready(status):
 result=SandboxResult(status=status,tests_total=99,tests_passed=99)
 assert result.test_counts is None
 assert release_readiness.evaluate_release_readiness(result).status=='BLOCKED'
