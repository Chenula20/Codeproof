"""Google GenAI SDK adapter; public provider contracts remain unchanged."""
import asyncio
import math
from typing import Any, List, Optional
from google import genai
from google.genai import types
from .base import BaseAIProvider, AIProviderConfig


class GeminiProvider(BaseAIProvider):
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self.client = genai.Client(api_key=config.api_key, http_options=types.HttpOptions(
            timeout=config.timeout * 1000,
            retry_options=types.HttpRetryOptions(attempts=1),
        ))

    async def _generate(self, prompt, system_prompt, response_model=None):
        options = types.GenerateContentConfig(
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_tokens,
            system_instruction=system_prompt,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            response_mime_type='application/json' if response_model else None,
            response_json_schema=response_model.model_json_schema() if response_model else None,
        )
        response = await asyncio.wait_for(self.client.aio.models.generate_content(
            model=self.config.model, contents=prompt, config=options), self.config.timeout)
        if not response.text or not response.text.strip():
            raise ValueError('Empty provider response')
        return response.text

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            return await self._generate(prompt, system_prompt)
        except Exception:
            raise RuntimeError('Gemini generation failed; check credentials, model and service availability.') from None

    async def generate_structured(self, prompt: str, response_model: type,
                                  system_prompt: Optional[str] = None) -> Any:
        try:
            text = await self._generate(prompt, system_prompt, response_model)
            return response_model.model_validate_json(text)
        except Exception:
            raise RuntimeError('Gemini structured generation failed or returned invalid output.') from None

    async def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        try:
            # One vector per input, unlike models which aggregate input lists.
            response = await asyncio.wait_for(self.client.aio.models.embed_content(
                model='gemini-embedding-001', contents=texts), self.config.timeout)
            vectors = [embedding.values for embedding in response.embeddings or []]
            if len(vectors) != len(texts) or any(not v or any(not math.isfinite(x) for x in v) for v in vectors):
                raise ValueError('Invalid embedding result')
            return vectors
        except Exception:
            raise RuntimeError('Gemini embedding failed or returned invalid vectors.') from None

    @property
    def provider_name(self) -> str:
        return 'gemini'

    async def close(self):
        try:
            await self.client.aio.aclose()
        finally:
            self.client.close()
