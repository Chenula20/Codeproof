# F07 — structured test counts and readiness implementation report

Date: 2026-10-01 (Asia/Colombo).
TASK: Trace real SandboxResult counts through connected models and Dart results/readiness; implement the user-approved compatible contract; verify all-pass/fail/empty/unavailable/timeout/parse failure and honest simulation labels with real Docker evidence.

Worktree: C:\Codeproof-fix-ai-setup. Branch: codex/fix-ai-setup. HEAD: 911d45cc267d8972dd7b65d6cf260bd6e7a779db. F07-CONTRACT-PROPOSAL.md was approved by the user's yes before shared contract edits. No commits, pushes or branch merges.

IMPLEMENTED:
- Shared strict TestCounts model: total, passed, failed, skipped. failed combines failed/error test outcomes; all counters are nonnegative integers and must sum to total. Fractional/boolean/string and inconsistent counts are rejected.
- Nullable test_counts propagated from SandboxResult to ReleaseReadiness and connected Validation/report. Legacy integer counts remain compatibility projections when known; their defaults do not establish successful evidence when canonical counts are null.
- Connected Validation includes simulated=false and preserves error status. Counts unavailable for Docker/image unavailability, timeout, unrecognized/unsupported summaries; confirmed empty runs use measured zeros. Output-cap truncation clears counts and returns error. Collection/setup failures with no trustworthy executed-test total remain unknown instead of fabricating completed tests.
- Pytest preserves skips and combines recognized test errors with failures. Ordinary warning counts do not inflate test totals. Unittest derives mixed passing/failing/skipped totals from its completed summary instead of marking the entire suite failed. Node checks reported totals against pass/fail/skip outcomes.
- Readiness consumes canonical counts. Unknown, zero, failed or skipped evidence stays BLOCKED, even if legacy numbers or status alone appear successful. Existing security/original/state gates remain. Only a positive, complete all-pass result can become READY; existing warnings retain WARNING behavior.
- Dart has typed TestCounts, nullable parsing, count-aware success/readiness, explicit unknown/empty messages, exact Total/Passed/Failed-errors/Skipped display and exported evidence fields.
- Simulated practice explicitly says no tests executed and keeps real counts null. Practice completion remains separately labelled; it cannot certify real release readiness. Older connected payloads lacking counts are treated as unknown.

## Source-to-consumer map

| Stage | Files | Change |
|---|---|---|
| Canonical backend model | backend/models.py | TestCounts and nullable canonical evidence; compatibility projections |
| Real runner parsing | backend/services/sandbox.py | Known totals/skips, null for unsupported/unknown evidence, cap failure semantics |
| Readiness | backend/services/release_readiness.py | Positive complete all-pass canonical counts required |
| Connected response | backend/session_models.py; backend/services/sessions.py | Preserve counts, error and simulated=false |
| Connected report | existing backend/routers/sessions.py | Already serializes Validation, so new fields flow through without route changes |
| Dart models | desktop/lib/domain/workspace.dart | Strict count parsing; legacy missing field is unknown; conservative readiness |
| Results/readiness/export UI | desktop/lib/features/workspace/evidence.dart | Exact counters, unknown/empty/simulation labels, no status-only real success |
| Practice service | desktop/lib/services/practice_service.dart | Explicit simulated flag and null real counts |

## Verification results

| Check | Result | Evidence |
|---|---|---|
| Full backend + project Python suite | 423 passed: 230 backend + 193 project; 0 failed/errors/skips; 1,033 warnings; exit 0 | f07-python-tests.log/XML |
| Flutter analysis | No issues; exit 0 | f07-flutter-analyze-verified.log |
| Flutter tests | 27 passed; exit 0 | f07-flutter-tests-verified.log |
| Windows release build | Succeeded; exit 0 | f07-windows-build.log |
| Real connected HTTP + Docker scenarios | All 7 scenario expectations verified; harness exit 0 | f07-real-docker-v2.log/JSON |
| Additional real runner scenarios | All 3 expectations verified; harness exit 0 | f07-real-runners.log/JSON |
| Original checkout preservation | 253 baseline hashes, HEAD and index unchanged | f07-preservation.json |
| Diff whitespace check | Exit 0 | f07-preservation.json |

