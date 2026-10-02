# CodeProof v.10 integration impact

CURRENT: main already contains the AI analysis/coaching/patch-generator branches, backend integration, migrated Flutter v2 desktop, and the tested release fixes. Four of the 19 captured branch references lack direct ancestry: local Flutter v1, its remote initial parent, the Guardian contract branch, and master. Their supported functionality was migrated or subsequently replaced by the current implementations.

REQUEST: Reconcile all captured branch histories into one application and build a matching Windows release from the canonical root source.

WHY: A branch archive is not a runtime. The current root app already combines the maintained component implementations. Reintroducing historical backend/app.py, backend/service.py, sandbox/runner.py, workspace/security.py, and their old models would create conflicting APIs and undo later security and workflow fixes.

AFFECTED COMPONENTS: AI/Guardian source-contract reconciliation; backend and sandbox historical implementation review; Flutter release build; Git ancestry and integration evidence. Existing root application implementations remain canonical.

REQUIRED CHANGES: Resolve Guardian merge conflicts by retaining the evolved typed ProjectSnapshot, PatchRequest, ContextBuilder and current tests. Reconcile superseded unrelated Flutter/master histories without replacing active code. Verify all 19 captured commits are ancestors. Change the desktop release version to 1.0.10+10, run isolated Python tests and native Flutter checks/build, and provide merged source plus the full Windows runtime folder.

RISKS: Older branch implementations are incompatible with current shared models and security gates. Their files remain available in the existing branch archive rather than becoming a second active backend. The executable still depends on the documented local FastAPI backend, configured private AI provider/model, and Docker for target validation. Repository-wide test discovery can traverse archived snapshots, so tests use explicit root test paths. Full live AI/native workflow quality is distinct from automated regression/build checks.

RECOMMENDATION: Retain the current architecture and shared APIs; reconcile redundant history and build the latest maintained app. No cross-component architecture, API contract or data model change is proposed or performed. Bundling the backend into one self-contained executable is outside this integration and would require a separate architecture approval.

EXECUTION RULE: AGENTS.md says "All code execution happens in Docker containers." Python regression tests run in the existing trusted image with network disabled, read-only source and resource limits. A native Windows Flutter test/build exception must be explicitly approved before those commands run; the Windows SDK is installed on the host, not in the Linux Docker test image.
