"""Patch validation endpoint."""

from fastapi import APIRouter, HTTPException

from backend.models import PatchValidateRequest, PatchValidateResponse
from backend.services import patch_lab

router = APIRouter(prefix="/patch", tags=["patch"])


@router.post("/validate", response_model=PatchValidateResponse)
async def validate_patch(request: PatchValidateRequest) -> PatchValidateResponse:
    """Validate a patch without applying it.

    Returns whether the patch can be safely applied to a temporary workspace.
    """
    result = patch_lab.validate_patch(request.patch)
    return result
