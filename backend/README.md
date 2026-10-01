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
