# F06 — three-way explanation evaluation implementation report

Date: 2026-10-01 (Asia/Colombo).
TASK: Implement the approved F06 evaluation contract, preserve explanation-before-patch gates, revoke stale approvals, run deterministic production-provider regressions, and separate live evaluation evidence.
Worktree: C:\Codeproof-fix-ai-setup. Branch: codex/fix-ai-setup. HEAD remains 911d45cc267d8972dd7b65d6cf260bd6e7a779db. Changes are uncommitted and unpushed. This worktree also retains earlier P01/P02 changes; F06 did not modify the original checkout.

IMPLEMENTED:
- Retained the AI enum CORRECT/PARTIALLY_CORRECT/INCORRECT and propagated it into typed backend SessionView.evaluation and Dart.
- Added classification as an additive connected response field; passed, score, feedback, routes, request shapes and phases remain available.
- Evaluator derives passed from CORRECT AND score >= configured passing threshold, default 0.7. Provider passed is not authority. Prompt reflects the configured threshold.
- Provider output validation rejects unknown/missing classifications, nonnumeric/boolean/nonfinite/out-of-range scores, missing fields, blank feedback and nonboolean passed. Malformed JSON is rejected by the existing production provider parser.
- Partial/incorrect or correct-below-threshold results stay investigating, have no patch, and cannot apply patches. Application independently rechecks classification and score even if a stored passed flag contradicts them.
- Each accepted new explanation attempt clears prior evaluation/patch approval and blocks readiness before provider work. Malformed evaluation, transport failure or malformed patch output cannot retain prior approval. Desktop controller also clears visible old approval before requesting a fresh evaluation.
- Coach shows Correct / Partially correct / Incorrect, percentage score and feedback. Review and readiness consumers use the consistent gate.
- Dart supports legacy payloads with the classification field absent, showing the old generic label rather than inventing a three-way verdict. Explicit null/unknown classifications and invalid score/feedback are rejected. Legacy fallback remains subject to passed and score threshold; verified three-way semantics require the updated backend.
- Practice simulation supplies three explicit categories; legacy backend keyword evaluation no longer marks partial passed. Demo re-evaluation clears stale patch unlocks. These simulated paths remain simulation, not provider-quality evidence.

## Boundary mapping

| Boundary | Files | Behavior |
|---|---|---|
| AI output validation | ai/models/explanation.py | Existing enum, finite bounded numeric score, nonblank feedback, strict provider passed field |
| Server-owned decision | ai/services/explanation_evaluator.py; ai/prompts/explanation.md | CORRECT + score threshold; no keyword judgment in connected path |
| Typed connected response | backend/session_models.py | Required classification plus existing passed/feedback/score |
| Connected state/gates | backend/services/sessions.py | Revoke old approval; generate patch only after accepted evaluation; recheck on apply |
| Dart parsing and gates | desktop/lib/domain/workspace.dart; domain/workspace_controller.dart | Typed enum, legacy fallback, malformed response rejection, client stale-approval revocation |
| UI consumers | desktop/lib/features/workspace/coach.dart; evidence.dart | Three labels, percentage, feedback and gated review/readiness |
| Simulated consumers | desktop/lib/services/practice_service.dart; backend/services/challenge_service.py; demo_fixtures.py | Simulated grading only, partial/incorrect remain locked |

## Verification

All Python commands used C:\Codeproof-mvp-audit-worktree\backend\.venv\Scripts\python.exe, from this fix worktree, with PYTHONDONTWRITEBYTECODE=1. Docker CLI bin was prepended for the existing real Docker regression. Trusted repository tests were host-executed as authorized; target fixture execution through CodeProof remained in Docker.

| Command | Result | Evidence |
|---|---|---|
| python -m pytest backend/tests tests/ --tb=short -q -p no:cacheprovider --basetemp=C:\Codeproof-fix-ai-setup\.pytest-tmp-f06-final --junitxml=setup-evidence/f06-python-final.xml | Exit 0: 371 passed, 0 failed/errors/skips, 815 warnings. Backend 178, project 193 | f06-python-final.log/XML |
| python -m pytest backend/tests -q --tb=short -p no:cacheprovider --basetemp=C:\Codeproof-fix-ai-setup\.pytest-tmp-f06-backend-verified --junitxml=setup-evidence/f06-backend-verified.xml | Exit 0: 184 passed, 0 failed/errors/skips, 706 warnings; includes six further application-defense cases | f06-backend-verified.log/XML |
| flutter pub get (desktop/) | Exit 0 | f06-flutter-pub-get.log |
| flutter analyze (desktop/) | Exit 0: no issues | f06-flutter-analyze-verified.log |
| flutter test (desktop/) | Exit 0: 17 passed | f06-flutter-test-verified.log |
| flutter build windows (desktop/) | Exit 0, release executable built | f06-windows-build.log |
| git diff --check | Exit 0 | f06-preservation.json |

Final verified Python coverage is 184 backend + 193 project tests, across the two successful runs above (not a claimed single 377-test command).

