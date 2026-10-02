from typing import Any, Dict
from ..models import HintRequest, HintResponse
from ..providers import BaseAIProvider


class HintEngine:
    """Generates progressive hints for coding challenges."""

    def __init__(self, provider: BaseAIProvider):
        self.provider = provider

    async def generate_hint(self, request: HintRequest, context: Dict[str, Any]) -> HintResponse:
        """Generate a hint based on the request and context."""
        prompt = self._build_hint_prompt(request, context)
        return await self.provider.generate_structured(
            prompt=prompt,
            response_model=HintResponse,
            system_prompt="You are a helpful coding mentor providing progressive hints."
        )

    def _build_hint_prompt(self, request: HintRequest, context: Dict[str, Any]) -> str:
        level_descriptions = {
            1: "Subtle nudge - point in the right direction without giving the answer",
            2: "Moderate guidance - explain the concept or approach needed",
            3: "Direct help - show the solution approach with explanation",
        }

        level_desc = level_descriptions.get(request.hint_level, level_descriptions[1])

        return f"""
Generate a hint for this coding challenge:

Challenge ID: {request.challenge_id}
Hint Level: {request.hint_level} ({level_desc})
Context: {context}

User's current progress: {request.context.get('progress', 'Not started')}
User's question: {request.context.get('question', 'No specific question')}

Provide a hint appropriate for level {request.hint_level}.
Indicate if a higher level hint is available.
"""