Python command, from fix-worktree root:
C:\Codeproof-mvp-audit-worktree\backend\.venv\Scripts\python.exe -m pytest backend/tests tests/ --tb=short -q -p no:cacheprovider --basetemp=C:\Codeproof-fix-ai-setup\.pytest-tmp-f07 --junitxml=setup-evidence/f07-python-tests.xml

Flutter commands, from desktop/: flutter analyze; flutter test; flutter build windows. Dependency resolution completed normally; four packages have newer releases outside current constraints. No unrelated dependency upgrades were made.

Runtime commands, from fix-worktree root with the same Python and PYTHONDONTWRITEBYTECODE=1:
- setup-evidence/f07_real_docker_v2.py — exit 0.
- setup-evidence/f07_real_runners.py — exit 0.

Docker image: codeproof/sandbox:latest, ID sha256:2625fdcd45d0636bbb5aa97521e89a3f48c2a047cec9333dfb9522b40b82cb5f. Existing trusted repository image, Linux engine 29.8.1. No user process or engine was stopped to manufacture unavailable evidence.

## Real Docker evidence

The first seven cases used a fresh loopback Uvicorn backend and real HTTP connected-session routes through Guardian, managed patch copy, application, Docker, Validation and report. Earlier AI steps used explicitly deterministic OpenRouter HTTP transport fixtures. Docker SDK/engine/container execution and result parsing were real. These checks establish count propagation and readiness, not live AI evaluation quality.

| Scenario | Actual connected status | Canonical total / passed / failed / skipped | Readiness |
|---|---|---|---|
| All-pass pytest | passed | 2 / 2 / 0 / 0 | READY |
| Mixed failing pytest | failed | 2 / 1 / 1 / 0 | BLOCKED |
| Passing pytest with skip | passed | 2 / 1 / 0 / 1 | BLOCKED |
| No tests collected | failed | 0 / 0 / 0 / 0 | BLOCKED |
| Timeout | timeout | null | BLOCKED |
| Intentionally absent audit image | unavailable | null | BLOCKED |
| No recognized runner summary | error | null | BLOCKED |
| Mixed unittest (direct real sandbox service) | failed | 3 / 1 / 1 / 1 | BLOCKED |
| Mixed Node (direct real sandbox service) | failed | 3 / 1 / 1 / 1 | BLOCKED |
| All-skipped pytest (direct real sandbox service) | failed | 2 / 0 / 0 / 2 | BLOCKED |

Counts remain available for a recognized failed suite; those failures are expected fixture outcomes, not regressions. Unavailable image checks exercise the genuine image-unavailable branch without stopping Docker. A mocked daemon failure remains covered by existing security regressions. The real parse-failure fixture removes pytest's terminal reporter inside the container; no completed standard summary is available, and CodeProof reports unknown counts instead of success. Timeout is bounded and containers are removed by CodeProof.

Every runtime fixture's original bytes remained unchanged. The connected harness inspected readonly snapshot mounts, container removal, snapshot-path removal, session shutdown and empty managed-copy registry. Additional runner tests also retained original hashes and emptied the copy registry. Final docker ps -a --filter name=codeproof- returned no containers.

## Regression scope and evidence boundaries

Parser/model regressions cover the three supported runners, pass/fail/skip/all-skip/empty, collection failure, ordinary pytest warnings, malformed output, extended unsupported outcomes, inconsistent totals, strict invalid counter types and unknown counts with misleading legacy values. HTTP regressions check exact nested count propagation and report readiness with both TestClient and loopback TCP; sandbox transport fixtures in those tests are explicitly synthetic. They also replace prior validation with unavailable evidence to prove stale validated phase does not retain READY.

