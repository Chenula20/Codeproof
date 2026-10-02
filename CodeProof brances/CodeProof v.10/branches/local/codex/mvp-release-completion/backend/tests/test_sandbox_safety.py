from pathlib import Path
from unittest.mock import MagicMock
import shutil
import pytest

from backend.models import SandboxResult
from backend.services import patch_lab, sandbox, release_readiness


@pytest.fixture
def source(tmp_path):
    root = tmp_path / 'source'
    root.mkdir()
    (root / 'test_one.py').write_text('def test_one(): assert True\n')
    return root


@pytest.fixture
def docker_client(monkeypatch):
    import docker
    client = MagicMock()
    container = client.containers.create.return_value
    container.wait.return_value = {'StatusCode': 0}
    container.logs.return_value = iter([b'1 passed in 0.01s\n'])
    monkeypatch.setattr(docker, 'from_env', lambda **kwargs: client)
    return client


def test_limits_copy_and_cleanup(source, docker_client):
    result = sandbox.run_sandbox(str(source))
    assert result.status == 'passed'
    kwargs = docker_client.containers.create.call_args.kwargs
    assert kwargs['user'] == '65532:65532'
    assert kwargs['network_mode'] == 'none'
    assert kwargs['network_disabled'] is True
    assert kwargs['cap_drop'] == ['ALL']
    assert kwargs['pids_limit'] == 64
    assert kwargs['nano_cpus'] > 0
    assert kwargs['mem_limit'] == kwargs['memswap_limit']
    assert kwargs['read_only'] is True
    assert kwargs['security_opt'] == ['no-new-privileges:true']
    path, mount = next(iter(kwargs['volumes'].items()))
    assert path != str(source) and mount['mode'] == 'ro'
    assert not Path(path).exists()
    docker_client.containers.create.return_value.remove.assert_called_once_with(force=True, v=True)
    docker_client.images.build.assert_not_called()
    docker_client.close.assert_called_once()
    assert (source / 'test_one.py').read_text() == 'def test_one(): assert True\n'


@pytest.mark.parametrize('operation', ['start', 'wait', 'logs'])
def test_cleanup_after_error(source, docker_client, operation):
    getattr(docker_client.containers.create.return_value, operation).side_effect = TimeoutError()
    result = sandbox.run_sandbox(str(source))
    assert result.status == 'timeout'
    docker_client.containers.create.return_value.remove.assert_called_once_with(force=True, v=True)
    assert not patch_lab._copies


def test_cleanup_failed_create_by_unique_name(source, docker_client):
    docker_client.containers.create.side_effect = RuntimeError('lost response')
    assert sandbox.run_sandbox(str(source)).status == 'error'
    docker_client.containers.get.return_value.remove.assert_called_once_with(force=True, v=True)


def test_unavailable_is_not_passing(source, docker_client):
    docker_client.ping.side_effect = RuntimeError('not running')
    result = sandbox.run_sandbox(str(source))
    assert result.status == 'unavailable'
    assert release_readiness.evaluate_release_readiness(result).status == 'BLOCKED'
    docker_client.containers.create.assert_not_called()
    assert not patch_lab._copies


def test_output_cap(source, docker_client):
    docker_client.containers.create.return_value.logs.return_value = iter([b'x' * 100_000])
    result = sandbox.run_sandbox(str(source))
    assert len(result.output) <= sandbox.MAX_OUTPUT
    assert result.status != 'passed'
    assert result.security_warnings


@pytest.mark.parametrize('result', [SandboxResult(status='error'), SandboxResult(status='failed'),
    SandboxResult(status='passed'), SandboxResult(status='passed', tests_total=2, tests_passed=1),
    SandboxResult(status='passed', tests_total=1, tests_passed=1, runtime_errors=['error'])])
def test_readiness_fails_closed(result):
    assert release_readiness.evaluate_release_readiness(result).status == 'BLOCKED'


def test_nonzero_exit_never_passes():
    result = sandbox._parse_test_results('1 passed in 0.01s', 2)
    assert result.status == 'failed'
    assert release_readiness.evaluate_release_readiness(result).status == 'BLOCKED'


def test_skipped_unittests_are_not_passing_evidence():
    result = sandbox._parse_test_results('Ran 2 tests in 0.01s\nOK (skipped=2)', 0, 'python-unittest')
    assert result.status == 'failed'


def test_client_close_error_still_removes_copy(source, docker_client):
    docker_client.close.side_effect = RuntimeError('close failed')
    assert sandbox.run_sandbox(str(source)).status == 'error'
    assert not patch_lab._copies


def test_real_docker_when_available(source):
    if not shutil.which('docker'):
        pytest.skip('Docker is not installed; real container validation unavailable')
    import docker
    try:
        client = docker.from_env()
        client.ping()
        client.images.get(sandbox.get_sandbox_image())
    except Exception:
        pytest.skip('Docker daemon or prebuilt sandbox image unavailable')
    finally:
        if 'client' in locals():
            client.close()
    assert sandbox.run_sandbox(str(source)).status == 'passed'
