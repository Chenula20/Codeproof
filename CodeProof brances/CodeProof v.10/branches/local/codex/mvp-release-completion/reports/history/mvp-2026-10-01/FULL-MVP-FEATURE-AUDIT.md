Historical initial audit (2026-10-01), before later fixes. Read [the latest release audit](../../p06-p15/FULL-MVP-RELEASE-AUDIT.md) for current results. Prior missing/deprecated/unavailable findings below are historical evidence, not a claim that the fixes are absent.

# FULL CodeProof MVP FEATURE AUDIT

Date: 2026-10-01 (Asia/Colombo)
Audit worktree: C:\Codeproof-mvp-audit-worktree
Branch: test/mvp-integration
Integrated HEAD: 911d45cc267d8972dd7b65d6cf260bd6e7a779db
External test target: C:\New folder\CodeProof-DummyApp
Verdict: Full connected MVP flow is NOT verified and is not ready for release sign-off from this audit. Inspection and safe-copy patch protections work in the tested scope. Live AI and Docker prerequisites are unavailable; connected native UI verification was interrupted by minimized-window/user-input guards. No application fixes were made.

## Final assessment and evidence rules

This consolidates setup, automated-check and runtime evidence collected in this chat. Full connected MVP release sign-off is blocked. Exactly 18 features are assessed below: 1 PASS, 6 PARTIAL, 11 NOT TESTABLE, 0 MISSING, 0 BROKEN. PASS is scoped to exercised behavior, not inferred from source or simulation. NOT TESTABLE denotes unexecuted or gated live checks, not an established application failure.

ORIGINAL CHECKOUT: UNTOUCHED within the recorded baseline: all 253 tracked/protected SHA256 entries, original HEAD and index match. This covers protected desktop/.dart_tool/, desktop/codeproof_desktop.iml and desktop/windows/. Pre-existing C:\Codeproof-mvp-audit was preserved and unused.
AUDIT WORKTREE: C:\Codeproof-mvp-audit-worktree
AUDIT BRANCH: test/mvp-integration
FETCH RESULT: elevated git fetch origin --prune succeeded; no stale refs used. Earlier non-elevated fetch failed: error: cannot open '.git/FETCH_HEAD': Permission denied.
BASE origin/main: 6efa548ab78a2b93075a395b777b2fe30206f403
BACKEND MERGE RESULT: clean fast-forward to 2874de18cfa1ed9fabbf04fa4f3b9af694e895a4
FLUTTER MERGE RESULT: clean merge of e8ebf7c657db5379b98a384c947250e8096499db
INTEGRATED HEAD: 911d45cc267d8972dd7b65d6cf260bd6e7a779db

Both feature heads are ancestors of integrated HEAD. No main/teammate branch was changed. Merge identity was command-scoped. No application fixes, pushes or merges into main occurred.

Final process verification: ZERO audit-owned runtime processes currently running. The audit backend was previously stopped after command/parent verification and its private pairing-token file removed. The previously observed audit desktop has since exited; its historic PID was reused by an unrelated process, which was not touched. Earlier reports saying the desktop was left open describe the earlier observation, not final state. See final-state-verification.json.

Read root AGENTS.md and root/backend/desktop/ai/workspace setup READMEs; no additional AGENTS.md was found. Worktree Python 3.12.14 virtual environment and backend/requirements-dev.txt installation succeeded. Flutter 3.47.5/Dart 3.13.4 were used. Trusted repository tests/builds ran only in the audit worktree. External dummy code was not executed on the host.

## Results

| Check | Passed | Failed | Errors | Skipped | Warnings | Exit |
|---|---:|---:|---:|---:|---:|---:|
| Backend first attempt | 52 | 0 | 48 | 0 | 40 | 1 |
| Backend retry with isolated temporary directory | 99 | 0 | 0 | 1 | 274 | 0 |
| Project-wide Python suite | 141 | 0 | 0 | 0 | 146 | 0 |
| Flutter tests | 7 | 0 | 0 | 0 | No test warning reported; dependency notices noted below | 0 |

