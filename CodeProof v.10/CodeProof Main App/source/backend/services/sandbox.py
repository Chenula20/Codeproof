"""Run fixed test commands in a prebuilt, restricted, ephemeral Docker container."""
import os
import re
import time
import uuid
from pathlib import Path

from backend.models import SandboxResult, TestCounts
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
            result.status = 'error'
            result.test_counts = None
            result.tests_total = result.tests_passed = result.tests_failed = 0
            result.runtime_errors = ['Could not determine complete test counts: output was capped.']
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
    """Recognize supported completed summaries; never infer success from unknowns."""
    def unknown(message='Could not determine complete test counts.'):
        return SandboxResult(status='error', runtime_errors=[message])

    passed = failed = skipped = total = 0
    if runner == 'python-pytest':
        summaries = [line.strip().strip('= ').strip() for line in logs.splitlines()
                     if re.search(r'\bin [\d.]+s', line)]
        if not summaries:
            return unknown()
        match = re.fullmatch(r'(.+) in [\d.]+s', summaries[-1])
        if not match:
            return unknown()
        body = match.group(1)
        if body != 'no tests ran':
            outcomes = re.findall(r'(\d+) (passed|failed|errors?|skipped|warnings?)', body)
            remainder = re.sub(r'\d+ (?:passed|failed|errors?|skipped|warnings?)', '', body)
            if not outcomes or remainder.strip(' ,'):
                return unknown('Unsupported pytest summary outcomes.')
            values = {}
            for count, kind in outcomes:
                kind = 'errors' if kind in ('error', 'errors') else kind
                if kind in values:
                    return unknown()
                values[kind] = int(count)
            if 'ERROR collecting' in logs or (values.get('errors', 0) and
                    not any(values.get(k, 0) for k in ('passed', 'failed', 'skipped'))):
                return SandboxResult(status='failed', runtime_errors=[
                    'Test discovery/setup failed; executed test counts are unknown.'])
            passed = values.get('passed', 0)
            failed = values.get('failed', 0) + values.get('errors', 0)
            skipped = values.get('skipped', 0)
        total = passed + failed + skipped
    elif runner == 'python-unittest':
        matches = re.findall(r'^Ran (\d+) tests? in [\d.]+s$', logs, re.M)
        verdicts = re.findall(r'^(OK|FAILED)(?: \(([^\n]*)\))?$', logs, re.M)
        if len(matches) != 1 or len(verdicts) != 1:
            return unknown()
        total = int(matches[0])
        verdict, details = verdicts[0]
        values = {}
        for item in details.split(',') if details else []:
            match = re.fullmatch(r'\s*(failures|errors|skipped)=(\d+)\s*', item)
            if not match or match[1] in values:
                return unknown('Unsupported unittest summary outcomes.')
            values[match[1]] = int(match[2])
        failed = values.get('failures', 0) + values.get('errors', 0)
        skipped = values.get('skipped', 0)
        passed = total - failed - skipped
        if passed < 0 or (verdict == 'OK' and failed) or (verdict == 'FAILED' and not failed):
            return unknown('Inconsistent unittest summary.')
    elif runner == 'node-test':
        values = {}
        for kind in ('tests', 'pass', 'fail', 'skipped', 'cancelled', 'todo'):
            matches = re.findall(r'^# ' + kind + r' (\d+)$', logs, re.M)
            if len(matches) != 1:
                return unknown('Incomplete Node test summary.')
            values[kind] = int(matches[0])
        if values['cancelled'] or values['todo']:
            return unknown('Unsupported Node cancelled/todo outcomes.')
        total, passed, failed, skipped = (values[k] for k in ('tests', 'pass', 'fail', 'skipped'))
    else:
        return unknown('Unsupported test runner.')
    try:
        counts = TestCounts(total=total, passed=passed, failed=failed, skipped=skipped)
    except ValueError:
        return unknown('Inconsistent test counts.')
    ok = exit_code == 0 and passed > 0 and failed == 0
    errors = [] if ok else [
        'No tests collected or no passing tests.' if passed == failed == 0
        else f'Test runner exited with code {exit_code}; passing evidence required.']
    return SandboxResult(status='passed' if ok else 'failed', test_counts=counts,
                         runtime_errors=errors)
