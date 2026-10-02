# CodeProof Main App

CodeProof is the Windows developer workspace for inspecting an explicitly selected project, understanding failures, reviewing patches, and validating disposable copies in Docker.

This is the separated MAIN application. Demo/sample projects, the browser presentation demo, controlled training incidents, and the bundled offline practice service are preserved independently in the clearly labelled CodeProof Demo App folder. They are not mounted by this backend or included in the main Windows executable.

Architecture: Flutter Desktop -> Workspace Guardian -> authenticated loopback FastAPI /v1 service -> AI services -> managed-copy Patch Lab -> Docker validation -> release readiness. The original selected user project is read-only; patches and execution use disposable copies.

Start the backend with python -m backend after installing trusted backend dependencies. Its launcher loads only CodeProof's own root .env and pairs the desktop using a token. Select a nonempty project filesystem folder. AI requests require private provider/model configuration and explicit consent. Docker must be running with an approved trusted sandbox image for actual validation.

See backend/README.md and desktop/README.md for setup. No /demo or legacy sample endpoints are served by this main app. Existing /v1 response fields are retained; supported_incidents is empty and controlled demo incident requests are rejected. A blank or omitted project path returns an actionable HTTP 400 and never chooses a sample.

Historical branch archives under CodeProof brances and older deliverable ZIPs are retained as history. They are excluded from the new main source/runtime packages and do not describe the current runtime. The external original dummy app remains separate and untouched.