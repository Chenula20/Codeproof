# Separate dummy remediation

Run from the new CodeProof worktree with its trusted Python environment. The input is read through the hardened Guardian adapter. The output MUST be a new, separate folder; existing output is never overwritten.

```powershell
$env:PYTHONPATH = (Get-Location).Path
backend/.venv/Scripts/python.exe remediation/dummy-app/prepare_copy.py 'C:\New folder\CodeProof-DummyApp' tmp/dummy-new-copy
docker build -t codeproof/dummy-remediation:20261002 remediation/dummy-app/sandbox
$env:SANDBOX_DOCKER_IMAGE = 'codeproof/dummy-remediation:20261002'
```

Select the new copy in CodeProof for inspection/validation. Do not run the copied application/tests on the host. CodeProof validation uses its existing managed-copy Docker runner. The trusted image extension installs reviewed dependencies explicitly; it never reads requirements or Dockerfiles from an opened project.

Copied production auth requires CODEPROOF_DUMMY_SIGNING_KEY as a process variable, at least 32 UTF-8 bytes, supplied privately from a high-entropy generator/secret store. No default or implicit .env loader exists. A length check does not guarantee key entropy. Restart the target after rotation; previously issued tokens become invalid and users must sign in again. Never reuse the old embedded key.

The .py.in files are Docker-target test templates, not host pytest tests. The copy tool materializes them as .py only inside the new copy. They use explicit harmless synthetic credentials. Those credentials are never a production fallback. The sandbox does not forward arbitrary host secrets into target containers; no new secret-injection API was added.

Test passwords/signing fixtures may differ from originals because Guardian redacts source literals. The copy is a filtered test/reference target, not a byte-identical production deployment. Follow reports/release-completion for actual counts and remaining blockers.

HTTPX migration uses the documented explicit transport: [HTTPX ASGI transports](https://www.python-httpx.org/advanced/transports/). The async test marker/loop configuration follows [pytest-asyncio concepts](https://pytest-asyncio.readthedocs.io/en/stable/concepts.html).
The current copy preparation also creates a healthy startup reference: existing users/events/bookings tables are initialized on target startup. The copied regression verifies a fresh separate process/database inside Docker, rather than relying on test-fixture setup. Original training faults remain unchanged. The healthy copied suite passes all 32 tests; target dependency/UTC deprecation warnings are recorded in the report.
