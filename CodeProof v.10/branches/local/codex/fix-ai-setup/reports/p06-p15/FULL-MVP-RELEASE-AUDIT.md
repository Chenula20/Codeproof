Publication note: this records the audit state before the later user-authorized commit/push. See MERGE-REPORT.md for publication scope and current Git state.

# CodeProof full project and P06–P15 release audit

Date: 2026-10-02, Asia/Colombo. Fresh results supersede the original audit where checks were repeated; historical failures remain in prior evidence.

The Windows app builds and launches. Implemented safety, explanation gates, controlled incidents, managed patching, Docker and readiness pass their exercised checks. Full connected MVP release sign-off remains blocked: private live AI configuration is incomplete, connected native interaction is unverified, and the separate dummy has incompatible test layout/dependencies. This report does not claim every possible bug or model-quality issue is fixed.

## Delivery and preservation

- ORIGINAL CHECKOUT: **UNTOUCHED in the recorded scope**. All 253 tracked/protected baseline hashes, HEAD and index match, including desktop/.dart_tool/, desktop/codeproof_desktop.iml and desktop/windows/. Unrelated ignored files were not exhaustively inventoried.
- Original HEAD: 2874de18cfa1ed9fabbf04fa4f3b9af694e895a4. Index SHA256: EE5FAD670F85390FDBB926B940E83E0EF66C9C21BA3A44256E26C3230279544E.
- External dummy: C:\New folder\CodeProof-DummyApp. **6,398 files before and after; zero changes/additions/removals**. No target code executed on the host.
- C:\Codeproof-mvp-audit and C:\Codeproof-mvp-audit-worktree preserved; neither was cleaned/reset/stashed or used for new source writes. Historical evidence read/copied only.
- Fix source: **C:\Codeproof-fix-ai-setup**, branch codex/fix-ai-setup; fixes remain uncommitted.
- Fresh AUDIT WORKTREE: **C:\Codeproof-release-audit-p06-p15**.
- AUDIT BRANCH: **codex/release-audit-p06-p15**.
- Audit base/HEAD: **911d45cc267d8972dd7b65d6cf260bd6e7a779db**.
- Assembly: 62 approved changed/new source files copied by verified P15-ASSEMBLY-MANIFEST.json. Final source hashes match. No invented fix-branch merges/commits. Private .env, virtual environments and generated build trees were not copied as source.
- One extra EOF blank line was removed in the fix worktree requirements file and that file/hash explicitly reassembled. Dependency specifications unchanged.
- FETCH RESULT: earlier authorized elevated git fetch origin --prune **succeeded**. Initial sandbox attempt failed exactly: error: cannot open '.git/FETCH_HEAD': Permission denied. No new fetch performed in this final phase.
- Earlier origin/main: 6efa548ab78a2b93075a395b777b2fe30206f403.
- BACKEND MERGE RESULT: **clean fast-forward** to 2874de18cfa1ed9fabbf04fa4f3b9af694e895a4.
- FLUTTER MERGE RESULT: **clean merge** of e8ebf7c657db5379b98a384c947250e8096499db into integrated 911d45c. No automatic conflict resolution.
- No commits, pushes, main/teammate branch changes or merge into main. Generated Flutter files inside fix/audit worktrees remain uncommitted.

Preservation evidence: final-preservation.json, p06-p15-before.json, dummy-after-hashes.json and the original audit baseline.

## Complete checks

| Check | Pass | Fail | Error | Skip | Warnings | Exit |
|---|---:|---:|---:|---:|---:|---:|
| Backend Python suite | 249 | 0 | 0 | 0 | 0 | 0 |
| Project-wide Python suite | 228 | 0 | 0 | 0 | 0 | 0 |
| Flutter tests | 37 | 0 | 0 | 0 | No test warnings reported | 0 |
| Flutter pub get | Completed | — | — | — | Four dependency notices | 0 |
| Flutter analyze | No issues | 0 | — | — | 0 analyzer findings | 0 |
| Windows release build | Built; native launch observed | — | — | — | No build failure | 0 |
| Python pip check | No broken requirements | — | — | — | 0 | 0 |
| Final git diff --check | Clean | — | — | — | LF/CRLF notices | 0 |