Backend first-attempt errors were fixture setup errors: PermissionError [WinError 5] accessing C:\Users\binuj\AppData\Local\Temp\pytest-of-binuj. No test source or contracts were changed. Retried the complete backend suite with --basetemp pointing to a new, previously absent directory inside audit-evidence. Both attempts and their JUnit XML are retained; the failed attempt is not discarded.

The single backend skip is test_real_docker_when_available, with reason: "Docker is not installed; real container validation unavailable". This is the test's PATH-based availability check; it does not establish whether a Docker installation exists elsewhere on disk. Live Docker behavior remains NOT TESTABLE in this environment.

Flutter pub get exited 0. Flutter analyze exited 0 and reported "No issues found!" (29.2 seconds). Flutter tests exited 0 with all seven passing. flutter build windows exited 0 and produced desktop/build/windows/x64/runner/Release/codeproof_desktop.exe; the build reported 54.6 seconds. Artifact size and SHA256 are recorded in windows-build-artifact.json. The executable was subsequently launched: the real startup shell was observed in the runtime phase below.

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

Flutter tests cover the in-memory practice workflow, responsive layouts, navigation, controller errors and pairing-dialog validation. They do not exercise LocalWorkspaceService against the integrated backend; a separate real Dart runtime harness subsequently did. A successful Windows build is not evidence of successful native application startup.


## Repository and integration state

The elevated fetch succeeded earlier in this session. Backend 2874de1 merged by fast-forward from main 6efa548. Flutter e8ebf7c merged cleanly into audit commit 911d45c. Both feature heads were verified as ancestors. No main/teammate branches were changed or pushed. This phase used only the separate audit worktree for execution and evidence; original repositories were not used as execution directories.

Original checkout: recorded 253 tracked/protected file hashes, HEAD and Git index remain unchanged. Pre-existing C:\Codeproof-mvp-audit repository was preserved and not used. The evidence scope does not claim to hash every unrelated ignored file on the PC.

## Backend startup and API inventory

Started a new audit-owned backend from this worktree using the intended backend/.venv/Scripts/python.exe -u -m backend launcher on free loopback port 8010. The launcher generated a token. A wrapper kept it in a private temporary file under the audit virtual environment and redacted its startup line from logs. No token/API-key values are in this report.

GET /health returned HTTP 200 with healthy/codeproof-backend/version 1.0.0. Saved runtime-health.json. GET /openapi.json returned HTTP 200. Saved full schema as runtime-openapi.json and all 35 method/path operations as runtime-routes.json.

Available routes:

| Method | Route |
|---|---|
| GET | /project |
| GET | /analysis |
| GET | /skills |
| GET | /challenges |
| GET | /challenges/{challenge_id} |
| POST | /challenges/{challenge_id}/hint |
| POST | /challenges/{challenge_id}/explanation |
| POST | /patch/validate |
| POST | /sandbox/run |
| GET, POST | /release-readiness |
| POST | /v1/sessions |
| DELETE | /v1/sessions/{session_id} |
| POST | /v1/sessions/{session_id}/analysis |
| POST | /v1/sessions/{session_id}/challenge |
| POST | /v1/sessions/{session_id}/hint |
| POST | /v1/sessions/{session_id}/explanation |
| POST | /v1/sessions/{session_id}/patch |
| POST | /v1/sessions/{session_id}/validation |
| GET | /v1/sessions/{session_id}/report |
| GET | /demo/overview |
| GET | /demo/skill-map |
| GET | /demo/files |
| GET | /demo/file |
| POST | /demo/challenge/start |
| GET | /demo/challenge |
| POST | /demo/hint |
| POST | /demo/explanation |
| GET | /demo/patch |
| POST | /demo/patch/apply |
| POST | /demo/validation |
| GET | /demo/release-readiness |
| GET | /demo/state |
| POST | /demo/reset |
| GET | /health |

