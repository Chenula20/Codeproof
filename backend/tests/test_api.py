"""Tests for CodeProof Backend API endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)


class TestProjectEndpoints:
    """Test project and skills endpoints."""

    def test_get_project(self):
        """GET /project returns project metadata."""
        response = client.get("/project")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "languages" in data
        assert "frameworks" in data

    def test_get_analysis(self):
        """GET /analysis returns skill estimates."""
        response = client.get("/analysis")
        assert response.status_code == 200
        data = response.json()
        assert "debugging" in data
        assert "api" in data
        assert "database" in data

    def test_get_skills(self):
        """GET /skills returns skill estimates."""
        response = client.get("/skills")
        assert response.status_code == 200
        data = response.json()
        assert "authentication" in data
        assert "testing" in data


class TestChallengeEndpoints:
    """Test challenge endpoints."""

    def test_list_challenges(self):
        """GET /challenges returns list of challenges."""
        response = client.get("/challenges")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_get_challenge(self):
        """GET /challenges/{id} returns challenge details."""
        response = client.get("/challenges/auth-001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "auth-001"
        assert "title" in data
        assert "description" in data

    def test_get_challenge_not_found(self):
        """GET /challenges/{id} returns 404 for unknown challenge."""
        response = client.get("/challenges/nonexistent")
        assert response.status_code == 404

    def test_get_hint(self):
        """POST /challenges/{id}/hint returns a hint."""
        response = client.post("/challenges/auth-001/hint", json={
            "challenge_id": "auth-001"
        })
        assert response.status_code == 200
        data = response.json()
        assert "hint" in data
        assert "level" in data

    def test_evaluate_explanation(self):
        """POST /challenges/{id}/explanation evaluates explanation."""
        response = client.post("/challenges/auth-001/explanation", json={
            "challenge_id": "auth-001",
            "explanation": "Use bcrypt.checkpw to verify hashed password"
        })
        assert response.status_code == 200
        data = response.json()
        assert "classification" in data
        assert "feedback" in data


class TestPatchEndpoints:
    """Test patch validation endpoint."""

    def test_validate_patch_valid(self):
        """POST /patch/validate accepts valid patch."""
        import difflib
        from backend.services.guardian import capture, open_guardian
        from backend.services.patch_lab import get_demo_project_path
        snapshot, _ = capture(open_guardian(get_demo_project_path()))
        before = snapshot.files['backend/auth.py']
        patch = ''.join(difflib.unified_diff(before.splitlines(keepends=True),
            ('# Proposed review change\n' + before).splitlines(keepends=True),
            fromfile='a/backend/auth.py', tofile='b/backend/auth.py'))
        response = client.post("/patch/validate", json={
            "challenge_id": "auth-001",
            "patch": patch
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["files_changed"] == 1

    def test_validate_patch_empty(self):
        """POST /patch/validate rejects empty patch."""
        response = client.post("/patch/validate", json={
            "challenge_id": "auth-001",
            "patch": ""
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False

    def test_validate_patch_invalid_format(self):
        """POST /patch/validate rejects invalid format."""
        response = client.post("/patch/validate", json={
            "challenge_id": "auth-001",
            "patch": "not a valid patch"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False


class TestSandboxEndpoints:
    """Test sandbox execution endpoint."""

    def test_sandbox_run(self):
        """POST /sandbox/run executes tests in Docker."""
        response = client.post("/sandbox/run", json={
            "challenge_id": "auth-001",
            "patch": ""
        })
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "tests_total" in data
        assert "tests_passed" in data


class TestReleaseReadinessEndpoints:
    """Test release readiness endpoint."""

    def test_get_release_readiness(self):
        """GET /release-readiness returns readiness status."""
        response = client.get("/release-readiness")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["READY", "WARNING", "BLOCKED"]
        assert "critical_issues" in data
        assert "warnings" in data