Python 3.12.14; Flutter 3.47.5 / Dart 3.13.4. Python tests elevated DeprecationWarning/FutureWarning to errors; deprecated SDK/UTC/TestClient warnings are addressed without suppressing warning classes. Fresh dependency installation succeeded. FastAPI 0.142.2, application httpx 0.28.1, test-client httpx2 2.13.1 and google-genai 2.25.0; exact installed set in python-tested-requirements.txt. Pip's upgrade notice is informational.

Docker daemon and CLI were available for all 477 tests; zero Docker-availability skips. P06 includes nine actual baseline/injected/repaired container states. Initial failed regression attempts and unavailable-Docker attempts remain in fix-worktree evidence; final results do not erase them. XML/logs and exact invocation ledger are included.


## Implemented tasks and remaining work

| Task | Result | Limitation |
|---|---|---|
| P01 carried forward | Source/config signing literals redacted before provider serialization; synthetic interception and unchanged bytes pass. | Lexical detection limitations below. |
| P02 carried forward | Root-only .env load; process variables authoritative; interpolation disabled; nonsecret model example and safe actionable errors. | No usable private provider key/model pair available. |
| P03 freshly verified | Actual trusted Docker execution, isolation, limits, timeout and cleanup. | Target dependencies not installed automatically. |
| P04/F06 carried forward | CORRECT/PARTIALLY_CORRECT/INCORRECT with finite score/feedback. Patch requires CORRECT and score >=0.7; new explanation revokes old permission. | Live evaluator quality unmeasured. |
| P05/F07 carried forward | Nullable typed total/passed/failed/skipped counts across API/Dart/readiness; honest unknown and simulated labels. | Legacy scalar zeros are compatibility defaults when canonical counts are null. |
| P06 | Approved incident_id and typed incident metadata; three exact-manifest incidents in registered copies; transactional injection, contextual coaching and close/reopen restoration. 15 incident tests include nine actual Docker baseline/fail/repair states. | Only unchanged training-project is eligible; native/live flow pending. |
| P07 | Fresh native launch; real launcher health/auth/routes/dummy open/local inspection; real connected fixture patch/Docker/readiness flow. | Full native/live journey remains incomplete. |
| P08 | Gemini migrated to google-genai with model/settings/schema parsing, async timeout, one attempt, disabled automatic function calling, finite ordered embeddings and cleanup. Actual SDK HTTP transport fixtures pass. | Connected default stays OpenRouter. Live Gemini NOT TESTABLE. |
| P09 | UTC factories retain established naive-UTC timestamp serialization; compatible constrained TestClient dependencies; 477 tests warning-free. | No blanket upgrade or complete transitive vulnerability audit. |
| P10 | Correct setup and connected/practice documentation; accurate model/token/port/folder/Docker instructions; misleading hardcoded resource-limit UI claim removed. | Documentation is not live feature proof. |
| P11 | Exclusive loopback socket bound before printing token; actionable busy/invalid port, short/wrong token, unavailable backend, redirects and malformed response handling. | Matching successfully running service token/port remains required. |
| P12 | Consistent light/dark palettes, dialogs/code/diff/status, opt-in nonsecret native preference and supported titlebar colors. Contrast/widget journeys/previews pass; native build succeeds. | Native toggle/titlebar/persistence not confirmed due input guards. Appearance -> Light theme; Remember theme off for this session. |
| P13 | Four Flutter notices reviewed; tested lockfile/SDK constraints retained, no justified update. | Notices remain informational. |
| P14 | Separate dummy signing-key remediation proposed with redacted diff, private environment key and safe missing-key behavior. | Proposal only; original target unchanged. |
| P15 | Fresh assembly, complete checks, actual backend/Docker evidence, preservation, final matrix and packages. | Release sign-off withheld for explicit blockers. |

Additional reproduced Guardian defects: generic credential replacement could remove identifiers/partial expressions and make filtered Python invalid; substring ignore matching hid filenames such as test_timeout.py and environment.py. Redaction now preserves assignment boundaries and recognized password-hashing call context while replacing literal values. Ignore matching uses whole components/globs. Filtered dummy Python is parseable; 24 visible files instead of the earlier 23. Synthetic payload interception covers analysis, four hints, evaluation and patch generation; original bytes and existing signing/.env/path protections pass.