Unversioned endpoints are legacy/demo services; /demo is explicit in-memory simulation; /v1 is the connected project interface. Route existence alone is not a feature PASS.

## Native desktop observations

Launched the integrated release executable from desktop/build/windows/x64/runner/Release/codeproof_desktop.exe. Native process PID 12964 was verified to belong to this exact audit build. Computer Use eventually discovered its returned window titled CodeProof and captured the real startup shell. Observed the branding, protection banner, Open sample project and Connect your project controls. The process remained responding with a native window; no immediate crash was observed.

A prior turn's Computer Use was stopped by physical Escape, then resumed with user authorization. Later attempts to continue input encountered the exact guards:

- "verify current window before using captured target: window is minimized; call activate_window, refresh with get_window, then retry get_window_state"
- "user input was detected in this window; call get_window_state before continuing"
- "window is minimized; call activate_window, refresh with get_window, then retry get_window_state"

Recovery and refreshed observations did not yield a usable connection-dialog state. No input was sent using guessed coordinates or forged window handles. A node-side attempt to save an observation also hit EPERM in the audit folder; the failing call stopped before its planned click. These are audit tooling/input limitations, not evidence of an application bug.

Native folder selection, subsequent workspace navigation, AI analysis controls, investigation, patch-review UI, sandbox results UI and readiness UI require manual verification or a quiet, unminimized audit window in a later run. The full native UI journey did not reach confirmed project selection.

## Real connected backend/Dart journey

The target was found after the user supplied C:\New folder. Before opening it, recorded SHA256 for all 6,398 files, including its pre-existing venv; zero read errors. No files were created, moved, patched or executed in the external target.

Ran the actual desktop LocalWorkspaceService via an audit-only Dart harness against the live backend. No HTTP/provider transport mocks were injected. It opened the external path, parsed WorkspaceData successfully, obtained 23 snapshot files including backend/auth.py, excluded venv/, and closed its session. Mode was Local backend, provider Local inspection, skills count zero. The harness uses the real shipped Dart client, but does not substitute for native selection/UI evidence.

Independent real HTTP probes produced:

| Step | Outcome |
|---|---|
| Open external project | HTTP 200; 23 filtered source/config/test files |
| Analyze with use_ai=true | HTTP 503: Configure OPENROUTER_API_KEY and CODEPROOF_MODEL to enable AI. |
| Start authentication investigation | HTTP 409: Enable AI analysis before project investigation |
| Hint requests 1, 2, 3, 4 | All HTTP 409; HintEngine was not reached |
| Incorrect explanation | HTTP 409: Start an investigation first |
| Partially correct candidate | HTTP 409: Start an investigation first |
| Well-supported candidate based on target source | HTTP 409: Start an investigation first |
| Apply proposed patch | HTTP 409: A passed explanation and reviewed patch are required |
| Docker validation capability probe | HTTP 200 containing validation.status=unavailable; actual SDK path was attempted without mocks |
| Readiness report | HTTP 200, readiness=BLOCKED, original_unchanged=true |
| Close session | HTTP 200 |

Exact first backend/Dart journey failure: Analyze, due to missing provider key and model environment variables. Both were checked only for presence, not printed. Later calls were explicit gate/capability probes after the journey had already failed, not a successful continuation.

The selected external auth.py already uses password verification through its hashing library. It is not the bundled demo's plaintext-vs-hash login bug. The audit did not invent that root cause for this different target. Candidate explanations were not evaluated by the live evaluator, so no candidate is claimed to be AI-certified correct.

## Safe Patch Lab runtime checks

Initial legacy /patch/validate probes accidentally omitted required challenge_id and received HTTP 422. That result did not establish path enforcement. The initial records are preserved in runtime-api-steps.json. Corrected audit-only request bodies then returned HTTP 200/valid=false for absolute paths, ../ traversal and unknown files.

