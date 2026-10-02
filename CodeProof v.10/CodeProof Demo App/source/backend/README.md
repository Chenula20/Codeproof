# Backend integration

Use Python 3.12 and run from the repository root:

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/python -m pip install -r backend/requirements-dev.txt
backend/.venv/Scripts/python -m pytest backend/tests tests -q
backend/.venv/Scripts/python -m backend
```

The launcher binds to `127.0.0.1:8000` and prints a generated pairing token, or
uses `CODEPROOF_TOKEN` (at least 32 characters). Alternatively, set that variable
and run `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`.
Use one process/worker. Sessions are in memory, limited to eight, reclaimed after
two hours when another is opened, and removed on close or normal shutdown.

## Connected desktop API

All `/v1` routes require `Authorization: Bearer <CODEPROOF_TOKEN>`.
Browser Origin requests are rejected. `GET /health` does not require a token.
The response fields in `session_models.py` match the existing Flutter client.

| Method | Route | Body |
| --- | --- | --- |
| POST | `/v1/sessions` | `{"path":"C:/path/to/project"}` |
| POST | `/v1/sessions/{id}/analysis` | `{"use_ai":true}` |
| POST | `/v1/sessions/{id}/challenge` | `{"issue":"Observed failure","target_file":"src/main.py"}` |
| POST | `/v1/sessions/{id}/hint` | `{}` (up to four levels) |
| POST | `/v1/sessions/{id}/explanation` | `{"explanation":"Root cause and correction..."}` |
| POST | `/v1/sessions/{id}/patch` | `{}` (apply reviewed proposal to copy) |
| POST | `/v1/sessions/{id}/validation` | `{"runner":"python-pytest"}` |
| GET | `/v1/sessions/{id}/report` | — |
| DELETE | `/v1/sessions/{id}` | — |

Opening creates a filtered Guardian snapshot and disposable copy without an AI
request. Explicit AI analysis requires `OPENROUTER_API_KEY` and `CODEPROOF_MODEL`.
The real ProjectAnalyzer, HintEngine, ExplanationEvaluator and PatchGenerator
consume the existing typed contracts. No API key is accepted from the desktop.
The explanation endpoint returns a patch proposal only after a passing evaluation.
Only the patch endpoint applies it. No endpoint writes to the original project.
The snapshot's absolute root is removed before any provider call.

The unversioned `/project`, `/analysis`, `/skills`, `/challenges`, `/patch`,
`/sandbox` and `/release-readiness` routes remain **legacy demo mode**, not real
project sessions. Their deterministic skill scores and coaching are practice data.
The Flutter practice workspace remains independent of the backend.

The browser demo under `frontend/` uses the separately labeled `/demo` API.
Those endpoints serve in-memory fixtures and simulated validation only. They do
not access original projects, providers, or Docker. Its Vite proxy exposes only
`/demo` and `/health`; connected `/v1` sessions remain desktop-only.

## Docker validation

Docker must already be installed and running. Image setup is explicit:

```powershell
docker build -t codeproof/sandbox:latest sandbox
```

Validation never builds project Dockerfiles, installs project dependencies, or
runs project code on the host. It uses the configured prebuilt image
(`SANDBOX_DOCKER_IMAGE`), with a read-only mount of a fresh Guardian copy, a
128 MiB writable tmpfs, no network, non-root user, dropped capabilities,
no-new-privileges, and CPU/memory/PID/time/output limits. Containers are removed
in `finally`, including errors and timeouts. A daemon cleanup error is reported.

The supplied image includes Python unittest/pytest, Node's built-in test runner,
and the declared demo Python dependencies. Projects needing other libraries require
an explicitly provisioned trusted image. Missing dependencies fail validation;
they are never installed implicitly.
Guardian excludes secrets, binaries, ignored and oversized files, so a filtered
snapshot may be insufficient to run a project's complete suite. Reports are
evidence from that snapshot, not a production certification. Original hashes are
rechecked through Guardian. No tests, Docker unavailable, or changed originals
keep readiness blocked. Crash recovery of abandoned copies is not implemented.

Tests mock external provider transport and Docker lifecycle calls. The live HTTP
tests start the actual FastAPI factory under Uvicorn on an ephemeral loopback port.
The optional real Docker test is skipped when Docker/image is unavailable.

## Environment and provider setup

The intended launcher is backend/.venv/Scripts/python.exe -m backend.
It explicitly loads only the .env beside this repository's root README, before
importing the FastAPI app. It never searches the current directory, a selected
project, or parent folders for environment files.

Use .env.example as a nonsecret template only when your .env does not already
exist. Set OPENROUTER_API_KEY privately and replace CODEPROOF_MODEL=provider/model-id
with an available OpenRouter model ID. The example is not an actual model.
Do not paste keys or pairing tokens into chats, screenshots, or reports.

Inherited process variables always take precedence, including intentionally empty
values. File interpolation is disabled; dollar/brace text in a credential remains
literal. Restart the backend after editing configuration. An unreadable root .env
produces a safe permissions/encoding diagnostic. An absent file is allowed:
local inspection and practice do not require an AI key.

| Variable | Meaning |
| --- | --- |
| OPENROUTER_API_KEY | Private credential required for connected AI requests |
| CODEPROOF_MODEL | OpenRouter model ID required for connected AI requests |
| BACKEND_PORT | Loopback service port, default 8000; integer 1–65535 |
| CODEPROOF_TOKEN | Optional existing pairing token, at least 32 characters; omit for a generated token |
| GEMINI_API_KEY | Optional for independently constructed GeminiProvider; does not switch the connected backend |
| SANDBOX_DOCKER_IMAGE / SANDBOX_CPU_LIMIT / SANDBOX_MEMORY_LIMIT / SANDBOX_TIMEOUT | Existing Docker settings, separate from provider configuration |

Host is always 127.0.0.1; BACKEND_HOST is not a supported override.
AIProviderConfig supplies model/key/temperature/max_tokens/timeout to the
BaseAIProvider abstraction. The connected configured_provider factory currently
selects OpenRouterProvider with a 60-second request timeout and closes the HTTP
client after use. Services consume typed Guardian snapshots/coaching models.
No provider credential is accepted from Flutter. GeminiProvider exists as a
separate adapter; changing the connected selection is not part of environment setup.

The launcher generates and prints a token only when CODEPROOF_TOKEN is absent or
empty. Use the token from the successfully running service and its BACKEND_PORT
in the desktop dialog; select the dummy filesystem folder, not its backend URL.
Keep one worker. /health does not require a token; /openapi.json lists routes.
Opening/inspecting a project does not call a provider. Analysis is explicit.

Direct python -m uvicorn backend.main:app does NOT run this loader or generate a
token. Supply required process variables yourself, or use Uvicorn's explicit
--env-file option against the intended CodeProof file. Prefer python -m backend
for desktop pairing. Merely importing ai.providers also does not load .env.

| Problem | Behavior / action |
| --- | --- |
| Missing or whitespace-only key/model | HTTP 503 names missing variables, points to root .env/process variables and restart; local inspection still works |
| Unchanged provider/model-id example | HTTP 503 asks you to replace the example model |
| Provider authentication error | Existing sanitized HTTP 500; verify private key/account access without sharing values |
| Malformed JSON or invalid response schema | Existing sanitized HTTP 500; analysis state is not advanced |
| Provider timeout | Existing sanitized HTTP 500; check connectivity/provider availability; configured request timeout is 60 seconds |
| Provider unavailable | Existing sanitized HTTP 500; inspect provider/service availability privately |
| Invalid BACKEND_PORT | Launcher exits with allowed integer range without echoing the supplied value |
| Port already occupied | Choose a free port; never kill an unrelated listener |
| / or /favicon.ico returns 404 | These are not health endpoints; use /health |

HTTP status codes and response schemas are unchanged. Provider failure details,
keys and raw provider output are not returned or logged by the backend's generic
error handler. Distinct typed provider error codes/statuses would require a
separate shared-contract proposal.

Tests in test_configuration.py cover root-file loading, process precedence,
literal values, fixed file discovery, launcher token behavior, missing/example
configuration and real provider serialization with intercepted transport.
Malformed output, schema failure, authentication, timeout and unavailable-service
cases are transport mocks; they do not establish live provider reliability.

## Connected explanation evaluation

SessionView.evaluation includes classification (CORRECT, PARTIALLY_CORRECT or
INCORRECT), score (finite 0..1), feedback and passed. The server derives passed:
CORRECT and score >= 0.7. Provider-supplied passed does not authorize a patch.
Partial/incorrect explanations remain investigating with no patch proposal.
A fresh evaluation attempt revokes previous approval, including on malformed
provider output, transport failure or invalid patch output. Applying still
requires a review-phase session, a patch and a passing correct evaluation.

Older desktop clients can ignore the additive classification field. Updated
clients tolerate its absence only for legacy payload compatibility and show a
generic legacy label; deploy both updated components for verified three-way
semantics. Practice/legacy keyword results remain simulated coaching data and
are not evidence of live-provider evaluation quality.

## Structured validation counts

Connected validation and reports expose nullable test_counts with strict integer
fields total, passed, failed and skipped. Failed combines failed/error test
outcomes. Known counts must sum to total. null means counts are unknown or
unavailable; confirmed empty runs contain measured zeros. Legacy sandbox integer
fields remain compatibility projections and are not readiness evidence when
canonical counts are null.

Readiness requires a positive, complete all-pass count set, no skipped tests,
a passing runner status and all existing state/original/security checks.
Unavailable Docker/image, timeout, missing/truncated/unsupported summaries,
collection failures and empty suites cannot become READY. Connected error status
preserves execution/parse failures. The desktop treats older responses without
counts as unknown and labels practice checks simulated with no executed counts.

The fixed pytest/unittest/Node parsers support standard completed summaries.
Unreconciled collection/subtest outcomes, pytest xfail/xpass/deselection,
unittest expected-failure variants and Node cancelled/todo outcomes remain
unsupported and fail closed. A count report describes the filtered snapshot's
runner output; it is not independent proof of test authenticity or production
readiness. No arbitrary project command or host dependency installation was added.

## Controlled training incidents

Select the bundled training-project filesystem directory for three exact-manifest controlled incidents. The existing challenge route additionally accepts {"incident_id":"request-field"}, date-serialization or database-init. Session responses carry supported_incidents and optional active_incident. Changed/unsupported projects remain ordinary observed-issue investigation. Injection updates only a newly registered disposable copy and its coaching context; closing/reopening restores the unchanged original. Fixture execution is Docker-only.

Use a new writable pytest --basetemp directory under the fix/test worktree for each run on Windows. Do not clean another user's temporary trees. Safe example: backend/.venv/Scripts/python.exe -m pytest backend/tests tests -q --basetemp=.pytest-tmp-new-run . Repository tests are trusted host development checks; selected project execution remains Docker-only.
