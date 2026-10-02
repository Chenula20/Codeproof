# Demo separation: architecture impact and proposed implementation

Status: APPROVED AND IMPLEMENTED. The user approved full separation, application to the original path and the isolated Windows rebuild in this chat on 2026-10-02.

CURRENT
- The Windows desktop imports PracticeWorkspaceService and exposes Open sample project.
- backend.main registers both authenticated /v1 session routes and legacy project/challenge/patch/sandbox/release routes plus /demo fixtures in one process.
- The connected session service silently chooses demo-project when the supplied project path is empty.
- demo-project is the Student Event sample. training-project is a healthy three-test controlled-incident fixture. frontend is the browser presentation demo. remediation/dummy-app is tooling that prepares a separate external dummy copy; it is not that external app itself.
- C:\New folder\CodeProof-DummyApp already exists outside the main CodeProof repository. Its files are not being changed by this task.
- The original checkout is on feature/backend-integration at 2874de1. The v10 release and isolated authentication copy are based on main commit 9c856e0. These are different baselines; replacing the original checkout wholesale with v10 would discard its branch context and is not proposed.

REQUEST
Separate all demo content from the main app and original project, while retaining usable demo copies independently.

WHY
Main-app analysis, patches and validation should refer to a project the user deliberately selects. Simulated sample data should not be bundled into the normal application or selected through an empty path.

AFFECTED COMPONENTS
Desktop startup/controller initialization; backend app composition and session opening; sample projects/browser demo; tests that currently assume a sample is always installed; release/source packaging and documentation. Guardian, provider abstractions, managed-copy patch safety and Docker execution controls remain the main app pipeline.

REQUIRED CHANGES
1. Preserve the demo/training/browser/remediation content separately, including the already requested and Docker-verified authentication correction in the sample copy.
2. Remove the production desktop import of its in-memory sample service and the Open sample project startup action. Keep connection, inspection, coaching, patch review and validation for explicitly opened projects. Retain synthetic test fixtures outside the shipped application.
3. Stop mounting /demo and the legacy sample-dependent endpoints in the normal backend. Preserve their implementations/contracts in the separate demo package/service. Main /v1 response schemas, pairing authentication and loopback controls remain unchanged.
4. Reject missing/blank selected-project paths with an actionable error before filesystem access. There is no automatic sample fallback.
5. Remove root demo-project, training-project, browser-demo frontend and dummy remediation content from the cleaned main source distribution; store independent preserved packages beside the main app. Keep historical branch archives as history, excluded from the main runtime/source package.
6. Adapt separation-sensitive tests, verify real-project opening and main route isolation in constrained Docker, run desktop analyze/tests, and rebuild the native Windows release in an isolated copy if the requested exception is approved.
7. Apply equivalent verified changes to the original checkout only if the direct-write exception is approved. Preserve its current branch and untracked content. A separately reviewed v10/main patch is required because the two baselines differ.
8. Create a file-by-file implementation log, troubleshooting guide, package hashes, rollback instructions and final implementation report. Publishing to GitHub can use the existing push authorization after validation; do not force-push or rewrite history.

RISKS
- Browser/legacy demo clients must target the separate service; their endpoints will intentionally no longer be served by the main service.
- Sample-dependent tests must use explicit separate fixtures. Main tests must prove the app works when demos are absent.
- Merely moving folders would leave the compiled practice app in the existing EXE. A rebuilt EXE is required to complete the runtime separation.
- Existing branch archives and older release ZIPs contain historical demos. They remain historical artifacts, not the new main runtime.
- Source baselines differ. Apply only reviewed separation changes to the original checkout; do not reset, clean or overwrite unrelated files.

RECOMMENDATION
Approve full separation and an isolated native Flutter validation/build. Preserve independent demos and existing archives; require deliberate project selection in the main app.

APPROVAL REQUIREMENT
AGENTS.md Architecture Protection Rule 3: Do not proceed with architectural change unless explicitly approved. Its AI Permissions and Sandbox Rules also restrict writes to temporary copies and execution to Docker. Both requested approvals were received before architecture implementation and original-checkout changes.
