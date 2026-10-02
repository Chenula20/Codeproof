# CodeProof demo separation implementation report

TASK: Fully separate demo/dummy projects from the main and original CodeProof application; deliver two clearly labelled local folders, troubleshooting and the last-24-hour change log.

IMPLEMENTED
- CodeProof Main App: independent main source (129 files), Windows runtime (12 files), version 1.0.10+11, source/runtime ZIPs, package hashes and separate backend requirement.
- CodeProof Demo App: independent preserved v10 demonstration desktop/runtime and source, Student Event sample with the requested authentication fix, training project, browser presentation demo and dummy-copy preparation tooling. Its Demo ZIP excludes the local original-checkout rollback directory.
- Removed the main production PracticeWorkspaceService and sample startup action. Main startup connects an explicitly selected project; a blank folder is rejected in the dialog.
- Main backend exports only /health and authenticated /v1 sessions. Demo/legacy routers and static demo services are physically removed from active main source. Blank/missing/whitespace paths are rejected before Guardian access. Controlled demo incidents are rejected; existing /v1 response fields are retained and incident fields are empty.
- Preserved synthetic widget fixtures only under desktop/test/support. They are injected in tests and not imported into the main application executable.
- Applied equivalent verified separation to C:\Codeproof-main\Codeproof-main while retaining its feature/backend-integration branch and older /v1 contracts. This older checkout has no tracked Flutter app source. Its existing release path now contains the rebuilt main EXE; complete matching Flutter source is in the labelled Main App folder.
- Removed originals and prior changed-file versions are preserved under CodeProof Demo App\original-checkout-rollback. Existing untracked desktop tooling/platform files, reports, other worktrees, branch snapshots and external C:\New folder\CodeProof-DummyApp are preserved.

FILES CREATED/CHANGED
The complete main source action list is MAIN-SOURCE-CHANGES.json and the original-checkout action log is ORIGINAL-CHANGE-LOG.json. Key files: backend/main.py; backend/routers/__init__.py; backend/services/patch_lab.py; backend/services/sessions.py; backend/tests/test_services.py; backend/tests/test_demo_separation.py; desktop/lib/app/app.dart; desktop/lib/domain/workspace.dart; desktop/lib/features/startup/startup_screen.dart; desktop/windows/runner/main.cpp; desktop/pubspec.yaml; desktop/test/support/practice_fixture.dart; desktop/test/demo_separation_test.dart; adapted widget/controller/evaluation/count tests; README and component guides; sandbox requirements comment; separate runtime/demo deliverables. Removed sample-dependent routes/services, demo/training/browser projects and dummy-copy tooling are independently preserved.

ARCHITECTURE IMPACT
Approved split between the real-project main application and independent demonstrations. The main Flutter -> Guardian -> authenticated backend -> AI -> managed-copy Patch Lab -> Docker -> readiness pipeline remains. Demo composition is preserved in its independent package.

API IMPACT
Main legacy/demo endpoints intentionally cease to exist (404). The separate demo package preserves them. Main /v1 request/response models and pairing boundary are retained. Empty selections now return actionable 400 instead of implicitly opening a sample. V10 controlled incident requests return actionable 400 and advertise no incidents. Original branch schemas remain unchanged.

DATA MODEL IMPACT
No persistent data migration. In-memory V10 incident fields are empty. Original branch models are not replaced with V10 models. Original dummy databases/environment files are not included in the published demo package.

SECURITY IMPACT
Selected target originals remain read-only. Guarded snapshots, managed-copy patching, provider-consent and ephemeral constrained Docker execution remain. Backend pairing/loopback/Origin restrictions remain. Main no longer exposes sample endpoints or selects an implicit sample. Source/Demo packages contain tracked reviewed source and synthetic fixtures, excluding private environment files, dependency directories, databases and Git metadata. Local rollback is not published.

TESTS
- V10 main Python suite in constrained Docker: 464 passed, 2 skipped (Windows junction and real Docker controller availability); zero failures/errors.
- Flutter analysis: no issues. Flutter regressions: 38 passed. Native Windows release build: passed.
- Original-branch backend suite in a separate constrained Docker copy: 70 passed, 2 skipped; 239 existing SDK/UTC warnings retained.
- Independently packaged main isolation suite: 6 passed, including route inventory, blank-path rejection before Guardian and explicit selected-project integrity.
- Main ZIP verification: all 129 source and 12 runtime files match disk SHA-256 values. Original EXE matches the main release hash.
- Native UI inspected: window title CodeProof Main App; main welcome screen has Connect your project and no Open sample project button. No selected-project/provider journey is claimed by this visual check.
- Preserved Student Event authentication source: previous constrained Docker evidence records 52 passed, four existing deprecation warnings. Its stored bcrypt hash cannot be used directly as a valid password.
- Initial checks caught a stale router package export and two tests still assuming automatic sample startup; both were corrected and the relevant suites rerun successfully.

KNOWN ISSUES
Backend and Docker are separate requirements, not embedded in the EXE. Live AI/provider quality and an end-to-end native connected-project journey are not established by these checks. Environment-specific skipped tests are recorded, not claimed as passed. Old branch/dependency deprecations remain. The independent demo desktop is the preserved v10 build; the authentication correction is in its Student Event source, not in that desktop's simulated offline fixture. Historical merged/branch packages still contain older demos and are explicitly superseded. Original checkout changes are uncommitted on its current branch; main publication is performed from the validated isolated branch without rewriting original branch history.

NEXT DEPENDENCY
Desktop/backend owners should use CodeProof Main App for real projects and CodeProof Demo App for demonstrations. Existing browser/legacy demo clients must use the demo service. Use matching main backend/source for newest behavior; the original checkout deliberately retains its older backend baseline. Review package manifests and troubleshooting before sharing or deploying either app.
