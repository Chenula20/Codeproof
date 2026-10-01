"""Run fixed test commands in a prebuilt, restricted, ephemeral Docker container."""
import os
import re
import time
import uuid
from pathlib import Path

from backend.models import SandboxResult
from workspace.models import ProjectSnapshot
from . import patch_lab

MAX_OUTPUT = 65_536
RUNNERS = {
    'python-pytest': 'python -m pytest -q -p no:cacheprovider',
    'python-unittest': 'python -m unittest discover -s tests -v',
    'node-test': 'node --test',
}


def get_sandbox_image() -> str:
    return os.getenv('SANDBOX_DOCKER_IMAGE', 'codeproof/sandbox:latest')


def get_sandbox_limits() -> dict:
    cpu = float(os.getenv('SANDBOX_CPU_LIMIT', '2'))
    timeout = int(os.getenv('SANDBOX_TIMEOUT', '120'))
    memory = os.getenv('SANDBOX_MEMORY_LIMIT', '512m')
    if not 0 < cpu <= 4 or not 1 <= timeout <= 300 or not re.fullmatch(r'[1-9]\d*[mg]', memory):
        raise ValueError('Invalid sandbox limits')
    if int(memory[:-1]) * (1024 if memory[-1] == 'g' else 1) > 2048:
        raise ValueError('Sandbox memory limit exceeds 2 GiB')
    return {'cpu': cpu, 'memory': memory, 'timeout': timeout}


def build_sandbox_image(project_path: str | None = None) -> tuple[bool, str]:
    """Explicit setup builds only the repository-owned image, never project code."""
    client = None
    try:
        import docker
        client = docker.from_env(timeout=120)
        client.images.build(path=str(Path(__file__).resolve().parents[2] / 'sandbox'),
                            tag=get_sandbox_image(), rm=True)
        return True, 'Sandbox image built from trusted sandbox/Dockerfile.'
    except Exception:
        return False, 'Docker image setup failed; check Docker and the configured image.'
    finally:
        if client:
            client.close()


def run_sandbox(project_path: str, patch: str | None = None,
                runner: str = 'python-pytest') -> SandboxResult:
    copy = None
    try:
        copy = patch_lab.create_temporary_copy(project_path)
        if patch:
            success, message = patch_lab.apply_patch(copy, patch)
            if not success:
                return SandboxResult(status='error', runtime_errors=[message])
        return run_managed_copy(copy, runner)
    finally:
        if copy:
            patch_lab.cleanup_temporary_copy(copy)


def run_managed_copy(project_path: str, runner: str = 'python-pytest') -> SandboxResult:
    client = container = copy = None
    name = 'codeproof-' + uuid.uuid4().hex
    started = time.monotonic()
    result = SandboxResult(status='error')
    attempted = False
    try:
        if runner not in RUNNERS:
            raise ValueError('Unsupported test runner')
        # Re-materialize exactly the known manifest, excluding injected files.
        files = patch_lab.copy_files(project_path)
        copy = patch_lab.materialize(ProjectSnapshot(project_id=name, project_root='snapshot', files=files))
        limits = get_sandbox_limits()
        import docker
        from docker.types import LogConfig
        try:
            client = docker.from_env(timeout=min(limits['timeout'], 15))
            client.ping()
            client.images.get(get_sandbox_image())
        except Exception:
            result.status = 'unavailable'
            result.runtime_errors = ['Docker or the prebuilt sandbox image is unavailable.']
            return result
        attempted = True
        container = client.containers.create(
            image=get_sandbox_image(), name=name,
            command=['sh', '-c', 'cp -R /snapshot/. /tmp/project && cd /tmp/project && exec ' + RUNNERS[runner]],
            user='65532:65532', network_mode='none', network_disabled=True,
            mem_limit=limits['memory'], memswap_limit=limits['memory'],
            nano_cpus=int(limits['cpu'] * 1e9), pids_limit=64,
            read_only=True, cap_drop=['ALL'], security_opt=['no-new-privileges:true'],
            tmpfs={'/tmp': 'rw,noexec,nosuid,nodev,size=128m,mode=1777'},
            volumes={copy: {'bind': '/snapshot', 'mode': 'ro'}},
            environment={'PYTHONDONTWRITEBYTECODE': '1', 'HOME': '/tmp'},
            log_config=LogConfig(type='json-file', config={'max-size': '64k', 'max-file': '1'}),
        )
        container.start()
        remaining = max(0.1, limits['timeout'] - (time.monotonic() - started))
        code = container.wait(timeout=remaining).get('StatusCode', -1)
        stream = container.logs(stream=True, follow=False)
        chunks = bytearray()
        try:
            for chunk in stream:
                chunks.extend(chunk[:MAX_OUTPUT - len(chunks)])
                if len(chunks) >= MAX_OUTPUT:
                    break
        finally:
            if hasattr(stream, 'close'):
                stream.close()
        output = chunks.decode('utf-8', errors='replace')
        result = _parse_test_results(output, code, runner)
        result.output = output
        if len(chunks) == MAX_OUTPUT:
            result.security_warnings.append('Test output was capped.')
    except Exception as exc:
        from requests.exceptions import Timeout, ConnectionError
        is_timeout = isinstance(exc, (TimeoutError, Timeout, ConnectionError))
        result.status = 'timeout' if is_timeout else 'error'
        result.runtime_errors = ['Sandbox timed out.' if is_timeout else 'Sandbox execution failed.']
    finally:
        try:
            if container is not None:
                container.remove(force=True, v=True)
            elif attempted and client:
                client.containers.get(name).remove(force=True, v=True)
        except Exception:
            result.status = 'error'
            result.runtime_errors.append('Container cleanup failed; check Docker for ' + name)
        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    result.status = 'error'
                    result.runtime_errors.append('Docker client cleanup failed.')
            if copy:
                patch_lab.cleanup_temporary_copy(copy)
            result.duration_ms = int((time.monotonic() - started) * 1000)
    return result


def _parse_test_results(logs: str, exit_code: int, runner: str = 'python-pytest') -> SandboxResult:
    passed = failed = errors = 0
    if runner == 'python-pytest':
        summaries = [line for line in logs.splitlines() if re.search(r'\bin [\d.]+s', line)]
        summary = summaries[-1] if summaries else ''
        def count(word):
            match = re.search(r'(\d+) ' + word + r'\b', summary)
            return int(match.group(1)) if match else 0
        passed, failed, errors = count('passed'), count('failed'), count('errors?')
    elif runner == 'python-unittest':
        match = re.search(r'Ran (\d+) tests? in', logs)
        total = int(match.group(1)) if match else 0
        skipped_match = re.search(r'skipped=(\d+)', logs)
        skipped = int(skipped_match.group(1)) if skipped_match else 0
        passed, failed = (max(0, total - skipped), 0) if exit_code == 0 else (0, total)
    else:
        match = re.search(r'# pass (\d+)', logs)
        passed = int(match.group(1)) if match else 0
        match = re.search(r'# fail (\d+)', logs)
        failed = int(match.group(1)) if match else 0
    total = passed + failed + errors
    ok = exit_code == 0 and passed > 0 and failed == errors == 0
    return SandboxResult(status='passed' if ok else 'failed', tests_total=total,
        tests_passed=passed, tests_failed=failed + errors,
        runtime_errors=[] if ok else [f'Test runner exited with code {exit_code}; passing evidence required.'])
