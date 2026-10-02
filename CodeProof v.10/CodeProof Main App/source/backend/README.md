# CodeProof Main backend

The main backend exposes authenticated /v1 project sessions and public /health. Demo and legacy sample routes are packaged in the separate CodeProof Demo App, not registered here.

Start using python -m backend from this source root after installing backend/requirements-dev.txt into a trusted Python environment. The launcher binds only to 127.0.0.1, loads only the root .env, and prints a pairing token when CODEPROOF_TOKEN is absent. Keep one worker. Configure BACKEND_PORT if needed; do not stop unrelated listeners. Credentials remain private backend environment variables.

POST /v1/sessions accepts {"path":"C:/path/to/project"}. Empty, whitespace-only or missing paths return HTTP 400 before Guardian access. Opening snapshots the selected project and creates a registered disposable copy without requesting AI. Explicit AI analysis/coaching requires OPENROUTER_API_KEY and an available CODEPROOF_MODEL. The model example provider/model-id must be replaced.

Existing /v1 response fields and authentication rules are retained. supported_incidents is empty; active_incident remains null. Controlled demo incident requests return HTTP 400. Investigate a real observed issue using issue and target_file. Explain its cause, review a passing proposal, apply only to the managed copy, and run a supported Docker runner. Prior approval is revoked on a new explanation attempt.

Browser Origin requests remain rejected. Pairing tokens are required for /v1. No endpoint modifies the selected original project. Guardian filters secrets and unsupported files; filtered evidence does not certify an entire production deployment.

Docker validation uses an explicitly provisioned trusted image, no network, non-root user, read-only snapshot mounts, limited writable tmpfs, dropped capabilities, no-new-privileges and bounded CPU/memory/PIDs/time/output. Containers are removed after runs. Validation never installs target requirements, builds target Dockerfiles, or runs selected project code on the host.

Readiness requires real, positive, complete all-pass counts plus integrity/state checks. Unknown or zero counts, skips, execution errors and unavailable Docker remain blocked. Configure an approved image with any required dependencies; never substitute simulated results for executed tests.

Tests under backend/tests and tests use synthetic fixtures and intercepted provider transport. They do not establish live provider reliability. Run them in constrained Docker under the repository's AGENTS.md rules. The preserved demo package has its own legacy/sample tests and service composition.