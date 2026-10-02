Historical initial audit (2026-10-01), before later fixes. Read [the latest release audit](../../p06-p15/FULL-MVP-RELEASE-AUDIT.md) for current results. Prior missing/deprecated/unavailable findings below are historical evidence, not a claim that the fixes are absent.

# CodeProof MVP audit: architecture and automated checks

Date: 2026-10-01 (Asia/Colombo)
Scope: integration audit only; stops before the desktop runtime journey.
Audit worktree: C:\Codeproof-mvp-audit-worktree
Branch: test/mvp-integration
Integrated commit: 911d45cc267d8972dd7b65d6cf260bd6e7a779db

## Integration and setup

Both fetched feature heads are ancestors of the integrated commit (Git exit 0 for each): backend 2874de18cfa1ed9fabbf04fa4f3b9af694e895a4 and Flutter e8ebf7c657db5379b98a384c947250e8096499db. The backend merge was a fast-forward and Flutter merged cleanly. No merges were performed in this audit phase.

Read root AGENTS.md, root README.md, backend/README.md, desktop/README.md, ai/README.md and workspace/README.md. Only root AGENTS.md was discovered in the audit worktree. The user's explicit permission authorizes trusted repository tests/builds on the host for this audit; target project execution through CodeProof remains Docker-only.

Created backend/.venv using Python 3.12.14 and installed backend/requirements-dev.txt. Installation exited 0. Exact resolved versions are in python-installed-packages.txt. Flutter 3.47.5, Dart 3.13.4. No global Python environment installation or application source fixes were performed.

## Results

| Check | Passed | Failed | Errors | Skipped | Warnings | Exit |
|---|---:|---:|---:|---:|---:|---:|
| Backend first attempt | 52 | 0 | 48 | 0 | 40 | 1 |
| Backend retry with isolated temporary directory | 99 | 0 | 0 | 1 | 274 | 0 |
| Project-wide Python suite | 141 | 0 | 0 | 0 | 146 | 0 |
| Flutter tests | 7 | 0 | 0 | 0 | No test warning reported; dependency notices noted below | 0 |

Backend first-attempt errors were fixture setup errors: PermissionError [WinError 5] accessing C:\Users\binuj\AppData\Local\Temp\pytest-of-binuj. No test source or contracts were changed. Retried the complete backend suite with --basetemp pointing to a new, previously absent directory inside audit-evidence. Both attempts and their JUnit XML are retained; the failed attempt is not discarded.

The single backend skip is test_real_docker_when_available, with reason: "Docker is not installed; real container validation unavailable". This is the test's PATH-based availability check; it does not establish whether a Docker installation exists elsewhere on disk. Live Docker behavior remains NOT TESTABLE in this environment.

Flutter pub get exited 0. Flutter analyze exited 0 and reported "No issues found!" (29.2 seconds). Flutter tests exited 0 with all seven passing. flutter build windows exited 0 and produced desktop/build/windows/x64/runner/Release/codeproof_desktop.exe; the build reported 54.6 seconds. Artifact size and SHA256 are recorded in windows-build-artifact.json. The executable has NOT been launched.

Exact commands, working directories, exit codes, and log names are in checks-commands.json. Python commands used the intended worktree virtual environment. Flutter commands ran from desktop/. The JUnit flags and expanded Flutter reporter only add evidence; no test selection was reduced.

## Warnings and notices

- Deprecated google.generativeai import: FutureWarning states its support has ended. This is a maintenance issue; no migration performed.
- datetime.utcnow deprecation warnings emitted through Pydantic model creation.
- Starlette TestClient deprecation warning for httpx; no dependency substitution performed.
- Flutter dependency resolution reports four newer package versions incompatible with the current constraints. This is a notice, not an analysis/build failure.
- pip upgrade notice; pip was not upgraded.
- Git warns that LF may become CRLF for Flutter-generated plugin files.

## Architecture inspection

The practical connected sequence is Flutter loopback HTTP client -> FastAPI session router -> Guardian snapshot -> AI services -> managed Patch Lab copy -> Docker runner -> readiness evaluation. This is the inspected implementation sequence; no architecture change was made. Guardian is used within the backend before AI consumption.

| Prohibited behavior | Finding | Evidence and limits |
|---|---|---|
| Flutter calls Gemini/OpenRouter directly | Not found in inspected application source | LocalWorkspaceService sends requests only to 127.0.0.1; bearer token; redirects disabled. No provider SDK/API-key or provider endpoint use found in desktop/lib. |
| AI directly reads selected-project files | Not found in inspected connected path | Services consume ProjectSnapshot and coaching models. PatchGenerator contains a local read helper for bundled ai/prompts templates; it is not a selected-project scan. |
| CodeProof writes original projects | Not found in inspected connected path | Guardian reads originals. Session open materializes a disposable copy; patch operation uses session.copy. Original-path rejection and fixture preservation assertions passed. This is not the full external dummy-app before/after proof. |
| Backend AI analysis bypasses Guardian | Not found in inspected connected path | open_session calls open_guardian and capture before ProjectAnalyzer. ControlledBuilder routes content reads through guardian.read_file; containment-aware scanner rejects links. Snapshot root is replaced with guardian-snapshot before provider use. |
| Patch writes outside managed copies | Not found in inspected path; safety tests passed | Patch Lab registry, manifest integrity checks, contained_path checks, and strict diff allowed-file checks. Tests cover absolute paths, traversal, unknown files, original paths, symlinks, hard links, Windows junctions, redirected owner directories, and stale/tampered copies. |
| Sandbox executes directly against originals | Not found in inspected implementation; real Docker unverified | run_managed_copy accepts managed copies, rematerializes a fresh manifest, mounts that copy read-only, and copies into container tmpfs. Fixed runner commands; no network; non-root; CPU/memory/PID/time/output limits; cleanup in finally. Docker lifecycle assertions use mocks. |

