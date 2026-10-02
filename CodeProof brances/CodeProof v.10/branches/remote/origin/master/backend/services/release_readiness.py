"""Release Readiness — converts test/security results into a structured verdict."""

from backend.models import ReleaseReadiness, SandboxResult


def evaluate_release_readiness(sandbox_result: SandboxResult) -> ReleaseReadiness:
    """Evaluate release readiness based on sandbox test results.

    Statuses:
    - READY: All tests pass, no critical issues
    - WARNING: Tests pass but there are warnings
    - BLOCKED: Tests fail or critical issues found
    """
    critical_issues = 0
    warnings = 0

    # Check for critical issues
    if sandbox_result.status == "error":
        critical_issues += len(sandbox_result.runtime_errors)
    elif sandbox_result.status == "failed":
        critical_issues += sandbox_result.tests_failed

    # Check for security warnings
    warnings += len(sandbox_result.security_warnings)

    # Determine status
    if critical_issues > 0:
        status = "BLOCKED"
    elif warnings > 0:
        status = "WARNING"
    else:
        status = "READY"

    return ReleaseReadiness(
        status=status,
        critical_issues=critical_issues,
        warnings=warnings,
        tests_passed=sandbox_result.tests_passed,
        tests_total=sandbox_result.tests_total,
    )
