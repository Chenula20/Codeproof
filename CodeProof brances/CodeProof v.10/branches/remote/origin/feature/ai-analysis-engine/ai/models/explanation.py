from pydantic import BaseModel, Field


class ExplanationEvaluation(BaseModel):
    """Evaluation of a user's explanation of code/concept."""
    user_explanation: str = Field(..., description="The user's explanation text")
    score: float = Field(..., ge=0.0, le=1.0, description="Score from 0.0 to 1.0")
    feedback: str = Field(..., description="Detailed feedback on the explanation")
    passed: bool = Field(..., description="Whether the explanation meets the threshold")