## What leaked and what is covered

Leaking boundary: original source/config -> Guardian snapshot -> AI service -> provider serialization. Excluding .env did not remove a signing key embedded in normal source such as auth.py. Supported values are now removed before serialization. The actual dummy signing key was never printed or saved in raw dummy tracebacks.

Tested forms: recognized SECRET_KEY/JWT/signing/session/app names and password/token/API-secret names; source and dictionary/property assignments; Python typed assignments, quoted/multiline literals and continuations; relevant JS/TS template/config assignments; JSON/TOML/YAML plain/literal/folded/block forms; environment lookups without embedded fallbacks. Common get_password_hash/hash_password literal calls preserve useful nonsensitive structure. Existing AWS access literals, private-key headers, credential database URLs and secret-file/path exclusions remain handled.

Unsupported/unproven: arbitrary aliases/unknown credential identifiers, computed or obfuscated values, unrestricted dynamic interpolation, arbitrary call graphs and unsupported language syntax. Conservative redaction can change snapshot execution semantics. This is not perfect detection or certification of the original application's security.

## End-to-end journey and exact stops

Intended launcher: python -u -m backend, fresh loopback port **51619**, owned PID **16480**. Generated token was kept only in memory. /health 200, missing/wrong bearer token 401, external dummy selection/local inspection 200, 24 filtered files. That backend has been stopped; this audit port is not a current pairing instruction.

A harmless safe fixture's actual non-mocked AI attempt returned **503 at Analyze**, safely reporting missing OPENROUTER_API_KEY and CODEPROOF_MODEL. No live external-provider request was sent. Live analysis/evaluation/patch quality is **NOT TESTABLE**, not a demonstrated implementation failure.

Native rebuilt CodeProof launched and responded; explicit Practice labels and the source explorer were observed. Input repeatedly encountered: "user input was detected in this window; call get_window_state before continuing"; also "window is minimized; call activate_window, refresh with get_window, then retry get_window_state". Fresh observations/recovery did not allow reliable input. These are audit interaction constraints. No guessed handles, security dialogs, credentials or OS theme settings were automated.

The native journey remains incomplete at confirmed **native project selection/pairing**. The independent real API journey reaches selection/local inspection and stops at **live AI configuration**. After that, connected skill map -> challenge -> four live hints -> three live explanation outcomes -> live patch generation -> native review/apply -> native Docker/results/readiness were not executed as a complete live/native journey.

Manual/native checks remaining: folder picker/pairing, connected skill/challenge navigation, four hints, explanation classification/score/gates, review/apply, measured versus unavailable/simulated results/readiness, both-theme dialogs/titlebar, and opt-in preference persistence. Deterministic provider transport fixtures separately verify contracts/gates; real Docker separately verifies target execution and readiness. Neither substitutes for model quality.


## Architecture and impact report

Read root AGENTS.md and setup instructions; no additional nested AGENTS.md found in inspected components. No prohibited direct Flutter provider call, AI direct selected-project read/write, analysis bypass of Guardian, patch outside managed copies or sandbox execution against originals was found in the inspected connected path. This is boundary-specific evidence, not comprehensive certification.

AI reads bundled prompt templates locally; selected-project content comes through Guardian. Flutter uses authenticated loopback HTTP, with redirects disabled. Approved shared changes: explanation outcomes/score gate, canonical nullable counts, and P06 additive incident metadata/request. Provider abstraction and Docker policy preserved. Timestamp serialization retains naive UTC semantics. Theme changes are desktop-local/native methods with one nonsecret preference; no backend/provider contract or OS-wide theme change.

Security impact: supported literals removed before provider use, original-only read boundaries, registered-copy mutations and actual Docker isolation exercised. Filtered snapshots can behave differently from original production code. Readiness certifies measured filtered-snapshot tests only.

## Mock/static inventory

