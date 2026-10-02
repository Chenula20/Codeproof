# F07 — test counts and readiness contract proposal

Status: investigation complete; approval required before implementation. No application source changed for F07.
Worktree: C:\Codeproof-fix-ai-setup, codex/fix-ai-setup. Existing F06/P01/P02 work retained. Original checkout untouched. Private AI .env was not read.

CURRENT / TRACE:
1. backend/services/sandbox.py produces backend/models.py SandboxResult with tests_total/tests_passed/tests_failed. All default to 0 even when execution is unavailable or has no trustworthy summary. No skipped field exists.
2. pytest parser sums passed + failed + errors and omits skipped. unittest parser subtracts skipped on successful exit, but then uses passed + failed as total, losing skipped; on nonzero exit it calls the whole reported total failed. Node ignores skipped/cancelled and does not check its reported total against outcomes. Unrecognized output is represented as failed with zero counts instead of a parse error with unknown counts.
3. backend/services/release_readiness.py gates on legacy counts/status/runtime_errors, then reports only total/passed. It fails closed for current unavailable statuses but can approve a partially skipped suite because skipped counts were omitted.
4. backend/services/sessions.py validate() drops every count when building backend/session_models.py Validation. It also maps generic sandbox error to connected failed. /v1/sessions/{id}/report forwards the same count-less validation.
5. desktop/lib/domain/workspace.dart ValidationResult contains only status/output/duration/originalUnchanged/checks. WorkspaceData.ready trusts phase == validated. evidence.dart paints a passing icon and marks Runner passed from status alone, with no count check. Logs are displayed, but structured metrics are absent.
6. PracticeWorkspaceService produces local in-memory fixture expectations; it does not execute three credential tests. Existing text labels Practice and says no Docker/tests executed. F07 must keep this distinction explicit and must not invent three passing tests from the three lines of expectations.

REQUEST — smallest compatible canonical addition:
Add a nullable test_counts object using one shared typed backend TestCounts model and matching Dart type:

  test_counts: {
    total: nonnegative strict integer,
    passed: nonnegative strict integer,
    failed: nonnegative strict integer,
    skipped: nonnegative strict integer
  } | null

Add test_counts to SandboxResult, ReleaseReadiness and connected Validation. Retain existing legacy SandboxResult/ReleaseReadiness integer fields and existing endpoint/request names, output, duration, original protection and explanation gates. These old integers become compatibility projections when canonical counts are known; existing zero defaults when unknown are deprecated placeholders, NEVER evidence of measured outcomes or readiness. Canonical test_counts=null explicitly means unavailable/unknown. Do not infer canonical counts from those default legacy zeros.

The supported equivalent failed means failed/error test outcomes combined, and the UI labels it Failed/errors. It is not advertised as assertion-only failures. For trustworthy completed summaries: total = passed + failed + skipped. Counts cannot be negative, fractional, boolean or internally inconsistent. Collection errors without a trustworthy test-outcome total yield null counts, not invented executed tests.

Add simulated: boolean = false to connected Validation, emitted explicitly. Practice sets true, keeps test_counts null, and labels its in-memory result Simulated practice — no tests executed. Do not populate real-looking test counters from demo expectations. Unversioned existing demo response shapes stay intact with their current simulation flags.

Allow error as an additional connected Validation.status value. Existing status fields are strings in Dart; old clients can display error generically and will not equate it with passed. New clients get an explicit execution/parse failure distinction. No new routes, configurable host commands, runner working-directory changes or Docker policy changes.

Examples:

Real all-pass:
{"status":"passed","test_counts":{"total":3,"passed":3,"failed":0,"skipped":0},"simulated":false}

Docker unavailable:
{"status":"unavailable","test_counts":null,"simulated":false}

Confirmed empty suite:
{"status":"failed","test_counts":{"total":0,"passed":0,"failed":0,"skipped":0},"simulated":false}

Parse failure:
{"status":"error","test_counts":null,"simulated":false}

Simulated practice:
{"status":"passed","test_counts":null,"simulated":true}

