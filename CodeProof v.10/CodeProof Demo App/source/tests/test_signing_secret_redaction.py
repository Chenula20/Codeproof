"""Synthetic regressions for signing-secret redaction; no real credentials."""
import ast
import hashlib
import json
import re
import tomllib

import pytest

from workspace import SecretFilter, WorkspaceGuardian
from backend.services.guardian import capture, open_guardian


@pytest.mark.parametrize("assignment", [
    'SECRET_KEY = "fixture!short"',
    "secret_key = 'fixture!short'",
    'JWT_SECRET = "fixture!short"',
    'JWT_SECRET_KEY = "fixture!short"',
    'jwtSecret = "fixture!short"',
    'SIGNING_KEY = "fixture!short"',
    'signingSecret = "fixture!short"',
    'TOKEN_SECRET = "fixture!short"',
    'SESSION_SECRET = "fixture!short"',
    'APP_SECRET = "fixture!short"',
    'DJANGO_SECRET_KEY = "fixture!short"',
    'SECRET_KEY: str = "fixture!short"',
    'SECRET_KEY: Final[str] = "fixture!short"',
    'settings["SECRET_KEY"] = "fixture!short"',
    '{"SECRET_KEY": "fixture!short", "algorithm": "HS256"}',
    '{"jwt-secret": "fixture!short", "algorithm": "HS256"}',
    "secret-key: fixture!short",
    "jwt_secret: fixture!short,continuation-fixture",
    "jwt_secret: fixture!short;continuation-fixture",
    "jwt_secret: fixture!short\n  continuation-fixture\nalgorithm: HS256",
    '{"secret_key":\n"fixture!short"}',
    '{\n  "secret_key":\n    "fixture!short",\n  "public_value":42\n}',
    'const signingKey =\n"fixture!short";',
    "secret-key: fixture!short#punctuation-fragment",
    "secret-key:\n  fixture!short\nalgorithm: HS256",
    "secret-key: |2-\n  fixture!short\nalgorithm: HS256",
    'secret_key = "fixture!short" # keep this comment',
    "SECRET_KEY = b'fixture!short'",
    "SECRET_KEY = r'fixture!short'",
    'SECRET_KEY = """fixture!short\nmultiline-fragment"""',
    'SECRET_KEY = ("fixture!short"\n "multiline-fragment")',
    'SECRET_KEY = "fixture!short" + "multiline-fragment"',
    'SECRET_KEY = os.getenv("SECRET_KEY", "fixture!short")',
    'SECRET_KEY = os.getenv("SECRET_KEY",\n "fixture!short")',
    'SECRET_KEY = "fixture!short" ' + chr(92) + '\n "multiline-fragment"',
    'jwt_secret: |\n  fixture!short\n  multiline-fragment\nalgorithm: HS256',
    'jwt_secret: >-\n  fixture!short\n  multiline-fragment\nalgorithm: HS256',
    'SECRET_KEY = "fixture!short' + chr(92) + '"escaped-fragment"',
    'const signingKey = ' + chr(96) + 'fixture!short\nmultiline-fragment' + chr(96) + ';',
])
def test_signing_value_removed_without_length_or_character_assumptions(assignment):
    original = assignment + "\npublic_value = 42\n"
    filtered = SecretFilter().redact_content(original)
    for fragment in ("fixture!short", "multiline-fragment", "escaped-fragment", "punctuation-fragment", "continuation-fixture"):
        assert fragment not in filtered
    assert SecretFilter.SIGNING_MARKER in filtered
    assert "public_value = 42" in filtered
    assert SecretFilter().redact_content(filtered) == filtered


@pytest.mark.parametrize("content", [
    "SECRET_KEY_REFERENCE = 'public documentation'\n",
    "from config import SECRET_KEY\n",
    'help_text = "Set SECRET_KEY = env var"\npublic_value = 42\n',
    "SECRET_KEY: str\npublic_value = 42\n",
    'jwt_algorithm = "HS256"\n',
    'SECRET_KEY = os.getenv("SECRET_KEY")\n',
    'SECRET_KEY = os.environ.get("SECRET_KEY")\n',
    'SECRET_KEY = os.environ["SECRET_KEY"]\n',
    "const signingKey = process.env.SIGNING_KEY;\n",
    'print("Read SECRET_KEY from the environment")\n',
])
def test_nonsensitive_context_and_environment_lookups_preserved(content):
    assert SecretFilter().redact_content(content) == content


def test_source_and_structured_config_still_parse():
    filtered = SecretFilter()
    python_source = filtered.redact_content('SECRET_KEY: str = "fixture!short"\nvalue = 42\n')
    ast.parse(python_source)
    assert json.loads(filtered.redact_content(
        '{"secret_key": "fixture!short", "algorithm": "HS256"}'
    )) == {"secret_key": filtered.SIGNING_MARKER, "algorithm": "HS256"}
    assert json.loads(filtered.redact_content(
        '{\n  "secret_key":\n    "fixture!short",\n  "public_value":42\n}'
    )) == {"secret_key": filtered.SIGNING_MARKER, "public_value": 42}
    assert tomllib.loads(filtered.redact_content(
        'secret_key = """fixture!short\nmultiline-fragment"""\nalgorithm = "HS256"\n'
    )) == {"secret_key": filtered.SIGNING_MARKER, "algorithm": "HS256"}


def test_signing_scan_reports_marker_and_custom_patterns_remain_supported():
    filtered = SecretFilter(custom_content_patterns=[(re.compile("custom-fixture"), "Custom")])
    findings = filtered.scan_content('SECRET_KEY = "fixture!short"')
    assert any(f["type"] == "Signing secret" for f in findings)
    assert all("fixture!short" not in f["match"] for f in findings)
    assert "custom-fixture" not in filtered.redact_content("custom-fixture")


def test_all_guardian_snapshot_entrypoints_preserve_original_bytes(tmp_path):
    files = {
        "auth.py": b'SECRET_KEY = "fixture!short"\nALGORITHM = "HS256"\n',
        "config.json": b'{"signing_key":"config-fixture!","public_value":42}',
        "config.yaml": b'jwt_secret: |\n  yaml-fixture!\n  continuation-fixture\nalgorithm: HS256\n',
        ".env": b"SECRET_KEY=excluded-env-fixture\n",
    }
    for name, contents in files.items():
        (tmp_path / name).write_bytes(contents)
    before = {name: hashlib.sha256(contents).hexdigest() for name, contents in files.items()}
    guardian = WorkspaceGuardian(str(tmp_path))
    assert "fixture!short" not in guardian.read_file("auth.py")
    assert guardian.read_file(".env") is None
    snapshots = [guardian.create_snapshot(), capture(open_guardian(str(tmp_path)))[0]]
    for snapshot in snapshots:
        serialized = snapshot.model_dump_json()
        for value in ("fixture!short", "config-fixture!", "yaml-fixture!", "continuation-fixture", "excluded-env-fixture"):
            assert value not in serialized
        assert ".env" not in snapshot.files
        assert "HS256" in snapshot.files["auth.py"]
        assert "public_value" in snapshot.files["config.json"]
    assert {name: hashlib.sha256((tmp_path / name).read_bytes()).hexdigest() for name in files} == before
