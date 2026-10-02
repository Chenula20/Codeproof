# CodeProof frontend (React + Vite)

Implements the 13 reference screens: welcome hero, Analysis, Skill Map, Code,
Investigation, Patch Review, AI Coach panel, and the Problems / Tests / Sandbox /
Release Readiness bottom panel. It talks to the FastAPI `/demo` routes
(deterministic fixtures, no AI, no disk writes).

```powershell
# terminal 1 (repo root)
backend/.venv/Scripts/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
# terminal 2
cd frontend; npm install; npm run dev      # http://localhost:5173
npm test                                   # UI flow test; needs the backend running
```

Vite proxies `/demo` to the loopback backend, removing Origin only for requests
from the same demo origin. Foreign origins remain rejected, and `/v1` is never
proxied. The UI uses simulated fixtures; it does not run AI or Docker.

For an alternate local backend port, set `CODEPROOF_BACKEND_PORT` before starting
Vite and `CODEPROOF_TEST_URL=http://127.0.0.1:<port>` before running the UI test.
