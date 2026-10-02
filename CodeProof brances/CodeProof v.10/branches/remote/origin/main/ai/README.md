# AI Engine

The AI Engine is the core intelligence component of CodeProof. It provides:

- Project analysis and understanding
- Architecture analysis
- Progressive hint generation
- Explanation evaluation
- Patch generation

## Structure

```
ai/
├── models/          # Pydantic data models
├── providers/       # AI provider abstractions (Gemini, OpenRouter)
├── services/        # High-level AI services
├── prompts/         # Prompt templates
└── README.md
```

## Providers

The AI Engine uses a provider abstraction pattern:

- `BaseAIProvider` - Abstract base class
- `GeminiProvider` - Google Gemini implementation
- `OpenRouterProvider` - OpenRouter implementation

Switch providers by changing the provider instance, no code changes needed in services.

## Configuration

The connected desktop backend selects OpenRouterProvider through
backend.services.sessions.configured_provider. It requires OPENROUTER_API_KEY
and CODEPROOF_MODEL. GEMINI_API_KEY configures only callers that explicitly
construct GeminiProvider; it does not switch the connected backend.

The intended python -m backend launcher loads CodeProof's root .env with process
variables authoritative and interpolation disabled. Provider/library imports do
not load environment files. Direct AI callers supply AIProviderConfig themselves.
See backend/README.md for setup and safe configuration-error handling.

## Usage

```python
from ai.providers import GeminiProvider, AIProviderConfig
from ai.services import ProjectAnalyzer

import os
config = AIProviderConfig(api_key=os.environ["GEMINI_API_KEY"],
                          model=os.environ["CODEPROOF_GEMINI_MODEL"])
provider = GeminiProvider(config)
analyzer = ProjectAnalyzer(provider)
try:
    analysis = await analyzer.analyze(project_snapshot)
finally:
    await provider.close()
```
The Gemini adapter uses google-genai 2.25.0. Choose an available Gemini model privately; CODEPROOF_GEMINI_MODEL in this direct-call example does not switch connected OpenRouter sessions. Live verification requires separate Gemini credentials.
