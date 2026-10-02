# CodeProof Windows desktop

The connected desktop calls the authenticated FastAPI service on 127.0.0.1. Guardian supplies filtered project files; AI services receive that filtered context. Patches modify registered temporary copies. Target tests run only in the configured trusted Docker image.

## Setup and build

Tested toolchain: Flutter 3.47.5 / Dart 3.13.4, Windows, Visual Studio C++ desktop workload. The Dart SDK constraint is ^3.13.4. From desktop/: flutter pub get, flutter analyze, flutter test, flutter build windows --release. The output folder is build/windows/x64/runner/Release; keep the executable, DLLs and data directory together.

From the repository root, create backend/.venv and install backend/requirements-dev.txt. Start with backend/.venv/Scripts/python.exe -m backend. This intended launcher loads only CodeProof's root .env; inherited process variables take precedence and values are not interpolated. It prints a generated pairing token unless a valid CODEPROOF_TOKEN was explicitly supplied. Keep the backend terminal running.

Connect your project using its filesystem folder, the token of that successfully running CodeProof service, and its loopback port (default 8000, configured with BACKEND_PORT). The port belongs to CodeProof, not the selected dummy app. If the port is busy, select a free BACKEND_PORT and restart; do not kill another listener. GET /health confirms service health; /openapi.json inventories routes. GET / and /favicon.ico are not application UI endpoints and may return 404.

Copy .env.example to root .env only if none exists. Set OPENROUTER_API_KEY privately and choose an available CODEPROOF_MODEL, replacing provider/model-id. Do not paste secrets into chat. Configuration is required for analysis/coaching/patch generation; local inspection and practice do not need a key. Explicit AI consent sends redacted selected contents to OpenRouter. Review sensitivity first: lexical filtering does not guarantee detection of every computed or obfuscated secret.

## Connected workflow and evidence

Project selection opens a real Guardian snapshot and disposable copy. Analysis/skill map use the configured provider. Investigate an observed issue or select one of three controlled incidents when the exact training-project manifest matches: request field, date serialization, database initialization. Incidents modify only registered copies. Close/reopen restores the healthy original. Ordinary external projects do not receive invented faults.

Four progressive hints and three explanation outcomes are supported. Only CORRECT with score >=0.7 permits a reviewed patch; a new explanation revokes old permission. Review the diff, apply it to the managed copy, then choose a supported Docker test runner. Results show measured total/passed/failed-errors/skipped counts or unavailable/unknown/no-tests states. Readiness requires real positive all-pass evidence and original integrity; empty or unavailable counts cannot certify success.

Docker must be running and codeproof/sandbox:latest (or an explicitly configured trusted image) must be built. Validation does not install target dependencies, build untrusted Dockerfiles or run target code on the host. Additional target dependencies require explicit trusted-image provisioning. Limits are configured by the backend; containers are ephemeral, network disabled, non-root, capability restricted, and snapshots mounted read-only.

## Practice and test distinctions

Open sample project is an in-memory practice workspace. Its hints, keyword scoring, static patch and validation/readiness are simulations; no provider or target tests execute. Legacy/demo backend routes also return labeled fixtures. Provider transport regression tests intercept actual request serialization, but do not prove live model quality. Real Docker fixture checks establish runner/isolation behavior, not production readiness for every selected project.

The connected runtime requires private provider/model configuration. See setup-evidence reports for executed checks and unavailable prerequisites; native behavior and live requests must be reported separately from widget tests. Sessions are in memory; close removes owned copies and progress. No installer is supplied by flutter build.