- desktop/lib/services/practice_service.dart: static sample files/analysis/skills, four curated hints, keyword explanation scoring, static diff, in-memory mutation and simulated validation/readiness. Explicitly labeled practice.
- backend/services/demo_fixtures.py and /demo routes: in-memory static practice; legacy endpoints may use demo-backed services. Route presence is not connected provider proof.
- backend/tests/test_sessions.py and test_incidents.py: substituted provider HTTP transport with real Guardian/services/routers/patch logic. Some lifecycle/unit tests mock Docker; separate container probes are actual Docker.
- tests/test_gemini_provider.py: real SDK serialization, substituted transport, no live Gemini.
- Flutter tests: typed fixture/practice data and substituted native preference channel; connection error tests use actual loopback networking.
- training-project: deterministic target fixture that actually executes in Docker, not a mock container. Deterministic repair proposals establish injection/patch/runner behavior, not model quality.

## Release blockers

1. **Live AI configuration/quality (Project Lead):** privately configure a usable OpenRouter key/model, then run actual safe analysis, all explanation outcomes and patch generation. Keep values out of chat/reports.
2. **Complete connected native journey (Friend 1 + integration lead):** complete the manual/runtime checks in an unminimized window without competing input after provider setup.
3. **External dummy setup/security (dummy owner + Friend 3):** actual root discovery cannot import main; test/dependency layout and old httpx AsyncClient use require explicit target/image provisioning. The original hardcoded signing key remains; separate remediation/rotation is proposed, not applied.

Non-blocking: four Flutter upgrade notices, pip notice, LF/CRLF notices, and older Windows ignoring optional DWM color attributes. Unsupported secret representations remain a material safety limitation before provider consent. Initial diff check exit 2 found an extra EOF blank line; fix-worktree-only correction and one-file reassembly yield final exit 0.

## What works and next three tasks

Works in measured scope: Windows build/native launch, real local snapshots/inspection, supported redaction/path protection, three controlled-copy incidents, strict explanation gate/typed outcomes, typed counts/null semantics, managed patching, real trusted Docker runners/isolation/limits/timeout/cleanup, conservative readiness, theme widgets/previews, and actionable configuration/pairing failures.

Remaining: live model quality and full native connected journey; external dummy dependency/import/security remediation; native theme preference/titlebar checks. The Windows frontend needs a running Python backend and Docker/provider prerequisites. It is not an installer or embedded backend bundle.

Next tasks:
1. Privately complete provider setup and verify actual non-mocked safe analysis/evaluation/patch output with Guardian safeguards.
2. Finish native connected journey using training-project, both themes and actual Docker; record evidence and reproduce any defects before fixing.
3. Obtain isolated dummy-remediation authorization, correct test/dependency layout and rotate/configure signing secrets in that copy, then run Docker and compare original hashes.

TASK: Continue P06–P15 and fix reproduced CodeProof errors.
IMPLEMENTED: Changes above and preserved-source delivery.
FILES CREATED/CHANGED: 62 source entries in appended manifest, plus evidence/build artifacts.
ARCHITECTURE/API/DATA IMPACT: Exact approved changes above; no silent redesign.
SECURITY IMPACT: Filter-before-provider, managed-only mutation, real Docker protection and preservation evidence.
TESTS: 477 Python and 37 Flutter passed; all fresh runtime probes exit 0, including asserted deliberate failures.
KNOWN ISSUES: Explicit blockers/limitations.
NEXT DEPENDENCY: Private setup, native verification and separately owned dummy remediation.

## Evidence and delivery

Per-task reports in audit-evidence and fix-worktree setup-evidence provide implementation details. Intermediate pending-build statements are superseded only by fresh checks here. Final source hashes: P15-ASSEMBLY-MANIFEST.json. Counts/exits: JUnit, Python/Flutter logs, final-commands.json and runtime-exit-codes.json. Protection: final-preservation.json and full dummy hash records. Tokens and API-key values are excluded.

CodeProof-Windows-P06-P15.zip includes the complete release folder (EXE/DLLs/data) and RUN-CODEPROOF.txt. Keep files together.
CodeProof-Source-P06-P15.zip includes tracked source plus approved new files and this report; no private .env, .git, dependency trees or generated build trees.
artifact-manifest.json records package/executable hashes and sizes.

The following appendices give the complete 18-feature matrix, real container outcomes, all 35 API operations, command ledger, process state and changed-file list.



## Complete MVP-01–MVP-18 matrix

Exactly one status per feature: **8 PASS, 10 PARTIAL**. Live provider subchecks remain NOT TESTABLE within partial features. PASS covers exercised scope only; regression fixtures do not establish model quality.

