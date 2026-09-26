from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HintRequest(BaseModel):
    """Request for a hint from the AI engine."""
    challenge_id: str = Field(..., description="Unique identifier for the challenge")
    hint_level: int = Field(..., ge=1, le=4, description="Hint level (1=direction, 2=component, 3=specific, 4=near-solution)")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context for hint generation")


class HintResponse(BaseModel):
    """Response containing a hint from the AI engine."""
    hint_level: int = Field(..., ge=1, le=4, description="Hint level provided")
    hint_content: str = Field(..., description="The hint content")
    next_level_available: bool = Field(..., description="Whether a higher hint level is available")