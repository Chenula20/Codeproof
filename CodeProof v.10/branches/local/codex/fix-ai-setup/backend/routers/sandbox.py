"""Sandbox execution endpoint."""

from fastapi import APIRouter, HTTPException

from backend.models import SandboxRunRequest, SandboxResult
from backend.services import patch_lab, sandbox

router = APIRouter(prefix="/sandbox", tags=["sandbox"])


@router.post("/run", response_model=SandboxResult)
async def run_sandbox(request: SandboxRunRequest) -> SandboxResult:
    """Run tests in an isolated Docker sandbox.

    Creates a temporary copy of the project, applies the patch,
    runs tests in Docker, and returns structured results.
    """
    project_path = patch_lab.get_demo_project_path()

    import os
    if not os.path.exists(project_path):
        raise HTTPException(
            status_code=404,
            detail=f"Demo project not found at {project_path}",
        )

    result = sandbox.run_sandbox(project_path, patch=request.patch)
    return result
