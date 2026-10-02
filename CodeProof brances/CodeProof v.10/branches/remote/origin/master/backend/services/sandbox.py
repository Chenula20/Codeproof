"""Docker Sandbox — runs tests in isolated Docker containers."""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional

from backend.models import SandboxResult


DOCKERFILE_CONTENT = """FROM python:3.11-slim

RUN groupadd -r sandbox && useradd -r -g sandbox sandbox

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R sandbox:sandbox /app
USER sandbox

CMD ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
"""

COMPOSE_CONTENT = """version: "3.8"
services:
  sandbox:
    build:
      context: .
      dockerfile: Dockerfile
    networks: []
    mem_limit: 2g
    cpus: 2.0
    read_only: true
    tmpfs:
      - /tmp
    security_opt:
      - no-new-privileges:true
"""


def get_sandbox_image() -> str:
    """Get the Docker image name for the sandbox."""
    return os.getenv("SANDBOX_DOCKER_IMAGE", "codeproof/sandbox:latest")


def get_sandbox_limits() -> dict:
    """Get resource limits for the sandbox."""
    return {
        "cpu": float(os.getenv("SANDBOX_CPU_LIMIT", "2")),
        "memory": os.getenv("SANDBOX_MEMORY_LIMIT", "2g"),
        "timeout": int(os.getenv("SANDBOX_TIMEOUT", "300")),
    }


def build_sandbox_image(project_path: str) -> tuple[bool, str]:
    """Build the Docker image for the sandbox.

    Returns (success, message).
    """
    try:
        import docker
        client = docker.from_env()

        # Write Dockerfile and docker-compose.yml to project
        dockerfile_path = os.path.join(project_path, "Dockerfile")
        compose_path = os.path.join(project_path, "docker-compose.yml")

        with open(dockerfile_path, 'w') as f:
            f.write(DOCKERFILE_CONTENT)

        with open(compose_path, 'w') as f:
            f.write(COMPOSE_CONTENT)

        # Build the image
        image, logs = client.images.build(
            path=project_path,
            tag=get_sandbox_image(),
            rm=True,
        )

        return True, f"Sandbox image built: {image.tags[0] if image.tags else 'unknown'}"

    except Exception as e:
        return False, f"Failed to build sandbox image: {str(e)}"


def run_sandbox(project_path: str, patch: Optional[str] = None) -> SandboxResult:
    """Run tests in a Docker sandbox.

    Creates a temporary copy, applies the patch, builds the image,
    runs the tests, and returns the structured result.
    """
    temp_dir = None
    try:
        import docker

        # Create temporary copy
        temp_dir = tempfile.mkdtemp(prefix="codeproof_sandbox_")
        temp_project = os.path.join(temp_dir, "project")
        shutil.copytree(project_path, temp_project, ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", ".git", "node_modules", ".venv", "venv"
        ))

        # Apply patch if provided
        if patch:
            from backend.services.patch_lab import apply_patch
            success, message = apply_patch(temp_project, patch)
            if not success:
                return SandboxResult(
                    status="error",
                    tests_total=0,
                    tests_passed=0,
                    tests_failed=0,
                    runtime_errors=[message],
                    security_warnings=[],
                )

        # Write Dockerfile
        dockerfile_path = os.path.join(temp_project, "Dockerfile")
        with open(dockerfile_path, 'w') as f:
            f.write(DOCKERFILE_CONTENT)

        # Build and run
        client = docker.from_env()
        limits = get_sandbox_limits()

        try:
            # Try to build the image
            image, _ = client.images.build(
                path=temp_project,
                tag="codeproof/sandbox:temp",
                rm=True,
            )
        except Exception as build_error:
            return SandboxResult(
                status="error",
                tests_total=0,
                tests_passed=0,
                tests_failed=0,
                runtime_errors=[f"Docker build failed: {str(build_error)}"],
                security_warnings=[],
            )

        # Run the container
        try:
            container = client.containers.run(
                image="codeproof/sandbox:temp",
                detach=True,
                network_mode="none",
                mem_limit=limits["memory"],
                nano_cpus=int(limits["cpu"] * 1e9),
                read_only=True,
                tmpfs={"/tmp": "rw,noexec,nosuid,size=100m"},
                security_opt=["no-new-privileges:true"],
            )

            # Wait for completion with timeout
            result = container.wait(timeout=limits["timeout"])
            exit_code = result.get("StatusCode", -1)

            # Get logs
            logs = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")

            # Parse test results from pytest output
            sandbox_result = _parse_test_results(logs, exit_code)

            # Cleanup container
            container.remove(force=True)

            return sandbox_result

        except Exception as run_error:
            return SandboxResult(
                status="error",
                tests_total=0,
                tests_passed=0,
                tests_failed=0,
                runtime_errors=[f"Container execution failed: {str(run_error)}"],
                security_warnings=[],
            )

    except ImportError:
        return SandboxResult(
            status="error",
            tests_total=0,
            tests_passed=0,
            tests_failed=0,
            runtime_errors=["Docker SDK not installed. Run: pip install docker"],
            security_warnings=[],
        )
    except Exception as e:
        return SandboxResult(
            status="error",
            tests_total=0,
            tests_passed=0,
            tests_failed=0,
            runtime_errors=[f"Sandbox error: {str(e)}"],
            security_warnings=[],
        )
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def _parse_test_results(logs: str, exit_code: int) -> SandboxResult:
    """Parse pytest output to extract test results."""
    import re

    # Look for pytest summary line: "===== 18 passed in 5.23s ====="
    passed_match = re.search(r'(\d+) passed', logs)
    failed_match = re.search(r'(\d+) failed', logs)
    error_match = re.search(r'(\d+) error', logs)

    tests_passed = int(passed_match.group(1)) if passed_match else 0
    tests_failed = int(failed_match.group(1)) if failed_match else 0
    tests_error = int(error_match.group(1)) if error_match else 0

    tests_total = tests_passed + tests_failed + tests_error

    # Extract runtime errors
    runtime_errors = []
    if exit_code != 0 and tests_total == 0:
        runtime_errors.append(f"Tests exited with code {exit_code}")
        # Add last few lines of logs as error context
        log_lines = logs.strip().split('\n')
        runtime_errors.extend(log_lines[-5:] if len(log_lines) > 5 else log_lines)

    # Extract security warnings (basic patterns)
    security_warnings = []
    security_patterns = [
        (r'WARNING.*security', "Security warning detected in test output"),
        (r'DEPRECATION', "Deprecated API usage detected"),
    ]
    for pattern, warning in security_patterns:
        if re.search(pattern, logs, re.IGNORECASE):
            security_warnings.append(warning)

    status = "passed" if tests_failed == 0 and tests_error == 0 and tests_passed > 0 else "failed"

    return SandboxResult(
        status=status,
        tests_total=tests_total,
        tests_passed=tests_passed,
        tests_failed=tests_failed + tests_error,
        runtime_errors=runtime_errors,
        security_warnings=security_warnings,
    )