Flutter regressions cover strict parsing, legacy missing counts, simulation labels, exact counters, unknown/empty messages, stale validated state and results/readiness rendering. Existing F06 explanation gates, Guardian/.env/path protections, synthetic secret redaction and original-byte tests passed in the full suite. The Windows executable was built but no native desktop runtime session was launched for F07.

Initial unsuccessful verification artifacts are retained. The first Flutter run had new-test import and required-widget-argument mistakes; those fixtures were corrected. An attempted analyze log path was outside the intended relative directory and failed before saving; the final analysis ran from desktop/ and succeeded. The first real parse fixture used a large log, but Docker retained a valid completed summary, so that fixture did not create a parse failure and its harness correctly exited 1. The corrected summary-suppression fixture produced the intended real error/null-count path. Neither first-run artifact is counted as a PASS.

## Preservation and remaining limits

Original checkout C:\Codeproof-main\Codeproof-main: all 253 recorded file hashes unchanged, original HEAD and index unchanged. Protected original untracked Flutter files were not touched. All edits/generated artifacts are in the separate fix worktree. Private AI .env was not read or modified for F07. No original dummy project files were executed or changed by this task; runtime evidence used newly created harmless fixtures only. The audit Python environment was used with bytecode disabled.

All F07-owned loopback backend processes stopped, managed copies were cleaned, and no CodeProof validation containers remain. Docker Desktop and its existing engine remain available. No user-owned process was stopped. The worktree and evidence remain intact.

Unsupported cases fail closed: pytest extended xfail/xpass/deselection summaries, unittest expected-failure variants or unreconciled subtest totals, Node cancelled/todo outcomes and unrecognized summary formats. Error-only pytest discovery/setup summaries may intentionally yield unknown counts rather than asserting an executed-test total. Textual runner summaries are not an independent proof that project tests are authentic. Results describe a filtered snapshot, not production certification.

Existing deprecation warnings remain: google.generativeai support ended; Starlette/httpx test-client integration; datetime.utcnow. The unrelated dummy-app import-layout failure and Guardian substring exclusion issue from prior reports are not fixed by F07. No live provider request or real AI-quality claim was made.

FILES CREATED/CHANGED for F07:
- backend/models.py, backend/session_models.py, backend/services/sandbox.py, backend/services/release_readiness.py, backend/services/sessions.py, backend/README.md.
- backend/tests/test_services.py, backend/tests/test_sessions.py, new backend/tests/test_validation_counts.py.
- desktop/lib/domain/workspace.dart, desktop/lib/features/workspace/evidence.dart, desktop/lib/services/practice_service.dart.
- desktop/test/widget_test.dart, new desktop/test/validation_counts_test.dart.
- setup-evidence/F07-CONTRACT-PROPOSAL.md, this report, F07 logs/JSON/XML and helper scripts/harmless fixtures; generated Flutter/pytest build and test artifacts are uncommitted.

ARCHITECTURE IMPACT: Approved propagation of canonical evidence and conservative readiness across existing components. No topology, arbitrary command execution, provider abstraction or isolation changes.
API IMPACT: Additive nullable test_counts, connected simulated flag, connected error status; existing endpoint names/request shapes and legacy count fields retained.
DATA MODEL IMPACT: Strict consistent TestCounts shared by backend results/readiness/connected validation, matching nullable Dart type. Unknown and measured zero are distinct.
SECURITY IMPACT: Missing, unknown, skipped and unavailable evidence cannot certify real readiness. Docker restrictions, explanation-before-patch and original protection remain enforced; their regressions pass.
TESTS: Exact results and mock/real boundaries above.
KNOWN ISSUES: Documented parser limitations, existing deprecations and unrelated earlier findings remain. Native desktop interaction and live AI quality were not tested in F07.
NEXT DEPENDENCY: Backend and Flutter leads should deploy the approved count contract together; a new desktop paired with an old backend deliberately treats missing count evidence as unknown. No further implementation undertaken beyond F07.
