# Docker runtime validation — 2026-10-01

TASK: Continue Docker validation after authorized WSL prerequisite installation. Validation ran from C:\Codeproof-fix-ai-setup, branch codex/fix-ai-setup. No application source changes were made in this task.

IMPLEMENTED: Built the repository-owned sandbox image, ran real Docker fixtures through CodeProof's existing Guardian → managed copy → sandbox → readiness flow, reran backend regressions with Docker available, and executed the separate dummy app's tests inside Docker. No provider requests were made.

## Outcome

Docker infrastructure and restricted-container execution: PASS for the tested scenarios. Dummy-project test journey: BROKEN at pytest collection because project-root execution cannot import main from backend/main.py. This does not establish a full desktop/AI journey PASS.

| Check | Result | Evidence type |
|---|---|---|
| Docker engine | PASS: Linux engine 29.8.1, WSL2; SDK ping true | Real engine |
| Trusted image build | PASS, command exit 0 | Real build; docker-image-build.log |
| Isolation fixture | PASS: 6 tests | Real Docker |
| Deliberately failing fixture | PASS of failure handling: 1 failing test, readiness BLOCKED | Real Docker; expected failure |
| Timeout | PASS: 3-second budget returned timeout; readiness BLOCKED | Real Docker |
| Unittest runner | PASS: 1 test | Real Docker |
| Node runner | PASS: 1 test using one.test.js | Real Docker |
| Patch to managed copy | PASS: 1 test after patch; original still has failing assertion | Real Docker |
| Effective disk/noexec/cgroup limits | PASS: 3 tests | Real Docker |
| Cleanup | PASS: each recorded container removed, each managed copy removed, registry empty | Real Docker SDK inspection |
| Backend regression suite | 122 passed, 0 failed, 0 errors, 0 skipped; 300 warnings, exit 0 | Mixed: existing mocked tests plus real optional Docker test |
| Separate dummy app | 0 passed; 4 collection errors, pytest exit 2; readiness BLOCKED | Real Docker, unpatched dummy snapshot |
| Original protection | PASS for observed runs | Before/after hashes and HEAD/index baseline |
| Live provider / desktop full journey | NOT TESTABLE in this task | No live credentials/model verification or desktop journey performed |

## Container restrictions actually observed

Inspect evidence shows user 65532:65532; network none and disabled; root filesystem read-only; all capabilities dropped; no-new-privileges; 512 MiB memory with equal memory+swap ceiling; 2 CPUs; 64 PID limit; /tmp tmpfs 128 MiB with noexec,nosuid,nodev; /snapshot mounted read-only from a managed copy rather than the original. Log configuration limits one JSON log file to 64k; production output cap is 65,536 bytes. Output-cap stress behavior was not re-executed live in this task.

Container tests independently verified UID, denied writes to root and snapshot, loopback-only interface and failed connection to a documentation-only IP, no effective capabilities, NoNewPrivs, writable scratch, tmpfs capacity, denied direct scratch execution, and actual cgroup memory/CPU/PID ceilings. These are bounded checks; resource-exhaustion stress tests were not run.

## Dummy failure and next dependency

Dummy: C:\New folder\CodeProof-DummyApp. All four tests import main (also database/models/auth). The app entry module is backend/main.py. The fixed command executes from /tmp/project and does not provide a backend module search path. The real run stopped at collection with ModuleNotFoundError for main. The SandboxResult combines the four collection errors into tests_failed=4, tests_total=4; these are not four executed assertion failures. No tests reached application behavior. Readiness BLOCKED is correct.

Do not install dependencies or execute arbitrary commands from opened projects on the host. Backend + Sandbox Lead should first propose a controlled runner/import-layout solution with the Project Lead; confirm the dummy app's intended packaging and required trusted-image dependencies. This report does not authorize or implement a cross-component/API change. Other missing dependencies may appear once the import issue is addressed; they were not verified here.

## First-run evidence retained

The first probe exited 1 because two fixture-discovery assumptions were wrong. test_timeout.py was omitted by Guardian's existing substring ignore check: the default pattern out matches timeout. This is a real scanner false-positive that can also omit legitimate project files. Owner: Project Lead, workspace/scanner.py. Reported, not fixed.