FEATURE | STATUS | EVIDENCE | REAL OR MOCK | BLOCKER? | OWNER
---|---|---|---|---|---
| MVP-01 Desktop startup | PASS | Fresh release build; responding native practice source explorer observed | Real native | No | Friend 1 |
| MVP-02 Project selection | PARTIAL | Real launcher opens dummy: 24 files; earlier actual Dart client; native folder/pairing unverified | Real API/Dart; native pending | Yes: native journey | Friend 1 + Friend 3 |
| MVP-03 Guardian | PASS | Security suites and synthetic provider-payload interception; original hashes; scope limitations documented | Real Guardian; intercepted transport | No in tested scope | Project Lead + Friend 3 |
| MVP-04 Analysis | PARTIAL | Local inspection 200; provider contract fixtures pass; safe live attempt stops at configuration 503 | Real local; AI fixtures | Yes: live AI | Project Lead |
| MVP-05 Skill map | PARTIAL | Typed/rendered fixture skills; connected live inference not reached | Provider fixtures / static practice | Yes: live AI | Project Lead + Friend 1 |
| MVP-06 Controlled challenges | PARTIAL | Three exact-manifest incidents, nine actual Docker states; selector/coaching fixtures; native/live pending | Real incidents/Docker; AI fixtures | Yes: native/live flow | Project Lead + Friend 3 + Friend 1 |
| MVP-07 Investigation | PARTIAL | Real TCP/Guardian incident contexts; native practice explorer; live connected pending | Real services; provider fixtures | Yes: native/live flow | Project Lead + Friend 1 |
| MVP-08 Four hints | PARTIAL | Four serialized incident-bound hints tested; live hints not executed | Provider transport fixtures; curated practice | Yes: live AI | Project Lead |
| MVP-09 Explanation-before-patch | PASS | CORRECT >=0.7 enforced; partial/incorrect/malformed blocked; resubmission revokes permission | Real gate; deterministic AI output | No for gate | Project Lead + Friend 3 |
| MVP-10 Evaluation | PARTIAL | Three typed classifications, score/feedback, safe malformed rejection; live quality unmeasured | Provider fixtures; keyword practice | Yes: live quality | Project Lead + Friend 1 |
| MVP-11 Patch generation | PARTIAL | Typed diff/context serialization tested; actual owned-copy repair; no live proposal | Provider fixtures; real Patch Lab | Yes: live AI | Project Lead |
| MVP-12 Patch review | PARTIAL | Diff/gate/theme widgets and rendered previews; native connected review unexecuted | Widget rendering; fixture data | Yes: native journey | Friend 1 |
| MVP-13 Patch application | PASS | Actual owned-copy repair/Docker success; unsafe/original/link/tampered paths rejected; original bytes preserved | Real Patch Lab/Docker | No in tested scope | Friend 3 |
| MVP-14 Docker | PASS | Actual inspect/in-container limits, non-root/read-only/no-network, timeout/cleanup | Real containers | No for tested image | Friend 3 |
| MVP-15 Test runner | PASS | Actual pytest/unittest/node pass/fail/skip/empty/error cases; dummy setup fails honestly | Real containers | Yes for dummy setup | Friend 3 + dummy owner |
| MVP-16 Results UI | PARTIAL | Canonical count/null parsing/rendering and simulation labels; native connected screen pending | Real API/parser; widget fixtures | Yes: native journey | Friend 1 + Friend 3 |
| MVP-17 Readiness | PASS | Actual HTTP/Docker all-pass positive -> READY; other states -> BLOCKED | Real readiness/Docker | No for decision logic | Friend 3 |
| MVP-18 Original protection | PASS | 253 protected original hashes plus HEAD/index; all 6398 dummy files unchanged; actual copy/container protection | Real hashes/Docker | No in measured scope | Project Lead + Friend 3 |

## Real Docker details

Engine linux; trusted image sha256:2625fdcd45d0636bbb5aa97521e89a3f48c2a047cec9333dfb9522b40b82cb5f. Actual inspect and in-container assertions establish user 65532:65532, network none/disabled, read-only root/snapshot, dropped ALL capabilities, no-new-privileges, 2 CPUs, 512 MiB memory/no extra swap, 64 PIDs, /tmp tmpfs 128 MiB noexec/nosuid/nodev, timeout, capped logs and cleanup. statvfs and cgroup assertions passed. This tests container scratch limits, not a universal host/image-storage disk quota.

