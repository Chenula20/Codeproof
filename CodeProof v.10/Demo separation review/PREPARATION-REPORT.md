# Preparation report

TASK: Separate demo/dummy content from the main and original CodeProof project; provide troubleshooting and a change log for the last 24 hours.
IMPLEMENTED: Dependency inspection, concrete architecture proposal, four preserved ZIPs covering 59 tracked files, available Git commit/file history and reflog evidence, pending-change record, troubleshooting guide and copied authentication-test evidence. Separation implementation is pending the requested architecture/exception approvals.
FILES CREATED: ARCHITECTURE-IMPACT.md; CHANGES-LAST-24-HOURS.md/.json; LOCAL-REFLOG-LAST-24-HOURS.txt; PENDING-STATE.txt; TROUBLESHOOTING.md; PRESERVATION-MANIFEST.json; four preserved ZIPs; AUTH-FIX-DOCKER-TESTS.log; PREPARATION-REPORT.md.
ARCHITECTURE IMPACT: None applied. Proposed desktop/backend/demo/package separation is described in ARCHITECTURE-IMPACT.md.
API IMPACT: None applied. Proposed main removal of demo/legacy routes; their contracts preserved separately; /v1 response formats retained.
DATA MODEL IMPACT: None applied.
SECURITY IMPACT: No original project mutation or provider request. ZIPs include tracked sample/tool files only, not untracked databases, private environment files or dependency directories. Rejecting implicit sample selection is proposed, not yet implemented.
TESTS: Existing authentication correction evidence: 52 passed, four deprecation warnings in constrained Docker. New ZIP verification and log completeness checked separately. No new app runtime or build is claimed.
KNOWN ISSUES: Full separation and rebuilt EXE pending approval. Original checkout and v10 have different baselines. Git cannot reconstruct every uncommitted intermediate edit.
NEXT DEPENDENCY: Desktop and backend owners must use the separated main/demo entry points after implementation. Await the architecture and original-write/native-build choices presented to the user.
