"""Release readiness endpoint."""

from fastapi import APIRouter, HTTPException

from backend.models import ReleaseReadiness, SandboxRunRequest
from backend.services import patch_lab, sandbox, release_readiness

router = APIRouter(prefix="/release-readiness", tags=["release"])


@router.get("", response_model=ReleaseReadiness)
async def get_release_readiness() -> ReleaseReadiness:
    """Get release readiness for the current project state.

    Runs the test suite without any patch and evaluates the results.
    """
    project_path = patch_lab.get_demo_project_path()

    import os
    if not os.path.exists(project_path):
        raise HTTPException(
            status_code=404,
            detail=f"Demo project not found at {project_path}",
        )

    # Run sandbox without patch to get baseline
    sandbox_result = sandbox.run_sandbox(project_path, patch=None)
    return release_readiness.evaluate_release_readiness(sandbox_result)


@router.post("", response_model=ReleaseReadiness)
async def evaluate_release_readiness(request: SandboxRunRequest) -> ReleaseReadiness:
    """Evaluate release readiness after applying a patch.

    Applies the patch in a sandbox, runs tests, and evaluates readiness.
    """
    project_path = patch_lab.get_demo_project_path()

    import os
    if not os.path.exists(project_path):
        raise HTTPException(
            status_code=404,
            detail=f"Demo project not found at {project_path}",
        )

    sandbox_result = sandbox.run_sandbox(project_path, patch=request.patch)
    return release_readiness.evaluate_release_readiness(sandbox_result)