Ran actual Patch Lab functions against harmless disposable fixtures, without mocks:

- Rejected an absolute path to a sentinel.
- Rejected ../ traversal.
- Rejected unknown files.
- Rejected applying a patch to an unregistered original/fixture directory.
- Applied a valid diff only to a registered temporary copy.
- External sentinel bytes stayed unchanged.
- Removed the managed temporary copy after the probe.

Evidence: runtime-patch-safety.json and runtime-patch-probe.log. This establishes the exercised Patch Lab operations. The AI-generated patch flow against the external dummy remains untested because no proposal was available.

## Docker and test execution

Docker was not available on PATH and its standard installation path checked during preparation was absent. The real connected validation request returned unavailable: "Docker or the prebuilt sandbox image is unavailable." No successful container launch, test execution, timeout or container destruction was observed.

Mark Docker, actual target test runner and container-isolation runtime checks NOT TESTABLE. No real tests_total/tests_passed/tests_failed values are available for the external target. Counts in the separate automated suite or simulated demo are not external-target container results.

Source inspection and previously passing mocked Docker tests show read-only snapshot mounts, non-root, no network, CPU/memory/PID/time/output limits and finally cleanup. They are not a live isolation PASS. The server failed closed: real readiness stayed BLOCKED. Successful READY behavior with real Docker remains unverified.

## Explicit mock/demo runtime audit

Separately exercised /demo on the audit-owned backend. All 16 requests returned HTTP 200. Four hints were served. The keyword-driven evaluator returned INCORRECT, PARTIALLY_CORRECT and CORRECT for the three demo-oriented inputs. Static proposal/review data and in-memory patch application worked. Validation returned simulated=true with three simulated passed tests; readiness returned simulated=true and READY_FOR_REVIEW. Reset the audit-only fixture state afterwards.

Evidence: runtime-demo-only.json. These responses prove the explicitly demo-only API works, not that HintEngine, ExplanationEvaluator, PatchGenerator or Docker produced those results.

Mock locations:

- desktop/lib/services/practice_service.dart: static sample analysis and skill estimates, curated four hints, keyword pass/fail explanation scoring, static diff, in-memory mutation and simulated validation/readiness. Source and prior Flutter tests identify this path; native practice UI was not re-run in this phase. UI source labels practice coaching and no Docker/project test execution.
- backend/services/demo_fixtures.py and /demo: hard-coded analysis/skill estimates, fixed challenge/hints/diff, keyword three-way classification and simulated tests/readiness. Observed through real HTTP with simulated=true.
- backend/services/challenge_service.py and project_service.py: legacy static coaching/skill scores. Not evidence of connected AI operation.
- backend/tests/test_sessions.py and test_sandbox_safety.py: provider transport/Docker lifecycle mocks in the earlier automated suite; distinguished from this phase's real HTTP prerequisite failures.

## Guardian secret filtering finding

A read-only check through the actual Guardian adapter confirmed the selected target's hardcoded JWT signing-secret assignment survives content redaction in backend/auth.py. Saved only a boolean in runtime-secret-filter-check.json; no secret value was included. The source key is hardcoded by the target, and CodeProof currently fails to remove it from the snapshot. No provider transmission occurred because AI configuration was missing.

This is a confidentiality blocker before enabling live AI on this target. Owner: Project Lead for Guardian/SecretFilter, with Backend + Sandbox Lead for adapter integration. It does not demonstrate original-project modification. .env filtering and linked-path protection tests passed in the earlier suite, but do not cover this surviving signing secret.

## Original-project comparison

After the attempted real flow and safe/demo probes, hashed the target again. Before: 6,398 files. After: 6,398 files. Added: 0. Removed: 0. Changed SHA256: 0. Read errors: 0. ORIGINAL PROJECT UNCHANGED for the operations actually attempted.

