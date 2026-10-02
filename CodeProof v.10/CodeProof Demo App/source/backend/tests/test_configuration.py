"""Local configuration and provider-failure tests use synthetic credentials only."""
import asyncio
import hashlib
import logging
import os
from contextlib import asynccontextmanager

import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend import config
from backend.main import create_app
from backend.services.sessions import configured_provider


TOKEN = "synthetic-pairing-fixture-1234567890123456789"


@pytest.fixture(autouse=True)
def isolated_configuration(monkeypatch):
    for name in ("OPENROUTER_API_KEY", "CODEPROOF_MODEL", "CODEPROOF_TOKEN",
                 "BACKEND_PORT", "PYTHON_DOTENV_DISABLED"):
        monkeypatch.delenv(name, raising=False)


def test_repository_env_loads_and_never_overrides_inherited_values(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("OPENROUTER_API_KEY=synthetic-file-key\nCODEPROOF_MODEL=fixture/file\nBACKEND_PORT=8011\n")
    monkeypatch.setenv("OPENROUTER_API_KEY", "synthetic-inherited-key")
    monkeypatch.setenv("BACKEND_PORT", "8012")
    config.load_local_environment(env_file)
    assert config.provider_settings() == ("synthetic-inherited-key", "fixture/file")
    assert config.backend_port() == 8012


def test_empty_process_values_are_authoritative(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("OPENROUTER_API_KEY=synthetic-file-key\nCODEPROOF_MODEL=fixture/file\n")
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    config.load_local_environment(env_file)
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        config.provider_settings()


def test_default_env_path_does_not_search_selected_project(tmp_path, monkeypatch):
    repository = tmp_path / "codeproof"
    selected = tmp_path / "selected"
    repository.mkdir()
    selected.mkdir()
    (repository / ".env").write_text("CODEPROOF_MODEL=fixture/repository\n")
    (selected / ".env").write_text("OPENROUTER_API_KEY=selected-private-fixture\nCODEPROOF_MODEL=fixture/selected\n")
    monkeypatch.setattr(config, "REPOSITORY_ROOT", repository)
    monkeypatch.chdir(selected)
    config.load_local_environment()
    assert os.environ["CODEPROOF_MODEL"] == "fixture/repository"
    assert "OPENROUTER_API_KEY" not in os.environ


def test_env_values_are_not_interpolated(tmp_path, monkeypatch):
    monkeypatch.setenv("OTHER_PRIVATE_VALUE", "must-not-be-expanded")
    literal = "literal-" + chr(36) + "{OTHER_PRIVATE_VALUE}"
    env_file = tmp_path / ".env"
    env_file.write_text("OPENROUTER_API_KEY='" + literal + "'\nCODEPROOF_MODEL=fixture/model\n")
    config.load_local_environment(env_file)
    assert os.environ["OPENROUTER_API_KEY"] == literal


def test_missing_env_file_keeps_local_inspection_available(tmp_path):
    config.load_local_environment(tmp_path / "absent.env")
    assert config.backend_port() == 8000
    with TestClient(create_app(TOKEN)) as client:
        assert client.get("/health").status_code == 200


def test_unreadable_env_error_never_echoes_content(tmp_path, monkeypatch):
    def denied(*args, **kwargs):
        raise OSError("synthetic-private-details")
    monkeypatch.setattr(config, "load_dotenv", denied)
    with pytest.raises(SystemExit) as error:
        config.load_local_environment(tmp_path / ".env")
    assert "synthetic-private-details" not in str(error.value)
    assert "permissions" in str(error.value)


@pytest.mark.parametrize("port", ["bad-private-fixture", "", "0", "-1", "65536"])
def test_invalid_port_is_actionable_without_echoing_input(port, monkeypatch):
    monkeypatch.setenv("BACKEND_PORT", port)
    with pytest.raises(SystemExit) as error:
        config.backend_port()
    assert str(error.value) == "BACKEND_PORT must be an integer from 1 to 65535."


@pytest.mark.parametrize("key,model,missing", [
    ("", "", "OPENROUTER_API_KEY"),
    ("synthetic-private-key", "", "CODEPROOF_MODEL"),
    ("   ", "fixture/model", "OPENROUTER_API_KEY"),
])
def test_missing_configuration_has_safe_actionable_errors(key, model, missing, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", key)
    monkeypatch.setenv("CODEPROOF_MODEL", model)
    async def run():
        async with configured_provider():
            pytest.fail("Missing settings must not construct/use a provider")
    with pytest.raises(HTTPException) as error:
        asyncio.run(run())
    assert error.value.status_code == 503
    assert missing in error.value.detail
    assert "restart" in error.value.detail
    assert "synthetic-private-key" not in error.value.detail


def test_example_model_requires_explicit_replacement(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "synthetic-private-key")
    monkeypatch.setenv("CODEPROOF_MODEL", config.EXAMPLE_MODEL)
    with pytest.raises(ValueError, match="Replace the CODEPROOF_MODEL example"):
        config.provider_settings()


def test_intended_launcher_loads_settings_before_app_and_generates_token(tmp_path, monkeypatch, capsys):
    from backend import __main__ as launcher
    (tmp_path / ".env").write_text("BACKEND_PORT=8021\nCODEPROOF_MODEL=fixture/model\n")
    monkeypatch.setattr(config, "REPOSITORY_ROOT", tmp_path)
    calls = []
    monkeypatch.setattr(launcher, "_serve", lambda listener, port: calls.append((listener.getsockname()[0], port)))
    launcher.main()
    generated = os.environ["CODEPROOF_TOKEN"]
    output = capsys.readouterr().out
    assert len(generated) >= 32
    assert output == "Local pairing token: " + generated + "\n"
    assert calls == [("127.0.0.1", 8021)]
    assert os.environ["CODEPROOF_MODEL"] == "fixture/model"


def test_launcher_respects_private_process_token_and_does_not_print_it(monkeypatch, capsys):
    from backend import __main__ as launcher
    monkeypatch.setenv("CODEPROOF_TOKEN", TOKEN)
    monkeypatch.setattr(launcher, "load_local_environment", lambda: None)
    monkeypatch.setattr(launcher, "_serve", lambda listener, port: None)
    monkeypatch.setattr(launcher, "backend_port", lambda: 0)
    launcher.main()
    assert capsys.readouterr().out == ""
    assert os.environ["CODEPROOF_TOKEN"] == TOKEN


@pytest.mark.parametrize("failure", [
    "malformed_json", "invalid_schema", "authentication", "timeout", "unavailable"
])
def test_provider_failures_preserve_state_and_hide_private_details(failure, tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("OPENROUTER_API_KEY", "synthetic-private-key")
    monkeypatch.setenv("CODEPROOF_MODEL", "fixture/model")
    (tmp_path / "auth.py").write_text('SECRET_KEY = "synthetic-source-secret!"\nPUBLIC_VALUE = 42\n')
    original = hashlib.sha256((tmp_path / "auth.py").read_bytes()).hexdigest()
    requests = []
    instances = []

    def transport(request):
        requests.append(request.content)
        assert b"synthetic-source-secret!" not in request.content
        if failure == "timeout":
            raise httpx.ReadTimeout("synthetic-private-details", request=request)
        if failure in ("authentication", "unavailable"):
            return httpx.Response(401 if failure == "authentication" else 503,
                                  text="synthetic-private-details")
        content = "not-json synthetic-private-details" if failure == "malformed_json" else '{"project_id": []}'
        return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})

    @asynccontextmanager
    async def intercepted_provider():
        async with configured_provider() as provider:
            instances.append(provider)
            await provider.client.aclose()
            provider.client = httpx.AsyncClient(transport=httpx.MockTransport(transport))
            yield provider

    app = create_app(TOKEN, intercepted_provider)
    with caplog.at_level(logging.ERROR), TestClient(
            app, raise_server_exceptions=False, headers={"Authorization": "Bearer " + TOKEN}) as client:
        opened = client.post("/v1/sessions", json={"path": str(tmp_path)})
        assert opened.status_code == 200
        session_id = opened.json()["id"]
        response = client.post("/v1/sessions/" + session_id + "/analysis", json={"use_ai": True})
        assert response.status_code == 500
        assert response.json() == {"detail": "Operation failed; check local service configuration."}
        assert "synthetic-private" not in response.text
        assert "synthetic-private" not in caplog.text
        session = app.state.sessions[session_id]
        assert session.use_ai is False
        assert session.view.phase == "analyzed"
        assert session.view.patch is None
        assert client.delete("/v1/sessions/" + session_id).status_code == 200
    assert len(requests) == 1
    assert instances[0].client.is_closed
    assert hashlib.sha256((tmp_path / "auth.py").read_bytes()).hexdigest() == original


def test_busy_port_preserves_listener_and_emits_no_token(monkeypatch,capsys):
    import socket
    from backend import __main__ as launcher
    with socket.socket() as occupied:
        occupied.bind(('127.0.0.1',0));occupied.listen(1)
        port=occupied.getsockname()[1]
        monkeypatch.setattr(launcher,'load_local_environment',lambda:None)
        monkeypatch.setattr(launcher,'backend_port',lambda:port)
        with pytest.raises(SystemExit) as error:launcher.main()
        assert 'already in use' in str(error.value)
        assert capsys.readouterr().out=='' and 'CODEPROOF_TOKEN' not in os.environ
        with socket.create_connection(('127.0.0.1',port),timeout=1):pass


def test_short_token_fails_before_binding_without_echo(monkeypatch,capsys):
    from backend import __main__ as launcher
    monkeypatch.setattr(launcher,'load_local_environment',lambda:None)
    monkeypatch.setenv('CODEPROOF_TOKEN','synthetic-short')
    def unexpected(_):pytest.fail('Invalid token must not bind')
    monkeypatch.setattr(launcher,'bound_listener',unexpected)
    with pytest.raises(SystemExit) as error:launcher.main()
    assert 'synthetic-short' not in str(error.value) and capsys.readouterr().out==''
