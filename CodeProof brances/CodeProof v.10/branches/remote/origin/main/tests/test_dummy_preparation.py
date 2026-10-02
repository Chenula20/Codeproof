"""Trusted static copy-tool checks; no copied application is imported or executed."""
import importlib.util
import os
from pathlib import Path
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'remediation/dummy-app/prepare_copy.py'
spec = importlib.util.spec_from_file_location('dummy_copy_tool', SCRIPT)
copy_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(copy_tool)

@pytest.fixture
def source(tmp_path):
    root = tmp_path / 'original'
    (root / 'backend').mkdir(parents=True)
    (root / 'tests').mkdir()
    (root / 'backend/auth.py').write_text('SECRET_KEY = "harmless-source-fixture"\nALGORITHM = "HS256"\n')
    (root / 'backend/main.py').write_text('PUBLIC_VALUE = 42\n# Base.metadata.create_all(bind=engine)  # This line is intentionally commented out\n')
    (root / 'tests/test_auth.py').write_text('''async def test_login_wrong_password(test_user):
    async with client_context as client:
        response = await client.post("/api/login", data={
            "username": "testuser",
            "password": "synthetic-password"
        })
''')
    (root / 'tests/test_api.py').write_text('def test_database_tables_exist():\n    assert False\n')
    return root

def test_hardlinked_external_source_is_not_copied(source, tmp_path):
    outside = tmp_path / 'outside.py'
    outside.write_text('EXTERNAL_VALUE = "outside-fixture-must-not-be-copied"\n')
    os.link(outside, source / 'linked.py')
    destination = tmp_path / 'copy'
    copy_tool.prepare(source, destination)
    assert not (destination / 'linked.py').exists()
    assert outside.read_text().endswith('"outside-fixture-must-not-be-copied"\n')

def test_literal_removed_and_source_unchanged(source, tmp_path):
    before = (source / 'backend/auth.py').read_bytes()
    destination = tmp_path / 'copy'
    copy_tool.prepare(source, destination)
    copied = (destination / 'backend/auth.py').read_text(encoding='utf-8')
    assert 'harmless-source-fixture' not in copied
    assert 'os.environ.get("CODEPROOF_DUMMY_SIGNING_KEY")' in copied
    assert 'No default key is provided' in copied
    assert '\nBase.metadata.create_all(bind=engine)\n' in (destination / 'backend/main.py').read_text()
    assert 'subprocess.run' in (destination / 'tests/test_api.py').read_text()
    assert (source / 'backend/auth.py').read_bytes() == before

def test_existing_destination_not_overwritten(source, tmp_path):
    destination = tmp_path / 'existing'
    destination.mkdir()
    (destination / 'sentinel').write_text('preserve')
    with pytest.raises(ValueError, match='already exists'):
        copy_tool.prepare(source, destination)
    assert (destination / 'sentinel').read_text() == 'preserve'

def test_nested_destination_rejected(source):
    with pytest.raises(ValueError, match='non-overlapping'):
        copy_tool.prepare(source, source / 'nested')
