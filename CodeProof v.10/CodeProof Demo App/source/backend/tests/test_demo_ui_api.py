"""Tests for the deterministic demo UI API (/demo/*)."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services import demo_fixtures


client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_demo_state():
    demo_fixtures.reset()
    yield
    demo_fixtures.reset()


class TestDemoOverview:
    def test_overview(self):
        response = client.get("/demo/overview")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Student Event Management System"
        assert "Flask" in data["technologies"]
        assert data["review_focus"]

    def test_skill_map(self):
        response = client.get("/demo/skill-map")
        assert response.status_code == 200
        skills = response.json()["skills"]
        assert len(skills) == 6
        auth = next(s for s in skills if s["key"] == "authentication")
        assert auth["relevance"] == 95
        assert "src/frontend/login.js" in auth["evidence"]


class TestDemoFiles:
    def test_file_tree_original(self):
        response = client.get("/demo/files", params={"source": "original"})
        assert response.status_code == 200
        nodes = response.json()["nodes"]
        paths = {n["path"] for n in nodes}
        assert "src/frontend/login.js" in paths
        assert "src" in paths  # directory node

    def test_challenge_login_js_differs_from_original(self):
        original = client.get("/demo/file", params={"path": "src/frontend/login.js", "source": "original"}).json()
        challenge = client.get("/demo/file", params={"path": "src/frontend/login.js", "source": "challenge"}).json()
        assert "username: username" in original["content"]
        assert "email: username" in challenge["content"]
        assert challenge["highlights"] == [5]
        assert original["highlights"] == []

    def test_missing_file_is_404(self):
        response = client.get("/demo/file", params={"path": "does/not/exist.py"})
        assert response.status_code == 404

    def test_invalid_source_rejected(self):
        assert client.get("/demo/files", params={"source": "bogus"}).status_code == 422


class TestDemoChallengeFlow:
    def test_hint_requires_started_challenge(self):
        response = client.post("/demo/hint", json={"level": 1})
        assert response.status_code == 400

    def test_hint_progression(self):
        client.post("/demo/challenge/start")
        first = client.post("/demo/hint", json={"level": 1}).json()
        assert first["level"] == 1
        assert first["total"] == 4
        last = client.post("/demo/hint", json={"level": 4}).json()
        assert last["title"] == "Fix"
        state = client.get("/demo/state").json()
        assert state["hints_revealed"] == 4

    def test_patch_locked_until_correct_explanation(self):
        client.post("/demo/challenge/start")
        assert client.get("/demo/patch").status_code == 409
        weak = client.post("/demo/explanation", json={"explanation": "something is wrong with login"}).json()
        assert weak["classification"] == "INCORRECT"
        assert client.get("/demo/patch").status_code == 409

    def test_correct_explanation_unlocks_patch(self):
        client.post("/demo/challenge/start")
        answer = ("The frontend sends the credential under the email key, but the handler "
                  "reads the username key, so the credentials are missing and it returns 422.")
        result = client.post("/demo/explanation", json={"explanation": answer}).json()
        assert result["classification"] == "CORRECT"
        assert result["patch_unlocked"] is True
        proposal = client.get("/demo/patch").json()
        assert proposal["affected_file"] == "src/frontend/login.js"
        assert proposal["risk"] == "LOW"
        assert "-      body: JSON.stringify({ email: username, password })" in proposal["diff"]
        assert "+      body: JSON.stringify({ username: username, password })" in proposal["diff"]

    def test_partial_explanation(self):
        client.post("/demo/challenge/start")
        result = client.post("/demo/explanation", json={"explanation": "the username key is missing in the handler"}).json()
        assert result["classification"] in ("PARTIALLY_CORRECT", "CORRECT")
        assert result["patch_unlocked"] is False


class TestDemoValidationAndReadiness:
    def test_validation_fails_before_patch(self):
        client.post("/demo/challenge/start")
        result = client.post("/demo/validation").json()
        assert result["status"] == "failed"
        assert result["simulated"] is True
        assert all(t["status"] == "failed" for t in result["tests"])
        readiness = client.get("/demo/release-readiness").json()
        assert readiness["status"] == "IN_PROGRESS"
        failed = {c["key"]: c["passed"] for c in readiness["checks"]}
        assert failed["challenge_resolved"] is False
        assert failed["original_unchanged"] is True

    def test_full_flow_reaches_ready(self):
        client.post("/demo/challenge/start")
        client.post("/demo/hint", json={"level": 2})
        client.post("/demo/explanation", json={
            "explanation": "client sends email key, handler expects username key, missing credentials, 422"})
        applied = client.post("/demo/patch/apply").json()
        assert applied["applied"] is True
        assert "username: username" in applied["content"]
        validation = client.post("/demo/validation").json()
        assert validation["status"] == "passed"
        assert all(t["status"] == "passed" for t in validation["tests"])
        readiness = client.get("/demo/release-readiness").json()
        assert readiness["status"] == "READY_FOR_REVIEW"
        assert all(c["passed"] for c in readiness["checks"])
        state = client.get("/demo/state").json()
        assert state["validation_passed"] is True

    def test_apply_locked_patch_rejected(self):
        client.post("/demo/challenge/start")
        assert client.post("/demo/patch/apply").status_code == 409

    def test_reset_clears_state(self):
        client.post("/demo/challenge/start")
        client.post("/demo/explanation", json={
            "explanation": "email vs username key mismatch in the handler, missing credentials, 422"})
        client.post("/demo/patch/apply")
        reset = client.post("/demo/reset").json()
        assert reset["challenge_started"] is False
        assert reset["patch_applied"] is False
        assert client.get("/demo/patch").status_code == 409


class TestDemoSecurityBoundary:
    def test_origin_header_still_rejected(self):
        response = client.get("/demo/overview", headers={"Origin": "http://localhost:5173"})
        assert response.status_code == 403


def test_simulated_reevaluation_relocks_patch():
    client.post('/demo/challenge/start')
    answer = 'The frontend sends email but handler reads username, credentials missing with 422.'
    assert client.post('/demo/explanation', json={'explanation': answer}).json()['patch_unlocked']
    rejected = client.post('/demo/explanation', json={'explanation': 'Something unrelated is happening.'}).json()
    assert rejected['classification'] == 'INCORRECT'
    assert rejected['patch_unlocked'] is False
    assert client.get('/demo/patch').status_code == 409


def test_legacy_simulated_partial_is_not_passing():
    from backend.services.challenge_service import evaluate_explanation
    result = evaluate_explanation('auth-001', 'verify hashed password')
    assert result.classification == 'PARTIALLY_CORRECT'
    assert result.passed is False