Evidence: dummy-hashes-before.json, dummy-hashes-after.json and runtime-original-comparison.json. The full protection requirement is PARTIAL: a successful live AI proposal/application/Docker flow was not reached. Do not treat unchanged files during a blocked journey as proof of the entire successful journey.

## MVP matrix

Owner abbreviations: Lead = Project Lead (AI/Guardian/integration); Flutter = Flutter Desktop Lead; Backend = Backend + Sandbox Lead; Product = UI/Product Developer. Blocker means missing verification or behavior needed for full connected MVP sign-off, not necessarily a proven regression.

| Feature | Status | Evidence | Real or mock | Blocker? | Owner |
|---|---|---|---|---|---|
| MVP-01 Windows desktop | PARTIAL | Real startup shell captured; responding audit process; navigation not verified | Real native | Yes: native journey incomplete | Flutter |
| MVP-02 Open/select project | PARTIAL | Real Dart client/API opened external path; native dialog selection not completed | Real client/API | Yes: native selection evidence | Flutter / Backend |
| MVP-03 Workspace Guardian | PARTIAL | 23 real snapshot files; venv excluded; signing secret survives redaction | Real Guardian | Yes: confidentiality gap | Lead / Backend |
| MVP-04 Project analysis | NOT TESTABLE | Live analysis HTTP 503; no key/model | Real service gate; demo analysis static | Yes: prerequisites | Lead / Backend |
| MVP-05 Engineering skill map | NOT TESTABLE | Connected skills empty; AI analysis blocked; demo map static | Live data unavailable / demo mock | Yes | Lead / Flutter |
| MVP-06 Controlled challenge | PARTIAL | Demo in-memory incident works; connected challenge HTTP 409; three real incidents not demonstrated | Demo mock / live gate | Yes | Backend / Product |
| MVP-07 Investigation workspace | NOT TESTABLE | Connected challenge/UI not reached; source snapshot available via client | Real files; workspace unverified | Yes | Flutter / Product / Backend |
| MVP-08 Progressive AI hints | NOT TESTABLE | All four connected requests HTTP 409; four demo hints are curated | Real gate / demo mock | Yes | Lead / Backend |
| MVP-09 Explain before fix | NOT TESTABLE | Three connected explanation submissions HTTP 409; evaluator not reached | Real gate / demo mock | Yes | Lead / Flutter / Backend |
| MVP-10 Explanation evaluation | NOT TESTABLE | Live evaluator blocked; three classifications observed only in keyword demo | Demo mock only | Yes | Lead / Backend |
| MVP-11 AI patch generation | NOT TESTABLE | No live AI proposal available; demo proposal static | Demo mock only | Yes | Lead |
| MVP-12 Patch review UI | NOT TESTABLE | No live proposal or verified native review | Static demo data / prior practice tests | Yes | Flutter / Product |
| MVP-13 Patch Lab | PASS | Real fixture application changes only managed copy; unsafe/original paths rejected; cleanup observed | Real subsystem, safe fixtures | No for tested subsystem; target AI flow pending | Backend |
| MVP-14 Docker sandbox | NOT TESTABLE | Real request returns unavailable; no successful container | Real availability check / prior mocked lifecycle | Yes: prerequisites | Backend |
| MVP-15 Automated target test runner | NOT TESTABLE | No target Docker tests executed; no actual result counts | Demo counts simulated | Yes | Backend |
| MVP-16 Sandbox results UI | NOT TESTABLE | Native results screen not reached | Demo simulated / prior practice tests | Yes | Flutter / Product |
| MVP-17 Release readiness | PARTIAL | Real backend reports BLOCKED for unavailable validation; successful real READY not tested | Real fail-closed / demo mock READY | Yes: successful flow unverified | Backend / Flutter |
| MVP-18 Original protection | PARTIAL | All 6,398 hashes unchanged for attempted flow; complete successful flow not reached | Real SHA256 comparison | Yes: complete-flow proof pending | Lead / Backend |

