# CodeProof v.10 Windows release

This Windows desktop release was built from the maintained application after all 19 captured branch references were reconciled. Version: 1.0.10+10.

Keep codeproof_desktop.exe, every DLL, and the data directory together. Run codeproof_desktop.exe from this folder.

The existing architecture uses a separate local FastAPI service. From the matching merged source root, install backend/requirements-dev.txt into a private Python environment and start `python -m backend`. The service prints its pairing token; use that token and its loopback port in the desktop connection dialog. Keep that service running. See source/desktop/README.md for detailed setup. The executable does not bundle the Python backend or Docker.

Practice mode works without an AI key. Connected AI analysis/coaching/patch generation require private OPENROUTER_API_KEY and a valid CODEPROOF_MODEL; replace example values and never publish secrets. Actual target validation requires Docker Desktop and the trusted codeproof/sandbox:latest image. Original selected projects remain read-only; patches and tests use managed temporary copies.

Verified checks: 510 Python tests passed, 5 explicitly documented skips; 37 Flutter tests passed; no Flutter analyzer findings; Windows build succeeded; 3 healthy training tests passed in the actual restricted Docker sandbox image. Four skipped tests need Docker-daemon access from their test controller and one needs Windows junction support. The separate Docker smoke confirms the sandbox image/fixture, not those skipped backend-controller journeys. Live AI quality and a complete native connected journey were not newly verified.