New connected tests run against both FastAPI TestClient and an actual loopback Uvicorn HTTP server. They use real Guardian/AI/evaluator/patch services and the production OpenRouter structured JSON parser. Only external provider HTTP responses are deterministic httpx.MockTransport fixtures. No live provider grade is claimed.

Cases include all three classifications at 0.69, 0.70 and 0.95 with deliberately contradictory provider passed flags; pre-investigation rejection; patch-before-explanation rejection; no Patch provider request for nonpassing grades; successful correct/high-enough patch and managed-copy application; original fixture hashes unchanged; malformed enum/JSON, absent classification/score/feedback/passed, string/bool/nonfinite/negative/out-of-range score, blank feedback, nonboolean passed; partial/incorrect re-evaluation after prior success; transport failure; malformed patch output; and direct application defense against contradictory stored flags.

Flutter tests cover all three visible labels, score and feedback, classification-aware permission, below-threshold lock, legacy missing-field behavior, malformed typed payloads, controller stale approval, and the existing guided practice workflow. Widget/model fixtures certify rendering/gates, not semantic evaluation quality.

Existing Guardian/secret-filter/provider-context regressions passed, including synthetic source-signing-secret payload interception and original-byte/.env/path protections. No real dummy signing key or API key was displayed. Existing real Docker regression passed; dummy-app import-layout issues from the Docker report remain separate and unfixed.

## Live evaluation

NOT TESTABLE. Secret-free availability check found OPENROUTER_API_KEY absent in this process, CODEPROOF_MODEL absent, and no trusted fix-worktree root .env. P01 protections remain regression-verified, but private provider/model prerequisites are missing. No live analysis/evaluation request was made. Correct/partial/incorrect semantic quality remains unverified with a real model. Configure privately outside chat before running that separate verification; keyword practice results are not a substitute.

## Preservation

f06-preservation.json records all 253 original baseline file hashes unchanged, original HEAD unchanged and original index hash unchanged. The original desktop/.dart_tool/, desktop/codeproof_desktop.iml and desktop/windows/ were not touched. No cleanup/reset/stash/delete/move operations, commits, pushes or branch merges were performed. Source and generated files are confined to the separate fix worktree. The audit virtual environment was used read-only with bytecode disabled. Dummy project files were not edited during F06; the 6,398-file Docker comparison is prior-task evidence, not a fresh F06 dummy hash comparison.

Tests' loopback servers shut down; no F06 backend/app runtime process remains. Docker Desktop may remain running from the previous authorized validation. The Windows app was built, not launched in this task.

## Files created/changed for F06

Application/docs: ai/models/explanation.py, ai/services/explanation_evaluator.py, ai/prompts/explanation.md, backend/session_models.py, backend/services/sessions.py, backend/services/challenge_service.py, backend/services/demo_fixtures.py, backend/README.md, desktop/lib/domain/workspace.dart, desktop/lib/domain/workspace_controller.dart, desktop/lib/features/workspace/coach.dart, desktop/lib/features/workspace/evidence.dart, desktop/lib/services/practice_service.dart.
Tests: backend/tests/test_sessions.py, backend/tests/test_demo_ui_api.py, desktop/test/evaluation_test.dart (new), desktop/test/widget_test.dart, desktop/test/workspace_controller_test.dart.
Evidence: F06-CONTRACT-PROPOSAL.md, this report, F06 command logs/XML, f06-preservation.json and audit helper scripts. Flutter/pytest generated dependencies/build files are uncommitted in the worktree.

Initial failed runs are preserved: first Python combined run had one TCP follow-up connection reset after a handled 500. The fixture now disables keepalive so each real HTTP assertion uses a fresh connection; no production retry or error suppression was added. Initial Flutter runs exposed a new-test import name collision and a missing GlassSettings wrapper in isolated widget fixtures. Those test setup errors were corrected. A generated test file encoding issue was also corrected to UTF-8. Final verified logs supersede those failures without deleting them.

ARCHITECTURE IMPACT: Explicitly approved cross-component evaluation propagation/gate tightening. Existing component topology, provider abstraction and Guardian boundaries preserved.
API IMPACT: Additive SessionView.evaluation.classification; stricter evaluation output validation; existing response fields/routes retained. Older desktop clients ignore the new field.
DATA MODEL IMPACT: Required typed backend classification; Dart enum with missing-field-only legacy compatibility; bounded finite score.
SECURITY IMPACT: Partial/incorrect high scores cannot authorize patching, stale approval is revoked, and application checks do not trust the boolean alone. Original protection and redaction regressions pass.
TESTS: Results above. Mocked provider contract regressions and real loopback/Docker evidence are explicitly separated from absent live provider-quality evidence.
KNOWN ISSUES: Live evaluation unavailable; old backend fallback cannot certify old server behavior; existing Google SDK, Starlette/httpx and datetime.utcnow deprecation warnings remain. Four Flutter dependencies have newer versions outside current constraints. Existing Guardian substring exclusions and dummy test import failure are unrelated open findings.
NEXT DEPENDENCY: Project Lead + Backend Lead + Flutter/UI Leads should integrate this approved additive contract together. Live model grading needs private provider/model configuration; no further implementation performed after this task.
