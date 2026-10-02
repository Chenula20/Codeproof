# F02/F03 — AI configuration and launcher setup report

Date: 2026-10-01 (Asia/Colombo)
Worktree: C:\Codeproof-fix-ai-setup
Branch: codex/fix-ai-setup
Base: 911d45cc267d8972dd7b65d6cf260bd6e7a779db
Outcome: setup/configuration fixes verified; live provider analysis NOT TESTABLE.
This worktree also carries the verified, uncommitted P01 fix unchanged. Neither worktree is merged into main.

## Actual provider abstraction and source-to-service path

AIProviderConfig is the typed configuration for BaseAIProvider: api_key, model,
temperature (default 0.7), max_tokens (4096), timeout (60 seconds).
BaseAIProvider defines generate, generate_structured, embed and provider_name.
OpenRouterProvider and GeminiProvider implement the abstraction.
The connected backend configured_provider factory selects OpenRouterProvider;
GEMINI_API_KEY alone does not enable or switch connected desktop analysis.
The factory uses a 60-second timeout and closes its HTTP client after use.
AI services consume Guardian snapshots/coaching models; credentials never come
from Flutter. P01 redaction occurs before provider request serialization.

The intended desktop service entrypoint is:
backend/.venv/Scripts/python.exe -m backend

The launcher's module loads trusted CodeProof root configuration before Uvicorn
imports backend.main:app. It binds only 127.0.0.1. If CODEPROOF_TOKEN is absent/
empty it generates a pairing token and prints it locally; an existing token must
have at least 32 characters. Health is public, connected sessions require bearer
authentication. Use one worker.

## Root causes

F02: no private OPENROUTER_API_KEY or usable CODEPROOF_MODEL was available in the
current process or the checked fix/original CodeProof root .env locations.
The earlier analysis 503 was a real missing-prerequisite result, not an AI
quality regression.

F03: original instructions said to copy .env.example to .env, but the launcher
did not load that file. The example omitted CODEPROOF_MODEL and included unused
BACKEND_HOST/LOG_LEVEL settings that suggested unsupported behavior.

## Implemented

- backend/config.py loads only this CodeProof repository's .env by explicit path.
  It does not search selected projects, working directories or ancestor files.
- Existing process variables are authoritative, including empty values.
- Interpolation is disabled; credential characters are not expanded using other
  variables. An absent file allows local inspection. File permission/encoding
  errors produce safe messages without echoing file content.
- backend/__main__.py calls the loader before app import, validates BACKEND_PORT
  as an integer 1–65535 and keeps loopback/token behavior.
- provider_settings validates missing/whitespace-only key/model and the explicit
  example placeholder. Connected missing/example settings return actionable 503.
- .env.example includes nonsecret CODEPROOF_MODEL=provider/model-id. This is a
  placeholder requiring an available OpenRouter model ID, not a recommended or
  asserted currently available model. Keys are blank. Unused settings removed.
- Root/backend/AI documentation explains provider selection, dotenv behavior,
  restart requirements, token/port versus project path, direct Uvicorn differences
  and safe troubleshooting.
- python-dotenv>=1.0,<2 is now an explicit backend dependency. Existing audit
  interpreter already had version 1.2.4; no global package installation occurred.

## Configuration reference

| Variable | Effect |
|---|---|
| OPENROUTER_API_KEY | Private OpenRouter credential; required for connected AI |
| CODEPROOF_MODEL | Explicit available OpenRouter model ID; required for connected AI |
| BACKEND_PORT | Service port; default 8000; 1–65535 |
| CODEPROOF_TOKEN | Optional existing token; omit for generation |
| GEMINI_API_KEY | Used by explicit Gemini callers, not connected provider selection |
| SANDBOX_DOCKER_IMAGE | Trusted validation image, independent prerequisite |
| SANDBOX_CPU_LIMIT / SANDBOX_MEMORY_LIMIT / SANDBOX_TIMEOUT | Existing Docker limits |

Direct python -m uvicorn backend.main:app does not invoke this loader or generate
a token. Supply process variables explicitly, use an explicit Uvicorn env file,
or preferably use python -m backend. Provider/library imports do not load .env.
Restart after configuration edits. Do not overwrite an existing private .env.

## Contracts and impacts

No route, response schema, HTTP status-code mapping, AI model or provider
interface changed. Missing configuration still returns 503 with clearer detail.
Malformed provider output, authentication, timeout and unavailable-service
failures retain the existing sanitized 500 response. Its generic handler logs
only error type and does not emit raw provider exception text.
Distinct typed failure codes/statuses would require a separately approved
cross-component proposal; none was implemented here.

Documentation spans root/backend/AI; production changes remain backend-local.
No Flutter, Docker, Guardian or AI production source was changed for F02/F03.
The Guardian production change visible in this worktree is the unchanged carried
P01 fix.

## Mocked regression verification

22 new configuration/failure test cases cover:
- fixed root dotenv discovery and no selected-project dotenv loading;
- process precedence, including deliberately empty variables;
- disabled interpolation, absent/unreadable file behavior;
- safe port errors, missing configuration and example rejection;
- intended launcher loading/generation and existing token privacy;
- malformed JSON, invalid schema, provider authentication failure,
  timeout and unavailable provider.

