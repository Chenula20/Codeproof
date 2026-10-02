# Break My App and hints — implementation report

TASK: Add Break My App and hints to the CodeProof Main App.

IMPLEMENTED: Separate Break My App, Investigate, and Hints controls at narrow and wide window sizes. Python/Node source choices come from the explicitly selected Guardian snapshot. A fixed Docker test runner must produce a completely passing healthy baseline before a fresh managed copy receives a marked syntax fault. A second Docker run must reproduce that specific fault before the session switches copies. Four progressive hints run locally without provider access. Explicit AI consent is required for explanation review and patch generation; reviewed patches and measured Docker validation still gate readiness. Closing/reopening discards the fault. The Main App has no bundled sample, demo routes, or implicit project selection.

CURRENT: Main previously exposed observed-issue investigation and provider-generated hints, but no supported controlled incidents.
REQUEST: Add safe real-project controlled faults and visible progressive hints.
WHY: Let users reproduce and understand a failure in their own temporary project copy while keeping the separate demo package independent.
AFFECTED COMPONENTS: Flutter workspace controls, local session service, regression tests, Windows release package.
REQUIRED CHANGES: Server-derived incident catalog, baseline/fault Docker evidence, atomic copy selection and rollback, local hints, existing consent entry point, responsive controls, longer bounded client wait for two Docker runs.
RISKS: Unsupported languages, missing prepared dependencies/image, pre-existing failures, skipped tests, and unexercised modules prevent injection. Test output is evidence for review, not a production or security certification.
RECOMMENDATION: Implement within the existing Guardian/session/Docker architecture and existing API models, as requested by the user.

FILES CREATED/CHANGED:
- backend/services/controlled_faults.py (created)
- backend/services/sessions.py
- backend/routers/sessions.py
- backend/tests/test_controlled_faults.py (created)
- backend/tests/test_demo_separation.py
- desktop/lib/features/workspace/workspace_shell.dart
- desktop/lib/features/workspace/coach.dart
- desktop/lib/domain/workspace_controller.dart
- desktop/lib/services/workspace_service.dart
- desktop/lib/ui/glass.dart
- desktop/test/break_hints_test.dart (created)
- desktop/test/incidents_test.dart
- desktop/pubspec.yaml (1.0.10+12)
- README.md
- docs/break-my-app-hints-report.md (created)

ARCHITECTURE IMPACT: No architectural replacement. Controlled-fault preparation remains in the existing backend session service and Patch Lab managed-copy boundary; target execution remains in restricted ephemeral Docker containers.
API IMPACT: No routes or schema changes. Reuses ChallengeRequest.incident_id, SessionView.supported_incidents/active_incident, and existing challenge/hint/analysis endpoints. Supported incident requests now perform the requested controlled-fault workflow. Explicit AI analysis may be enabled during a controlled investigation; observed investigations keep their existing AI prerequisite.
DATA MODEL IMPACT: No persistent storage changes or shared wire model changes. Ephemeral Session holds the chosen controlled fault and healthy target content for grounded hints.
SECURITY IMPACT: Server controls eligible paths and fixed runners; unknown IDs are rejected. Original hashes checked before and after Docker execution. Passing baseline required; unrelated failures, absent coverage, timeouts, unavailable Docker, and cleanup errors fail closed. Candidate integrity checked before selection. Original files never patched. No provider access for local hints; AI opt-in enforced by backend and UI. Existing authentication, loopback destination, redaction, reviewed-patch scope, container limits/no-network, and cleanup remain intact.
TESTS: 485 backend/AI/Guardian tests passed in a constrained no-network Docker container; 2 pre-existing environment/platform tests skipped. 41 Flutter tests passed, including narrow/wide real-main local-hint flow and unsupported-project refusal. Flutter analyze: no issues. Windows release build: passed. Live authenticated backend trials using actual Docker passed for python-pytest, python-unittest, and node-test, each with four local hints, real syntax-failure evidence, BLOCKED readiness and unchanged original fixture hashes. Live uncovered-module and failing-baseline trials returned 409 without starting a challenge. No remaining codeproof test containers after trials.
KNOWN ISSUES: Controlled fault type is currently syntax failure in .py/.js/.mjs/.cjs modules. Catalog is bounded to 60 module/runner choices, excludes tests/hidden/generated directories, and requires existing runnable tests and a prepared local image. Baselines with skips or unknown counts are refused. Actual external AI-provider calls were not made; provider HTTP transport tests verify the review/patch flow. The two skipped tests cover Windows junction behavior and actual Docker control from the outer isolated test container; separate Windows live backend trials verified all three runners. The old feature/backend-integration checkout retains its pre-existing dirty source state; the installed Main App source and GitHub main are the current runtime source. Restarting a backend loses its ephemeral sessions; reconnect/reopen in the new executable.
NEXT DEPENDENCY: Use the updated Main App backend source with the updated executable. Backend/sandbox owner supplies prepared dependency images for target projects. Future language/fault types require a tested catalog implementation; desktop and backend must continue honoring explicit AI consent and existing session contracts.