Connected API + real Docker, with provider HTTP transport fixtures:

| Case | Status | Canonical counts | Readiness | Verified |
|---|---|---|---|---|
| pass | passed | {"total": 2, "passed": 2, "failed": 0, "skipped": 0} | READY | True |
| fail | failed | {"total": 2, "passed": 1, "failed": 1, "skipped": 0} | BLOCKED | True |
| skip | passed | {"total": 2, "passed": 1, "failed": 0, "skipped": 1} | BLOCKED | True |
| empty | failed | {"total": 0, "passed": 0, "failed": 0, "skipped": 0} | BLOCKED | True |
| delay | timeout | null | BLOCKED | True |
| unavailable | unavailable | null | BLOCKED | True |
| parse | error | null | BLOCKED | True |

Additional runners: unittest/node each total 3/pass 1/fail 1/skip 1 -> BLOCKED; pytest all-skipped 2/0/0/2 -> BLOCKED. Isolation fixture 6/6 pass; disk/cgroup/noexec fixture 3/3 pass. Real timeout/failure/repair/alternative-runner probes removed containers/copies. Unknown/setup-error/timeout/unavailable/missing-summary counts are null. Measured no-tests total 0 blocks readiness. Legacy scalar zero defaults are not measurements when canonical test_counts is null.

External dummy: actual Docker discovery failed, canonical counts null, missing main, readiness BLOCKED; raw traceback/source discarded. Earlier probe recorded four collection import errors. Current safe summary does not invent executed counts. Target README expects backend/ working directory while fixed runner starts at root; additional target dependencies and old httpx AsyncClient usage require explicitly approved provisioning. Original untouched.

## OpenAPI inventory

Fresh /health: HTTP 200 healthy/codeproof-backend/version 1.0.0. All 35 method/path operations below. /v1 is connected; /demo and legacy routes may use fixtures. Root / returned 404 as expected, not a server failure.

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
| GET | /release-readiness |
| POST | /release-readiness |
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

## Command ledger

Python used the fresh audit environment, worktree PYTHONPATH, PYTHONDONTWRITEBYTECODE=1 and Docker directory on PATH. Launcher helper starts python -u -m backend with a free BACKEND_PORT and in-memory token. No target executes on the host. Output redirected to the named logs; runtime errors are asserted cases.

| CWD | Command | Exit | Log |
|---|---|---:|---|
| C:\Codeproof-release-audit-p06-p15 | backend/.venv/Scripts/python.exe -m pip install -r backend/requirements-dev.txt | 0 | python-dependency-install.log |
| C:\Codeproof-release-audit-p06-p15 | backend/.venv/Scripts/python.exe -m pytest backend/tests -q -W error::DeprecationWarning -W error::FutureWarning -p no:cacheprovider --basetemp=C:/Codeproof-release-audit-p06-p15/.pytest-tmp-final-backend --junitxml=audit-evidence/backend-tests.xml | 0 | backend-tests.log |
| C:\Codeproof-release-audit-p06-p15 | backend/.venv/Scripts/python.exe -m pytest tests/ --tb=short -q -W error::DeprecationWarning -W error::FutureWarning -p no:cacheprovider --basetemp=C:/Codeproof-release-audit-p06-p15/.pytest-tmp-final-project --junitxml=audit-evidence/project-tests.xml | 0 | project-tests.log |
| C:\Codeproof-release-audit-p06-p15 | backend/.venv/Scripts/python.exe -m pip check | 0 | pip-check.log |
| C:\Codeproof-release-audit-p06-p15\desktop | flutter pub get | 0 | flutter-pub-get.log |
| C:\Codeproof-release-audit-p06-p15\desktop | flutter analyze | 0 | flutter-analyze.log |
| C:\Codeproof-release-audit-p06-p15\desktop | flutter test | 0 | flutter-tests.log |
| C:\Codeproof-release-audit-p06-p15\desktop | flutter build windows --release | 0 | windows-build.log |
| C:\Codeproof-release-audit-p06-p15 | backend/.venv/Scripts/python.exe audit-evidence/f07_real_docker_v2.py | 0 | f07_real_docker_v2.log |
| C:\Codeproof-release-audit-p06-p15 | backend/.venv/Scripts/python.exe audit-evidence/intended_launcher_runtime.py | 0 | intended_launcher_runtime.log |
| C:\Codeproof-release-audit-p06-p15 | backend/.venv/Scripts/python.exe audit-evidence/docker_validation_probe_v2.py | 0 | docker_validation_probe_v2.log |
| C:\Codeproof-release-audit-p06-p15 | backend/.venv/Scripts/python.exe audit-evidence/docker_validation_additional.py | 0 | docker_validation_additional.log |
| C:\Codeproof-release-audit-p06-p15 | backend/.venv/Scripts/python.exe audit-evidence/f07_real_runners.py | 0 | f07_real_runners.log |
| C:\Codeproof-release-audit-p06-p15 | git diff --check | 0 | diff-check.log |

