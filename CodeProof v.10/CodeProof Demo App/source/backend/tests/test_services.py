"""Tests for backend services."""

import pytest
import os
import tempfile
from backend.services import project_service, challenge_service, patch_lab, release_readiness
from backend.models import SandboxResult


class TestProjectService:
    """Test project service functions."""

    def test_get_project_info(self):
        """Test project info returns correct structure."""
        result = project_service.get_project_info()
        assert result.name is not None
        assert isinstance(result.languages, list)
        assert isinstance(result.frameworks, list)

    def test_get_skills(self):
        """Test skills response has all required fields."""
        result = project_service.get_skills()
        assert 0 <= result.debugging <= 100
        assert 0 <= result.api <= 100
        assert 0 <= result.database <= 100
        assert 0 <= result.authentication <= 100
        assert 0 <= result.testing <= 100
        assert 0 <= result.error_handling <= 100


class TestChallengeService:
    """Test challenge service functions."""

    def test_list_challenges(self):
        """Test listing all challenges."""
        challenges = challenge_service.list_challenges()
        assert len(challenges) >= 3
        ids = [c.id for c in challenges]
        assert "auth-001" in ids
        assert "API-001" in ids
        assert "DB-001" in ids

    def test_get_challenge_detail(self):
        """Test getting challenge details."""
        challenge = challenge_service.get_challenge("auth-001")
        assert challenge is not None
        assert challenge.id == "auth-001"
        assert challenge.title == "Users cannot log in"

    def test_get_challenge_not_found(self):
        """Test getting non-existent challenge returns None."""
        challenge = challenge_service.get_challenge("nonexistent")
        assert challenge is None


class TestPatchLab:
    """Test patch lab functions."""

    def test_validate_valid_patch(self):
        """Test validation of a valid unified diff."""
        patch = """--- a/file.py
+++ b/file.py
@@ -1 +1 @@
-old line
+new line
"""
        result = patch_lab.validate_patch(patch)
        assert result.valid is True
        assert result.files_changed == 1

    def test_validate_empty_patch(self):
        """Test validation rejects empty patch."""
        result = patch_lab.validate_patch("")
        assert result.valid is False

    def test_validate_invalid_format(self):
        """Test validation rejects non-diff text."""
        result = patch_lab.validate_patch("just some text")
        assert result.valid is False

    def test_create_temporary_copy(self):
        """Test temporary copy creation."""
        source = patch_lab.get_demo_project_path()
        temp = patch_lab.create_temporary_copy(source)
        import os
        assert os.path.exists(temp)
        patch_lab.cleanup_temporary_copy(temp)
        assert not os.path.exists(os.path.dirname(temp))

    def test_validate_patch_path_traversal(self):
        """Test validation rejects path traversal in file paths."""
        patch = """--- a/../etc/passwd
+++ b/../etc/passwd
@@ -1 +1 @@
-old
+new
"""
        result = patch_lab.validate_patch(patch)
        assert result.valid is False
        assert result.message

    def test_validate_patch_absolute_path_unix(self):
        """Test validation rejects Unix-style absolute paths in file paths."""
        patch = """--- a//etc/passwd
+++ b//etc/passwd
@@ -1 +1 @@
-old
+new
"""
        result = patch_lab.validate_patch(patch)
        assert result.valid is False
        assert result.message

    def test_validate_patch_absolute_path_windows(self):
        """Test validation rejects Windows-style absolute paths in file paths."""
        patch = """--- a/C:/Windows/System32/drivers/etc/hosts
+++ b/C:/Windows/System32/drivers/etc/hosts
@@ -1 +1 @@
-old
+new
"""
        result = patch_lab.validate_patch(patch)
        assert result.valid is False
        assert result.message

    def test_apply_patch_rejects_symlink_escape(self, tmp_path):
        source = tmp_path / 'source'
        source.mkdir()
        (source / 'example.txt').write_text('original content\n')
        sentinel = tmp_path / 'sentinel.txt'
        sentinel.write_bytes(b'original content\n')
        project = patch_lab.create_temporary_copy(str(source))
        try:
            from pathlib import Path
            target = Path(project) / 'example.txt'
            target.unlink()
            target.symlink_to(sentinel)
            patch = '--- a/example.txt\n+++ b/example.txt\n@@ -1 +1 @@\n-original content\n+MALICIOUS CONTENT\n'
            success, message = patch_lab.apply_patch(project, patch)
            assert not success
            assert 'Symlink' in message
            assert sentinel.read_text() == 'original content\n'
        finally:
            patch_lab.cleanup_temporary_copy(project)

    def test_apply_patch_absolute_path_rejected(self, tmp_path):
        (tmp_path / 'normal.txt').write_text('original content\n')
        project = patch_lab.create_temporary_copy(str(tmp_path))
        try:
            patch = '--- a/C:/etc/passwd\n+++ b/C:/etc/passwd\n@@ -1 +1 @@\n-old\n+new\n'
            assert patch_lab.apply_patch(project, patch)[0] is False
        finally:
            patch_lab.cleanup_temporary_copy(project)

    def test_apply_patch_normal_file_works(self, tmp_path):
        from pathlib import Path
        original = tmp_path / 'normal.txt'
        original.write_text('original content\n')
        project = patch_lab.create_temporary_copy(str(tmp_path))
        try:
            patch = '--- a/normal.txt\n+++ b/normal.txt\n@@ -1 +1 @@\n-original content\n+patched content\n'
            assert patch_lab.apply_patch(project, patch)[0]
            assert (Path(project) / 'normal.txt').read_text() == 'patched content\n'
            assert original.read_text() == 'original content\n'
        finally:
            patch_lab.cleanup_temporary_copy(project)


class TestReleaseReadiness:
    """Test release readiness evaluation."""

    def test_ready_status(self):
        """Test READY status when all tests pass."""
        sandbox_result = SandboxResult(
            status="passed",
            test_counts={"total": 18, "passed": 18, "failed": 0, "skipped": 0},
            tests_total=18,
            tests_passed=18,
            tests_failed=0,
            runtime_errors=[],
            security_warnings=[],
        )
        result = release_readiness.evaluate_release_readiness(sandbox_result)
        assert result.status == "READY"
        assert result.critical_issues == 0

    def test_blocked_status(self):
        """Test BLOCKED status when tests fail."""
        sandbox_result = SandboxResult(
            status="failed",
            test_counts={"total": 18, "passed": 10, "failed": 8, "skipped": 0},
            tests_total=18,
            tests_passed=10,
            tests_failed=8,
            runtime_errors=[],
            security_warnings=[],
        )
        result = release_readiness.evaluate_release_readiness(sandbox_result)
        assert result.status == "BLOCKED"
        assert result.critical_issues == 8

    def test_warning_status(self):
        """Test WARNING status when there are security warnings."""
        sandbox_result = SandboxResult(
            status="passed",
            test_counts={"total": 18, "passed": 18, "failed": 0, "skipped": 0},
            tests_total=18,
            tests_passed=18,
            tests_failed=0,
            runtime_errors=[],
            security_warnings=["Deprecated API usage detected"],
        )
        result = release_readiness.evaluate_release_readiness(sandbox_result)
        assert result.status == "WARNING"
        assert result.warnings == 1