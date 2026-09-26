from typing import Any, Dict
from ..models import ExplanationEvaluation
from ..providers import BaseAIProvider


class ExplanationEvaluator:
    """Evaluates user explanations of code or concepts."""

    def __init__(self, provider: BaseAIProvider, passing_threshold: float = 0.7):
        self.provider = provider
        self.passing_threshold = passing_threshold

    async def evaluate(
        self,
        user_explanation: str,
        expected_concepts: list[str],
        context: Dict[str, Any]
    ) -> ExplanationEvaluation:
        """Evaluate a user's explanation."""
        prompt = self._build_evaluation_prompt(user_explanation, expected_concepts, context)
        result = await self.provider.generate_structured(
            prompt=prompt,
            response_model=ExplanationEvaluation,
            system_prompt="You are an expert code reviewer evaluating explanations."
        )
        result.passed = result.score >= self.passing_threshold
        return result

    def _build_evaluation_prompt(
        self,
        user_explanation: str,
        expected_concepts: list[str],
        context: Dict[str, Any]
    ) -> str:
        return f"""
Evaluate this user explanation:

User's explanation:
{user_explanation}

Expected concepts to cover:
{', '.join(expected_concepts)}

Context:
- Code being explained: {context.get('code', 'Not provided')}
- Difficulty level: {context.get('difficulty', 'medium')}

Score from 0.0 to 1.0 based on:
1. Accuracy of explanation
2. Coverage of expected concepts
3. Clarity and depth

Provide detailed feedback and a score.
"""