Source references are saved in architecture-source-evidence.txt. Relevant files include desktop/lib/services/workspace_service.dart, backend/services/guardian.py, sessions.py, patch_lab.py, diff.py, sandbox.py and release_readiness.py.

No requested prohibited architecture flow was found in the examined source and tests. This conclusion is scoped to those boundaries; it is not a comprehensive security certification or a live end-to-end PASS.

## Test evidence versus runtime evidence

Backend session tests execute real Guardian, AI service classes, Patch Lab and HTTP routers through both TestClient and actual Uvicorn TCP. External provider transport is mocked, and Docker calls are mocked. They check four hint levels, explanation gating, patching only a disposable copy, redaction, readiness blocking after an external fixture edit, and cleanup. They do not validate live model response quality or live container behavior.

Flutter tests cover the in-memory practice workflow, responsive layouts, navigation, controller errors and pairing-dialog validation. They do not exercise LocalWorkspaceService against the integrated backend. A successful Windows build is not evidence of successful native application startup.

## Findings to carry into the runtime phase

- Docker's real-container test is skipped: container execution, runtime isolation and lifecycle remain unverified.
- Live provider responses and full desktop/backend integration are untested in this phase.
- PracticeWorkspaceService, backend demo_fixtures and legacy challenge services contain curated/static/simulated data. The practice service explicitly labels no project tests/Docker execution and non-AI coaching. Connected /v1 sessions use separate real service classes. A complete running-UI mock audit is pending.
- desktop/README.md is stale: it claims no backend integration, navigation, typed models or implemented workflows despite their presence in the integrated source. Owner: Flutter Desktop Lead.
- Connected challenge creation describes an issue and chooses a file; it does not inject the three expected controlled demo incidents. Practice mode provides an in-memory credential mismatch. Runtime feature evaluation must distinguish these behaviors. Owners: Backend + Sandbox Lead and UI/Product Developer.
- Connected Evaluation exposes passed, feedback and score, without the requested explicit three-way classification field. Connected Validation omits tests_total/tests_passed/tests_failed even though SandboxResult computes counts. These are feature/API reporting gaps to evaluate, not changes made during this audit. Owners: Backend + Sandbox Lead and Flutter Desktop Lead.
- Environment documentation says to set keys in .env, but the backend reads process variables without explicit dotenv loading. .env.example omits CODEPROOF_MODEL, required by configured_provider. This can block live AI setup. Owner: Backend + Sandbox Lead.

## Preservation and generated artifacts

Original checkout HEAD and Git index hash match the baseline. All 253 recorded tracked/protected file hashes match, and the protected desktop/.dart_tool and desktop/windows filename lists have zero differences. Evidence: checks-preservation.json and original-checkout-baseline.json. This verifies the recorded scope, not every unrelated ignored file on the machine.

No application source differences were found under ai/, workspace/, backend/, desktop/lib or desktop/test (git diff exit 0). Flutter rewrote generated plugin registrant files inside the AUDIT worktree; Git status flags three generated paths. Git's normalized diff had no content changes. These generated outputs were preserved, without resetting or committing them. New audit evidence and the isolated Python environment/build/cache outputs remain local.

The pre-existing C:\Codeproof-mvp-audit independent repository was not used or modified. No pushes, main/teammate branch changes, code fixes, or user-process interruptions were performed. No persistent audit backend or desktop runtime process was started; test-owned ephemeral HTTP servers were part of the completed suite.

## Required task report

TASK: Integrated architecture inspection, dependency setup and specified automated checks.
IMPLEMENTED: Audit evidence and report only; no product implementation.
FILES CREATED/CHANGED: audit-evidence logs/XML/JSON/report; backend/.venv; generated Flutter cache/build/preview/plugin artifacts within audit worktree.
ARCHITECTURE IMPACT: None introduced.
API IMPACT: None introduced; observed reporting gaps listed above.
DATA MODEL IMPACT: None introduced.
SECURITY IMPACT: Original preservation and copy-boundary regression tests passed; live Docker/dummy-project protection remains unverified.
TESTS: Counts, warnings and both backend attempts recorded above.
KNOWN ISSUES: Docker unavailability, maintenance warnings, stale setup documentation, and runtime/feature checks pending.
NEXT DEPENDENCY: Start a separate runtime audit against the external dummy app, with available provider configuration and Docker prerequisites. Do not infer a full MVP release verdict from these automated checks alone.

Stopped before runtime journey, as requested. No final 18-feature runtime matrix is claimed in this phase.