## Architecture and release blockers

No prohibited direct Flutter-provider call, selected-project AI filesystem scan, original-project patch or original-mounted Docker execution was observed. Earlier source/tests verify the intended separation; this phase did not reach all components live. Snapshot secret redaction is a confirmed security gap, not an architectural rewrite.

Release blockers:

1. Surviving signing secret in AI-ready snapshot: address and verify confidentiality before live provider use on this target.
2. Missing OPENROUTER_API_KEY and CODEPROOF_MODEL in the audit backend environment.
3. Docker/trusted-image availability prevents real target validation.
4. Connected native selection/navigation/review/results verification remains incomplete due input/window guards.
5. Expected three controlled incidents and complete successful external-project before/after proof remain unverified. Connected investigation currently describes existing issues rather than injecting controlled failure copies.

Non-blocking/maintenance issues include deprecated google.generativeai/datetime.utcnow/TestClient integration warnings, stale desktop README, Flutter package update notices and generated-file line-ending/stat differences. Connected evaluation/count reporting gaps identified in the previous architecture report remain unresolved; no API contracts were changed.

What actually works now: Windows build and observed native startup; audit backend launcher/health/OpenAPI; real Dart session open/parse/close; filtered Guardian snapshot; live failure gates; safe fixture Patch Lab protections; real fail-closed BLOCKED result; explicit demo API practice sequence.

What remains missing or unverified: live AI analysis/skill map/coaching/evaluation/proposal; three controlled incidents against target copies; connected native interaction; real Docker target tests and result UI; successful readiness; complete successful-flow original protection. Do not confuse unknown runtime behavior with proven missing classes or application failure.

Next three tasks (no implementation performed here):

1. Project Lead: close the confirmed signing-secret redaction gap and verify sanitized provider context with a safe regression fixture.
2. Backend + Sandbox Lead: provision audit provider/model configuration and running Docker with the trusted image; preserve credentials outside evidence. Retest actual AI and container prerequisites.
3. Flutter/Product/Integration leads: complete the native connected journey in an unminimized window, clarify the three incident scope and missing response fields, and repeat complete-flow external hashes before release sign-off. Cross-component changes require the project's impact report/approval rules.


## Exact dependency, test and build commands

| Command | Working directory | Exit | Evidence log |
|---|---|---:|---|
| C:\Users\binuj\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m venv backend/.venv | C:\Codeproof-mvp-audit-worktree | 0 | python-venv.log |
| .\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements-dev.txt | C:\Codeproof-mvp-audit-worktree | 0 | python-dependencies.log |
| .\backend\.venv\Scripts\python.exe -m pytest backend/tests -q --junitxml=audit-evidence/backend-tests.xml | C:\Codeproof-mvp-audit-worktree | 1 | backend-tests.log |
| .\backend\.venv\Scripts\python.exe -m pytest backend/tests -q --tb=short --basetemp=C:\Codeproof-mvp-audit-worktree\audit-evidence\pytest-temp-backend-run2 --junitxml=audit-evidence/backend-tests-retry.xml | C:\Codeproof-mvp-audit-worktree | 0 | backend-tests-retry.log |
| .\backend\.venv\Scripts\python.exe -m pytest tests/ --tb=short -q --junitxml=audit-evidence/project-tests.xml | C:\Codeproof-mvp-audit-worktree | 0 | project-tests.log |
| C:\flutter\bin\flutter.bat pub get | C:\Codeproof-mvp-audit-worktree\desktop | 0 | flutter-pub-get.log |
| C:\flutter\bin\flutter.bat analyze | C:\Codeproof-mvp-audit-worktree\desktop | 0 | flutter-analyze.log |
| C:\flutter\bin\flutter.bat test --reporter expanded | C:\Codeproof-mvp-audit-worktree\desktop | 0 | flutter-test.log |
| C:\flutter\bin\flutter.bat build windows | C:\Codeproof-mvp-audit-worktree\desktop | 0 | flutter-build-windows.log |

