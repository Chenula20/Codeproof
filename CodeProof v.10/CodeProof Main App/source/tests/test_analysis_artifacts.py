"""Generated pytest fixtures must not replace application context."""
import hashlib
from datetime import datetime
from pathlib import Path

from ai.services import ContextBuilder
from backend.services.guardian import capture, open_guardian
from backend.services import sandbox, release_readiness
from workspace.models import FileMetadata, ProjectIndex, ProjectSnapshot
from workspace.scanner import ProjectScanner
from workspace.snapshot import SnapshotBuilder


def test_generated_fixtures_are_pruned_without_deleting_originals(tmp_path):
    paths = ["backend/main.py", "desktop/lib/app.dart", "tests/test_api.py",
             ".pytest-tmp-backend-final/test_project/package.json",
             "backend/.pytest-tmp-final/test_project/normal.txt",
             ".pytest_tmp_run/test_app.py", "pytest-of-user/pytest-0/test.py",
             ".dart_tool/package_config.json"]
    for name in paths:
        file = tmp_path / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("value = 42\n", encoding="utf-8")
    before = {name: hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()
              for name in paths}
    snapshot, _ = capture(open_guardian(str(tmp_path)))
    assert set(snapshot.files) == set(paths[:3])
    assert before == {name: hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()
                      for name in paths}


def test_real_source_precedes_nested_test_manifests_in_both_budgets(tmp_path):
    files = {".gitignore": "build/\n", "backend/main.py": "APPLICATION_CODE = 42\n",
             "desktop/lib/app.dart": "void main() {}\n"}
    files.update({f"tests/fixture_{i}/package.json": '{"name":"fixture"}'
                  for i in range(40)})
    context = ContextBuilder(max_files=3).build(ProjectSnapshot(
        project_id="probe", project_root="snapshot", files=files))
    assert set(context["files"]) == set(list(files)[:3])
    index = ProjectIndex(project_root=str(tmp_path), files=[
        FileMetadata(path=name, size=len(content), hash=hashlib.sha256(content.encode()).hexdigest(),
                     is_text=True, modified_at=datetime(2026, 10, 2))
        for name, content in files.items()], total_files=len(files), total_size=1000)
    selected = SnapshotBuilder(ProjectScanner(str(tmp_path)))._select_files(index, None, None)
    assert {file.path for file in selected[:3]} == set(list(files)[:3])


def test_root_python_source_wins_over_docs_and_test_fixtures():
    snapshot = ProjectSnapshot(project_id="probe", project_root="snapshot", files={
        "README.md": "docs", "tests/test_main.py": "TEST", "main.py": "APP"})
    assert ContextBuilder(max_files=1).build(snapshot)["files"] == {"main.py": "APP"}


def test_context_budget_includes_notice_and_handles_windows_paths():
    snapshot = ProjectSnapshot(project_id="probe", project_root="snapshot", files={
        "tests\\fixture\\package.json": "{}", "backend\\main.py": "x" * 1000})
    context = ContextBuilder(max_files=1, max_file_chars=50, max_total_chars=30).build(snapshot)
    assert set(context["files"]) == {"backend\\main.py"}
    assert sum(map(len, context["files"].values())) <= 30


def test_entrypoint_is_not_crowded_out_by_library_modules():
    files = {f"ai/models/type_{i}.py": "class Model: pass\n" for i in range(40)}
    files["backend/main.py"] = "APPLICATION_ENTRY = 42\n"
    context = ContextBuilder(max_files=1).build(ProjectSnapshot(
        project_id="probe", project_root="snapshot", files=files))
    assert context["files"] == {"backend/main.py": "APPLICATION_ENTRY = 42\n"}


def test_signing_redaction_stays_enabled_for_test_fixtures(tmp_path):
    file = tmp_path / "tests" / "test_auth.py"
    file.parent.mkdir()
    file.write_text('SIGNING_SECRET = "synthetic-fixture-secret"\n', encoding="utf-8")
    original = file.read_bytes()
    snapshot, _ = capture(open_guardian(str(tmp_path)))
    assert "synthetic-fixture-secret" not in snapshot.files["tests/test_auth.py"]
    assert "[REDACTED SIGNING SECRET]" in snapshot.files["tests/test_auth.py"]
    assert file.read_bytes() == original


def test_missing_collection_summary_is_actionable_and_never_ready():
    result = sandbox._parse_test_results("", 2, "python-pytest")
    assert "exit code 2" in result.runtime_errors[0]
    assert result.test_counts is None
    assert release_readiness.evaluate_release_readiness(result).status == "BLOCKED"