Provider failure cases use real configured_provider, OpenRouter serialization
and AI analysis with httpx.MockTransport. They do not make real provider calls.
All verify safe 500, no private details in response/error logs, no analysis state
advance, client cleanup and unchanged fixture bytes.
Carried P01 tests verify source/config literals absent from complete intercepted
provider payloads across analysis, skills, hints, evaluation and patch generation.

## Commands and counts

Interpreter: C:\Codeproof-mvp-audit-worktree\backend\.venv\Scripts\python.exe
Commands ran from C:\Codeproof-fix-ai-setup with PYTHONDONTWRITEBYTECODE=1.
The existing interpreter/dependencies were reused read-only; application source
was imported from the new fix worktree. Cache writing was disabled.

| Command | Result |
|---|---|
| Python AST parse of config/launcher/session/tests/runtime helper | 5 files passed |
| python -m pytest backend/tests/test_configuration.py backend/tests/test_sessions.py tests/test_signing_secret_redaction.py -q -p no:cacheprovider --basetemp=C:\Codeproof-fix-ai-setup\.pytest-tmp-config-1 | 81 passed, 95 warnings, exit 0 |
| python -m pytest backend/tests -q -p no:cacheprovider --basetemp=C:\Codeproof-fix-ai-setup\.pytest-tmp-backend-final --junitxml=setup-evidence/backend-tests.xml | 121 passed, 0 failed/errors, 1 skipped, 295 warnings, exit 0 |
| python -m pytest tests/ --tb=short -q -p no:cacheprovider --basetemp=C:\Codeproof-fix-ai-setup\.pytest-tmp-project-final --junitxml=setup-evidence/project-tests.xml | 193 passed, 0 failed/errors/skipped, 152 warnings, exit 0 |
| git diff --check | Passed |
| python setup-evidence/runtime_launcher_probe.py | Real local launcher verification passed |

Docker availability test remains skipped, unrelated to provider setup.
Existing Gemini support-ended, datetime.utcnow and TestClient warnings remain.
No Flutter checks were rerun because desktop source/contracts were unchanged.

## Real runtime evidence — separate from transport mocks

Two launcher checks were made, each on a newly selected loopback port.
First: port 62417, no root .env, health/open 200; analysis 503 named both missing
provider variables.
Second/final: port 52690, PID 14456. An owned synthetic .env specified the model
placeholder and invalid port 0; the valid process port remained authoritative.
Actual health returned 200, session open returned 200 and signing literal was
redacted. Actual analysis returned 503 naming OPENROUTER_API_KEY only, confirming
the root file's model was loaded. The session closed, source SHA256 stayed
unchanged, owned backend stopped and owned synthetic .env was removed.
The token was retained only in probe memory and replaced with [REDACTED] in logs.
No API-key or token value is in this report.

Live provider analysis: NOT TESTABLE.
Reason: private provider key and usable model were absent. The synthetic file
provided an example placeholder solely for loader verification. No provider
request was sent and no mock success is described as live success.
Live authentication/timeout/malformed-provider behavior therefore remains
unverified; regression transport cases are explicitly mocked.

## Preservation and files

Original checkout: all 253 recorded hashes unchanged; HEAD/index unchanged.
P01 source/test files match the previously verified fix exactly.
Existing protected checkouts were not edited; dummy project was not read or run
for this task. Safe fixtures were created only for verification.
New worktree source/evidence remain uncommitted; no push/main merge occurred.

F02/F03 files:
backend/config.py; backend/__main__.py; backend/services/sessions.py;
backend/requirements.txt; backend/tests/test_configuration.py;
.env.example; README.md; backend/README.md; ai/README.md.

Carried P01 files:
workspace/secret_filter.py; tests/test_signing_secret_redaction.py;
backend/tests/test_sessions.py.

Local evidence:
setup-evidence/runtime_launcher_probe.py, runtime-result.json,
runtime-launcher.log, backend-tests.log/xml, project-tests.log/xml,
preservation.json, and this report. Test temporary directories remain local.

## Required task report

TASK: Investigate F02/F03 and make actual launcher/configuration behavior reliable.
IMPLEMENTED: Explicit safe root dotenv loading, validation, actionable config
messages, model template, accurate provider docs and regressions.
FILES CREATED/CHANGED: Listed above.
ARCHITECTURE IMPACT: None; provider selection and component boundaries preserved.
API IMPACT: No schema/status changes; actionable existing 503 detail.
DATA MODEL IMPACT: None.
SECURITY IMPACT: Fixed-path trusted config; process authority; no interpolation;
P01 protection retained; no live credential or token disclosure.
TESTS: Counts and real/mock distinction above.
KNOWN ISSUES: Live provider untested without private prerequisites; existing
warnings and optional Docker skip remain; P01 lexical limitations still apply.
NEXT DEPENDENCY: Review/integrate these isolated changes, configure private
provider key and available model, then perform a separately recorded live analysis.
PROCESSES: Both setup-owned backend processes stopped; no user processes stopped.