WHY:
An additive nullable object preserves old integer consumers while removing the ambiguity between unknown counts and a genuinely empty run. Four counters with an explicitly combined failed/error equivalent avoid falsely claiming precise assertion-only failure counts or adding unnecessary collection/subtest metrics. Propagating one canonical object prevents API and desktop counters from drifting.

SEMANTICS AND READINESS:

| Situation | Connected status | Canonical counts | Readiness |
|---|---|---|---|
| Completed all-pass suite, positive total | passed | Exact nonnull counters; passed=total, failed=skipped=0 | Eligible for READY only with all existing original/state/security gates |
| Recognized failing suite | failed | Exact counters where trustworthy | BLOCKED |
| Recognized all-pass executed tests plus skips | passed | Includes skips in total | BLOCKED for full release readiness; UI explains skipped tests remain unverified |
| All skipped | failed | Zero passed, positive skipped/total | BLOCKED |
| Confirmed no tests collected/run | failed | Explicit measured zero counters | BLOCKED; No tests collected |
| Docker/image unavailable | unavailable | null | BLOCKED; Counts unavailable |
| Timeout | timeout | null, regardless of incomplete printed logs | BLOCKED |
| Unrecognized/truncated/inconsistent summary | error | null | BLOCKED; Could not determine test counts |
| Execution/setup/cleanup error | error | null unless an already completed trusted summary was captured; error still blocks | BLOCKED |
| Collection failure with no test-outcome summary | failed | null; collection errors are not fabricated executed test counts | BLOCKED |
| Practice fixture check | passed/failed + simulated=true | null | Only separately labelled PRACTICE COMPLETE; never real release readiness |
| Older connected payload lacking test_counts | existing status | Treat absent as unknown | Never show real passing counts or real READY from phase alone |

Full readiness is deliberately conservative: skipped tests cannot certify all-pass. READY requires status passed, canonical counts present/consistent, positive total, passed==total, failed==skipped==0, no runtime errors, unchanged original and existing session/applied-state gates. Existing security warnings continue to prevent an unconditional READY. A previous validated phase must not override a later unknown/error/unavailable result. UI independently checks these prerequisites; server remains authoritative.

REQUIRED CHANGES / OWNERS:
- backend/models.py: shared TestCounts and canonical fields in SandboxResult/ReleaseReadiness, preserve legacy fields with controlled projection. Friend 3.
- backend/services/sandbox.py: recognized-runner parsing for pytest/unittest/Node, skip preservation, consistent totals, explicit confirmed-empty detection, null for unavailable/timeout/parse failures. Retain fixed commands and sandbox controls. Friend 3.
- backend/services/release_readiness.py: gate on canonical known counts instead of zero defaults; consistent readiness projection. Friend 3.
- backend/session_models.py and services/sessions.py: propagate canonical counts, simulated=false and explicit error. Report endpoint already forwards Validation. Friend 3.
- Dart domain/workspace.dart: typed strict TestCounts, nullable count parsing, simulated flag, count-aware success/readiness getters. Missing legacy counts remain unknown. Friend 1.
- features/workspace/evidence.dart: total/passed/Failed-errors/skipped display, explicit unknown/empty/error messages, no green runner-success from status alone, simulated labels, count-aware readiness and exported evidence. Friend 1 + Friend 2.
- services/practice_service.dart: simulated flag, null real counts, separate practice completion. Friend 1 + Friend 2.
- Backend/Dart tests and documentation: boundary propagation and failure/regression cases. Project Lead reviews original protection and integration compatibility.

SUPPORTED PARSER SCOPE / LIMITS:
Support recognized completed standard summaries for the three existing fixed runners, including explicit skips and empty suites. For unittest, calculate successes from Ran N and failure/error/skipped totals rather than marking all N failed. If subtest/extended outcomes cannot be reconciled, counts are unknown. For pytest, collection errors and special outcomes such as xfailed/xpassed/deselected must not be silently collapsed; use null/error where a complete supported total cannot be established. For Node, cancelled or otherwise unclassified outcomes must not be silently counted as passes. Unsupported/malformed formats fail closed and are reported; this proposal does not promise universal runner-format detection or proof of test authenticity. Existing filtered-snapshot-not-production-certification notice remains.