Node --test did not discover test_one.js and correctly produced zero tests; this was a fixture naming issue. Repeated with test_delay.py and one.test.js in a new fixture directory. The corrected probe exited 0 and all six scenario validations passed. Original first-run evidence remains alongside corrected evidence.

## Preservation and processes

Original checkout C:\Codeproof-main\Codeproof-main: 253 baseline file hashes unchanged; HEAD and index hash unchanged. Protected original untracked items were not modified. Existing audit repositories were not edited; the audit Python environment was used read-only with bytecode disabled. No branches pushed, commits created, merges performed, or files cleaned/reset/stashed.

Dummy: all 6,398 files hashed before and after the actual Docker run, unchanged. Only Guardian-created temporary copies were executed and removed. Raw dummy output was deliberately not retained because tracebacks can contain source literals; sanitized module names, counts, outcome and hashes were retained. No signing key or pairing token is present in this report.

No audit test/container processes remain. Docker Desktop and its engine remain running; no user-owned process was stopped. Observed Desktop PIDs 5916,12040,13980,14288 and backend PIDs 5896,10516 are a time-specific snapshot, not instructions to stop them. Built codeproof/sandbox:latest remains installed.

## Exact commands and evidence

Commands ran from C:\Codeproof-fix-ai-setup. Docker bin was prepended to each command's process PATH; PYTHONDONTWRITEBYTECODE=1 for Python commands.

1. docker version --format '{{json .Server}}' — exit 0. SDK engine ping/info — exit 0.
2. docker image inspect codeproof/sandbox:latest --format '{{.Id}}' — image absent initially. docker build --progress plain -t codeproof/sandbox:latest sandbox — exit 0; log docker-image-build.log.
3. C:\Codeproof-mvp-audit-worktree\backend\.venv\Scripts\python.exe setup-evidence/docker_validation_probe.py — Python exit 1; docker-validation-probe.log and docker-validation-runtime.json.
4. Same Python setup-evidence/docker_validation_probe_v2.py — Python exit 0; docker-validation-probe-v2.log and docker-validation-runtime-v2.json.
5. Same Python -m pytest backend/tests -q -p no:cacheprovider --basetemp=C:\Codeproof-fix-ai-setup\.pytest-tmp-docker-backend --junitxml=setup-evidence/docker-backend-tests.xml — exit 0; docker-backend-tests.log and XML.
6. Same Python setup-evidence/docker_validation_additional.py — harness exit 0 (records outcomes, does not require dummy tests to pass); dummy pytest inside container exit 2. docker-validation-additional.log and docker-validation-additional.json.
7. docker ps -a --filter name=codeproof- --format '{{.Names}} {{.Status}}' — exit 0, no matching containers after runs.

Image ID: sha256:2625fdcd45d0636bbb5aa97521e89a3f48c2a047cec9333dfb9522b40b82cb5f. Build from sandbox/Dockerfile; base resolved python:3.12-slim digest f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f. Build warnings: pip as root during trusted image construction and pip update notice. Runtime executes as non-root.

Backend warnings: deprecated google.generativeai package; Starlette httpx test-client deprecation; datetime.utcnow deprecations. No test failure or skip remains in this backend run. Existing regression mocks do not constitute live provider evidence.

FILES CREATED/CHANGED: setup-evidence/docker-image-build.log, docker_validation_probe.py, docker_validation_probe_v2.py, docker_validation_additional.py, their logs and JSON results, docker-backend-tests.log/XML, this report, harmless fixture directories and generated pytest temporary data. No application source/config edited.

ARCHITECTURE IMPACT: None.
API IMPACT: None.
DATA MODEL IMPACT: None.
SECURITY IMPACT: Real evidence supports isolation, failure/timeout gating, cleanup and original preservation for tested runs. Guardian filename exclusion issue remains. No live AI calls or raw dummy secret-bearing logs retained.
TESTS: Results in matrix above. Transparent audit inspection wrappers called original Docker SDK methods; no fake engine responses were used.
KNOWN ISSUES: Dummy collection failure; Guardian substring exclusions; existing deprecation warnings; untested full desktop/provider journey; no resource-exhaustion or live output-cap stress test.
NEXT DEPENDENCY: Backend/Sandbox Lead and Project Lead must agree on controlled test import layout and dependencies before the dummy validation journey can pass. Project Lead should correct scanner false positives in a separate scoped change. No fixes made here.
