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
@@ -1,2 +1,2 @@
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
        assert "Path traversal" in result.message

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
        assert "absolute path" in result.message.lower() or "path traversal" in result.message.lower()

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
        assert "absolute path" in result.message.lower() or "path traversal" in result.message.lower()

    def test_apply_patch_rejects_symlink_escape(self):
        """
        Regression test: Patch application must not follow symlinks that escape the workspace.
        
        This test creates a temporary project with a symlink pointing outside the workspace,
        then attempts to apply a patch targeting the symlink. The patch should be rejected.
        """
        import os
        import stat
        
        # Create a temporary workspace
        with tempfile.TemporaryDirectory() as workspace:
            project_dir = os.path.join(workspace, "project")
            os.makedirs(project_dir)
            
            # Create a target file inside the workspace
            target_file = os.path.join(project_dir, "target.txt")
            with open(target_file, "w") as f:
                f.write("original content")
            
            # Create a sentinel file OUTSIDE the workspace (should not be modifiable)
            sentinel_file = os.path.join(workspace, "sentinel.txt")
            with open(sentinel_file, "w") as f:
                f.write("SENTINEL - DO NOT MODIFY")
            
            # Create a symlink inside the project that points to the sentinel
            # This simulates an attacker replacing a file with a symlink
            symlink_path = os.path.join(project_dir, "malicious_link.txt")
            try:
                os.symlink(sentinel_file, symlink_path)
            except (OSError, NotImplementedError):
                # Symlinks may not be supported on this platform without admin rights
                pytest.skip("Symlink creation not supported on this platform")
            
            # Verify the symlink was created and points to the sentinel
            assert os.path.islink(symlink_path)
            assert os.path.realpath(symlink_path) == sentinel_file
            
            # Create a patch that targets the symlink
            patch = """--- a/malicious_link.txt
+++ b/malicious_link.txt
@@ -1 +1 @@
-original content
+MALICIOUS CONTENT
"""
            
            # Attempt to apply the patch - should be rejected due to symlink escape
            success, message = patch_lab.apply_patch(project_dir, patch)
            
            # The patch application should fail because the symlink escapes the workspace
            assert success is False, f"Patch application should have been rejected, but succeeded: {message}"
            assert "escape" in message.lower() or "symlink" in message.lower() or "traversal" in message.lower()
            
            # Verify the sentinel file was NOT modified
            with open(sentinel_file, "r") as f:
                content = f.read()
            assert content == "SENTINEL - DO NOT MODIFY", "Sentinel file was modified - containment breach!"

    def test_apply_patch_absolute_path_rejected(self):
        """Test that absolute paths in patches are rejected during application."""
        with tempfile.TemporaryDirectory() as workspace:
            project_dir = os.path.join(workspace, "project")
            os.makedirs(project_dir)
            
            # Create a patch with Windows absolute path
            patch = """--- a/C:/etc/passwd
+++ b/C:/etc/passwd
@@ -1 +1 @@
-old
+new
"""
            
            success, message = patch_lab.apply_patch(project_dir, patch)
            assert success is False
            assert "escape" in message.lower() or "traversal" in message.lower() or "absolute" in message.lower()

    def test_apply_patch_normal_file_works(self):
        """Test that normal file patches still work correctly."""
        with tempfile.TemporaryDirectory() as workspace:
            project_dir = os.path.join(workspace, "project")
            os.makedirs(project_dir)
            
            # Create a normal file
            target_file = os.path.join(project_dir, "normal.txt")
            with open(target_file, "w") as f:
                f.write("original content")
            
            # Create a valid patch
            patch = """--- a/normal.txt
+++ b/normal.txt
@@ -1 +1 @@
-original content
+patched content
"""
            
            success, message = patch_lab.apply_patch(project_dir, patch)
            assert success is True
            
            # Verify the file was patched
            with open(target_file, "r") as f:
                content = f.read()
            assert content.rstrip('\n') == "patched content"


class TestReleaseReadiness:
    """Test release readiness evaluation."""

    def test_ready_status(self):
        """Test READY status when all tests pass."""
        sandbox_result = SandboxResult(
            status="passed",
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
            tests_total=18,
            tests_passed=18,
            tests_failed=0,
            runtime_errors=[],
            security_warnings=["Deprecated API usage detected"],
        )
        result = release_readiness.evaluate_release_readiness(sandbox_result)
        assert result.status == "WARNING"
        assert result.warnings == 1