"""Synthetic source/config syntax and scanner-boundary regressions."""
import ast,json,hashlib,tomllib
import pytest
from workspace import SecretFilter,WorkspaceGuardian
from backend.services.guardian import capture,open_guardian

@pytest.mark.parametrize('source',[
 'hashed_password=get_password_hash("harmless-fixture")',
 'hashed_password=hash_password("harmless-fixture")',
 'password = "harmless-fixture"',
 'API_KEY = "harmless-fixture"',
 'API_SECRET = "harmless-fixture"',
 'AWS_SECRET_KEY = "harmless-fixture"',
 'TOKEN = "harmless-fixture"',
 'password: str = "harmless-fixture"',
 'settings["password"] = "harmless-fixture"',
 'value = {"password": "harmless-fixture", "public": 42}',
 'value = Account(hashed_password=get_password_hash("harmless-fixture"), public=42)',
])
def test_credential_redaction_preserves_identifiers_and_syntax(source):
    filter=SecretFilter();redacted=filter.redact_content(source)
    ast.parse(redacted)
    assert 'harmless-fixture' not in redacted and '[REDACTED' in redacted
    assert filter.redact_content(redacted)==redacted
    if 'get_password_hash' in source:assert 'get_password_hash(' in redacted
    if 'public' in source:assert 'public' in redacted

@pytest.mark.parametrize('format,source',[
 ('json','{"password":"harmless-fixture","public":42}'),
 ('toml','password = "harmless-fixture"\npublic = 42\n'),
 ('yaml','password: harmless-fixture\npublic: 42\n')])
def test_config_context_preserved(format,source):
    redacted=SecretFilter().redact_content(source)
    assert 'harmless-fixture' not in redacted and 'public' in redacted
    if format=='json':assert json.loads(redacted)['public']==42
    if format=='toml':assert tomllib.loads(redacted)['public']==42

def test_snapshot_preserves_original_bytes_and_nonsensitive_code(tmp_path):
    source='value = Account(hashed_password=get_password_hash("harmless-fixture"), public=42)\n'
    file=tmp_path/'app.py';file.write_text(source,encoding='utf-8')
    before=hashlib.sha256(file.read_bytes()).hexdigest()
    snapshot,_=capture(open_guardian(str(tmp_path)))
    ast.parse(snapshot.files['app.py'])
    assert 'harmless-fixture' not in snapshot.model_dump_json()
    assert 'get_password_hash(' in snapshot.files['app.py'] and 'public=42' in snapshot.files['app.py']
    assert hashlib.sha256(file.read_bytes()).hexdigest()==before

def test_scanner_uses_path_components_and_globs(tmp_path):
    include=['test_timeout.py','environment.py','about.py','template.py','src/runtime.py']
    exclude=['out/test.py','.venv/test.py','node_modules/test.js','.git/data.py','notes.log','.env.local','key.pem']
    for name in include+exclude:
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('value=42\n')
    paths={f.path.replace(chr(92),'/') for f in WorkspaceGuardian(str(tmp_path)).list_files()}
    assert set(include)<=paths and not set(exclude)&paths