## Remaining reporting/setup issues

- Backend instructions imply .env loading, but the launcher reads process variables without explicit dotenv loading; .env.example omits CODEPROOF_MODEL. Owner: Backend.
- Connected Evaluation returns passed/feedback/score without explicit three-way classification. Connected Validation omits tests_total/tests_passed/tests_failed although SandboxResult has counts. Owners: Backend/Flutter; these are inspected reporting gaps, not successful live AI/container results.
- The external target already uses password verification. Do not attribute the bundled demo credential mismatch to it.
- No prohibited cross-component bypass was found in inspected paths. The confirmed signing-secret redaction gap is a confidentiality violation requiring remediation before live AI use. Docker isolation, limits, timeout and cleanup remain source/mocked-test evidence.

## Evidence index

All listed evidence resides in C:\Codeproof-mvp-audit-worktree\audit-evidence. Reports exclude pairing tokens and API-key values.

| Evidence | Purpose |
|---|---|
| original-checkout-baseline.json; setup-verification.json | Preservation baseline and integration setup |
| checks-preservation.json; runtime-checkout-preservation.json; final-state-verification.json | Preservation across stages and final branch/process state |
| checks-commands.json; python-installed-packages.txt | Exact commands, exits and resolved dependencies |
| backend-tests*.log/xml; project-tests.log/xml | Initial setup errors, full retry, counts/skips/warnings |
| flutter-pub-get.log; flutter-analyze.log; flutter-test.log; flutter-build-windows.log | Flutter results |
| windows-build-artifact.json | Build metadata; its pre-runtime Executed field is historical |
| architecture-source-evidence.txt | Component boundary inspection |
| runtime-health.json; runtime-openapi.json; runtime-routes.json | Actual health and full 35-operation inventory |
| runtime-dart-client.log; runtime-api-steps.json | Real Dart service and connected endpoint probes |
| runtime-patch-safety.json; runtime-patch-probe.log | Actual safe-copy application/path rejection |
| runtime-demo-only.json | Explicitly simulated demo journey |
| runtime-secret-filter-check.json | Boolean signing-secret filtering evidence |
| dummy-hashes-before.json; dummy-hashes-after.json; runtime-original-comparison.json | 6,398 files; zero changes/additions/removals |
| runtime-backend-cleanup.json | Verified backend cleanup/token removal |
| RUNTIME-MVP-MATRIX.csv | Machine-readable 18-feature matrix |
| ARCHITECTURE-AND-CHECKS-REPORT.md; RUNTIME-AUDIT-REPORT.md | Historical stage reports; this final report supersedes their process observations |

TASK: Consolidate FULL integration-only MVP audit.
IMPLEMENTED: Final report and evidence consolidation only.
FILES CREATED/CHANGED: FULL-MVP-FEATURE-AUDIT.md and final-state-verification.json; prior worktree-only evidence, dependencies and Flutter generated/build artifacts retained.
ARCHITECTURE IMPACT: None introduced.
API IMPACT: None introduced.
DATA MODEL IMPACT: None introduced.
SECURITY IMPACT: Recorded checkout and dummy hashes unchanged; redaction gap reported; no live provider transmission.
TESTS: Previously executed suites/probes summarized above; no unnecessary reruns for this report.
KNOWN ISSUES: Release blockers, maintenance/setup/reporting gaps and incomplete live/native verification above.
NEXT DEPENDENCY: Lead redaction remediation, Backend prerequisite provisioning, then coordinated native/AI/Docker journey verification.
PROCESSES: Zero audit-owned runtime processes at final verification; no user-owned processes stopped.

No product fix, protected-folder cleanup/reset/stash, audit-output commit, push, worktree removal or merge into main was performed.