## Final processes

{
  "checked_at_utc": "2026-10-02T00:09:26.085355+00:00",
  "docker_engine": "29.8.1",
  "owned_runtime_containers_checked": 14,
  "owned_runtime_containers_remaining": [],
  "intended_launcher_stopped": true,
  "fixture_tcp_backend_stopped": true,
  "managed_fixture_copies_remaining": 0,
  "desktop": {
    "Id": 15404,
    "Path": "C:\\codeproof-release-audit-p06-p15\\desktop\\build\\windows\\x64\\runner\\release\\codeproof_desktop.exe",
    "Responding": true
  },
  "docker_desktop": "Started as authorized prerequisite; left running; user workloads untouched"
}

Audit-owned runtime backends stopped; recorded containers/copies removed. Responding rebuilt desktop left open. Docker Desktop remains running as authorized prerequisite. No user processes stopped; historic PIDs never used to kill unrelated processes.

## Changed source files

62 uncommitted source entries, verified by P15-ASSEMBLY-MANIFEST.json; generated/build/evidence files separate:

- .env.example
- README.md
- ai/README.md
- ai/models/analysis.py
- ai/models/explanation.py
- ai/models/patch.py
- ai/prompts/explanation.md
- ai/providers/gemini.py
- ai/services/explanation_evaluator.py
- backend/README.md
- backend/__main__.py
- backend/config.py
- backend/models.py
- backend/requirements-dev.txt
- backend/requirements.txt
- backend/routers/sessions.py
- backend/services/challenge_service.py
- backend/services/demo_fixtures.py
- backend/services/incidents.py
- backend/services/release_readiness.py
- backend/services/sandbox.py
- backend/services/sessions.py
- backend/session_models.py
- backend/tests/test_configuration.py
- backend/tests/test_demo_ui_api.py
- backend/tests/test_incidents.py
- backend/tests/test_services.py
- backend/tests/test_sessions.py
- backend/tests/test_validation_counts.py
- desktop/README.md
- desktop/lib/app/app.dart
- desktop/lib/app/theme.dart
- desktop/lib/domain/workspace.dart
- desktop/lib/domain/workspace_controller.dart
- desktop/lib/features/startup/startup_screen.dart
- desktop/lib/features/workspace/coach.dart
- desktop/lib/features/workspace/evidence.dart
- desktop/lib/features/workspace/pages.dart
- desktop/lib/features/workspace/workspace_shell.dart
- desktop/lib/services/practice_service.dart
- desktop/lib/services/workspace_service.dart
- desktop/lib/ui/glass.dart
- desktop/test/connection_test.dart
- desktop/test/evaluation_test.dart
- desktop/test/incidents_test.dart
- desktop/test/theme_test.dart
- desktop/test/validation_counts_test.dart
- desktop/test/widget_test.dart
- desktop/test/workspace_controller_test.dart
- desktop/windows/runner/flutter_window.cpp
- desktop/windows/runner/win32_window.cpp
- desktop/windows/runner/win32_window.h
- tests/test_gemini_provider.py
- tests/test_guardian_correctness.py
- tests/test_signing_secret_redaction.py
- tests/test_timestamp_compatibility.py
- training-project/README.md
- training-project/app.py
- training-project/tests/test_app.py
- workspace/models.py
- workspace/scanner.py
- workspace/secret_filter.py