ARCHITECTURE / CROSS-COMPONENT IMPACT:
Existing Sandbox → Backend → Dart/UI → Readiness flow and ownership remain. Shared response additions and conservative readiness behavior require approval. No architecture topology/provider contract, Docker isolation, project packaging or original-project mutation changes are proposed.

RISKS / COMPATIBILITY:
- Old desktop clients ignore additive counts/simulation fields and understand existing statuses; additional error status remains nonpassing in their existing string comparisons.
- New desktop with old backend treats absent counts as unknown and blocks a real READY display. This intentionally conservative downgrade is safer than inventing metrics; deploy paired updates for full results display.
- Legacy tests/manual SandboxResult construction must set canonical counts when claiming trusted successful evidence. Tests should not be weakened to accept unknown counts as success.
- Skip-aware full readiness may block runs previously marked READY; explain the incomplete coverage rather than silently accepting it.
- Parser limitations and output truncation can block otherwise passing executions when reliable counts cannot be recovered. Preserve diagnostics and distinguish infrastructure/parse problems from assertions.
- Real fixture counts certify only those fixtures, not the dummy project's full journey or live AI quality.

VERIFICATION AFTER APPROVAL:
1. Typed-model/parser regressions for all-pass, mixed pass/fail, skips/all-skips, confirmed zero tests, collection errors, malformed/truncated/unrecognized output, contradictory totals and strict invalid count types. Verify all three supported runners and documented unsupported outcomes.
2. Connected HTTP/API mapping tests from actual SandboxResult through Validation/report, including unavailable Docker/image, timeout and execution/parse errors. For unavailable testing, use an intentionally absent audit-only image reference or transport fixture; do not stop the user's Docker engine.
3. Dart parsing/rendering/export/readiness tests: exact counts, unknown counts, zero collected, all skipped, status passed with null counts, stale validated phase with unavailable/error counts, and simulated practice. Ensure labels are honest.
4. Real Docker through existing managed-copy flow: safe fixture suites passing/failing/skipping/empty/timed-out; capture exact counts and readiness. SDK/container inspection, cleanup and before/after original fixture hashes. Real connected propagation test can use provider transport fixtures for earlier gates but real Docker transport for validation; explicitly label that mix.
5. Run security-critical backend/project tests, Flutter analyze/test and Windows build as appropriate; retain exact commands, counts, errors/skips and warning evidence.

Docker availability: fresh Docker server-version check succeeded, engine 29.8.1, command exit 0. Previous DOCKER-VALIDATION-REPORT.md contains real passing/failing/timeout/isolation evidence, but F07 count contracts have not been implemented or runtime-verified. Recheck the trusted image before new real runs. No live AI calls are needed to verify count propagation.

RECOMMENDATION: Approve additive nullable test_counts + simulated flag + explicit error status, supported failed/error equivalent, conservative skip/unknown readiness policy, typed Dart/UI propagation and the regression/runtime plan.

TASK: Investigate F07 and propose before shared contract changes.
IMPLEMENTED: Read-only count/API/UI tracing and this proposal; Docker availability check only.
FILES CREATED/CHANGED: setup-evidence/F07-CONTRACT-PROPOSAL.md only for F07.
ARCHITECTURE IMPACT: Proposed cross-component metrics propagation, not implemented.
API IMPACT: Proposed test_counts/simulated additions and error enum expansion, not implemented.
DATA MODEL IMPACT: Proposed shared strict TestCounts + nullable evidence, not implemented.
SECURITY IMPACT: Identified unknown-count and skipped-evidence ambiguity; existing original protection unchanged.
TESTS: No F07 regression PASS claims; Docker availability succeeded only. Earlier Docker evidence explicitly separate.
KNOWN ISSUES: Count loss, skipped accounting and status/phase-only UI remain until approval/implementation; supported-summary parser limits documented above. Other findings and private AI verification are outside F07.
NEXT DEPENDENCY: Human approval of this concrete shared contract and readiness policy.
