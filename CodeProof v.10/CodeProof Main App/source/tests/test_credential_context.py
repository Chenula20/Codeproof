"""Keep nonsensitive Python credential plumbing while removing literal values."""
import ast
import hashlib
import pytest
from workspace import SecretFilter, WorkspaceGuardian

@pytest.mark.parametrize('source', [
    'token: str = Depends(oauth2_scheme)\n',
    'token = create_access_token(data={"sub": user.username})\n',
    'token = response.json()["access_token"]\n',
    'hashed_password = get_password_hash(password)\n',
    'user = User(hashed_password=hashed_password)\n',
    'hashed_password = Column(String, nullable=False)\n',
    'password: str\n\nclass PublicModel:\n    name: str\n',
    'class Request:\n    password: str\n\nclass Response:\n    name: str\n',
    'password = user.password\n',
    'token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)\n',
])
def test_nonliteral_credential_plumbing_is_preserved(source):
    assert SecretFilter().redact_content(source) == source
    ast.parse(source)

@pytest.mark.parametrize('source', [
    'token = create_access_token(data={"sub": "literal-secret-fixture"})\n',
    'password = get_password_hash("literal-secret-fixture")\n',
    'token = os.getenv("TOKEN", "literal-secret-fixture")\n',
    'token = build("literal-secret-fixture", user.name)\n',
    'password: literal-secret-fixture\npublic: 42\n',
    'password = "literal-secret-fixture"\n',
    'password = literal_secret_fixture\n',
])
def test_literal_credential_values_still_removed(source):
    redacted = SecretFilter().redact_content(source)
    assert 'literal-secret-fixture' not in redacted
    assert 'literal_secret_fixture' not in redacted
    assert '[REDACTED' in redacted

def test_filtered_source_keeps_models_and_auth_calls_and_original_bytes(tmp_path):
    source = 'class User:\n    password: str\n\nhashed_password = Column(String, nullable=False)\ntoken = response.json()["access_token"]\nAPI_KEY = "literal-secret-fixture"\n'
    target = tmp_path / 'app.py'
    target.write_text(source,encoding='utf-8')
    before = hashlib.sha256(target.read_bytes()).hexdigest()
    snapshot = WorkspaceGuardian(str(tmp_path)).create_snapshot()
    filtered = snapshot.files['app.py']
    ast.parse(filtered)
    assert 'Column(String, nullable=False)' in filtered
    assert 'password: str' in filtered
    assert 'response.json()["access_token"]' in filtered
    assert 'literal-secret-fixture' not in snapshot.model_dump_json()
    assert hashlib.sha256(target.read_bytes()).hexdigest() == before
