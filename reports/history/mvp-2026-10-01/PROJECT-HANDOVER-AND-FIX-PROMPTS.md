Historical initial audit (2026-10-01), before later fixes. Read [the latest release audit](../../p06-p15/FULL-MVP-RELEASE-AUDIT.md) for current results. Prior missing/deprecated/unavailable findings below are historical evidence, not a claim that the fixes are absent.

# CodeProof project handover: working features, errors and fix prompts

Date: 2026-10-01 (Asia/Colombo)
Evidence base: integrated audit commit 911d45cc267d8972dd7b65d6cf260bd6e7a779db.
This is an evidence-based handover, not a new exhaustive scan or a claim that every defect has been found. Latest read confirms the integrated commit is unchanged. No application fixes were performed to write this report.

## Overall condition

CodeProof builds and starts. Project inspection, connected session opening and safe-copy Patch Lab operations have real evidence. The complete live AI -> explanation -> patch -> Docker -> readiness journey is not demonstrated. Feature verdict: 1 PASS, 6 PARTIAL, 11 NOT TESTABLE. Missing prerequisites are not proof of broken application code.

The main confirmed release-blocking defect is incomplete redaction of a hardcoded signing secret. Resolve it before sending this target to a live provider.

## What works

| Area | Evidence | Limits |
|---|---|---|
| Integration | Elevated fetch succeeded; backend fast-forward and Flutter clean merge | No push/main merge |
| Windows app | Release build succeeded; native welcome shell observed | Full connected navigation unverified |
| Flutter static checks | Analyze no issues; 7 tests passed | Practice/layout/dialog tests, not full live workflow |
| Backend | Retry 99 passed/1 skipped; project-wide 141 passed | Provider/Docker mocks in relevant tests |
| Backend startup | Intended launcher; actual /health 200; 35 OpenAPI operations | Route existence is not feature success |
| Project session | Real shipped Dart client and API opened separate dummy app | Native folder dialog unverified |
| Snapshot filtering | 23 files; venv excluded | Secret-redaction defect remains |
| Patch Lab | Rejects unsafe/original paths; valid patch changes registered temporary copy only; cleanup observed | Safe fixtures, not live AI proposal |
| Fail-closed gates | Analysis prerequisites and investigation/explanation gates enforced; readiness BLOCKED | Successful readiness unverified |
| Practice/demo | Explicit demo sequence, four hints, keyword evaluation, static patch, simulated tests/readiness work | Mock, not live AI/Docker |
| Original protection | 6,398 dummy hashes unchanged in attempted flow; original checkout 253 baseline hashes/HEAD/index unchanged | Complete successful journey not reached |
| Temporary light preview | Separate preview built and launched | No permanent selector; visual coverage not checked; preview no longer running at last check |

## Confirmed defects, gaps and setup problems

| ID | Priority | Finding | Type | Action | Responsible component |
|---|---|---|---|---|---|
| F01 | P0 | Hardcoded JWT signing-secret assignment survives Guardian redaction | Confirmed security defect | Redact sensitive source/config content before any provider use; regression tests | workspace/ + backend Guardian adapter |
| F02 | P1 | Missing OPENROUTER_API_KEY and CODEPROOF_MODEL produced analysis 503 | Environment blocker | Configure privately; validate actual provider transport after F01 | ai/ + backend startup |
| F03 | P1 | .env guidance does not match explicit launcher loading; example omits model | Setup/documentation gap | Make setup contract and launcher behavior consistent | backend/ + docs |
| F04 | P1 | Docker or trusted sandbox image unavailable | Environment blocker | Provision supported Docker/image and verify real isolation | sandbox/ + backend/ |
| F05 | P1 | Native connected UI journey unverified due window/input guards | Verification gap | Execute quiet-window/manual journey; fix only reproduced defects | desktop/ |
| F06 | P1 | Connected API lacks explicit three-way explanation classification | Inspected contract gap | Report classification consistently through backend and UI | ai/ + backend/ + desktop/ |
| F07 | P1 | Connected validation omits numerical test counts | Inspected contract gap | Carry actual runner counts through API and results UI | backend/ + desktop/ |
| F08 | P1 | Three controlled incidents not demonstrated; connected flow describes existing issues | Scope/implementation gap | Define and implement approved copy-only incident behavior if required | backend/ + Product |
| F09 | P1 | Full successful-flow original hash proof missing | Verification gap | Repeat hashes around real AI/patch/Docker journey | workspace/ + backend/ |
| F10 | P2 | google.generativeai support-ended warning | Dependency maintenance | Migrate existing provider adapter without changing external contracts | ai/ |
| F11 | P2 | datetime.utcnow and TestClient integration warnings | Dependency maintenance | Address timestamp semantics/dependency compatibility; meaningful tests | ai/ + backend/ |
| F12 | P2 | Desktop README claims missing integration/workflows that exist | Documentation defect | Rewrite from verified behavior; label demo and blocked features | desktop/ docs |
| F13 | P2 | Four Flutter dependency upgrade notices | Maintenance notice, not failure | Inspect constraints before targeted updates | desktop/ |
| F14 | P2 | App hardcodes dark theme; no permanent selector | Product limitation | Implement only if desired; temporary preview is separate | desktop/ |
| F15 | P2 | Initial pytest run had 48 WinError 5 setup errors | Local test-environment problem | Use unique writable basetemp; never delete user temp directories | test tooling |
| F16 | P2 | Pairing/port confusion and occupied port 8000 | Setup/usability problem | Better guidance and startup error handling | desktop/ + backend/ |
| F17 | P1 | Dummy target contains a hardcoded signing key | Separate target issue | Remediate only with separate target authorization; F01 remains CodeProof's duty | Dummy app owner |

No live-provider quality failure, real Docker failure, native results-screen defect or complete-flow corruption was proven. These checks were blocked/unexecuted. The external auth.py already uses password verification; do not invent the demo plaintext/hash bug for it.

## Earlier console errors explained

- WinError 10048 on 127.0.0.1:8000: another listener already owns that port. Start a new CodeProof backend on a free loopback port using the launcher's supported configuration; do not kill unrelated processes.
- GET / and /favicon.ico returned 404: not evidence of failed startup; these routes were absent. Use /health for health verification and /openapi.json for inventory.
- Pairing token: per-launch authentication credential generated by the CodeProof backend launcher. It must match the running service. A token printed by a launch that failed to bind cannot authenticate an unrelated existing server. Do not put tokens in reports.
- Port: the CodeProof service's loopback port, not the dummy app server port.
- Project path: the dummy project's filesystem folder, not its backend URL.
- FutureWarning for google.generativeai: deprecated SDK maintenance warning, not the port binding cause.
- Analysis 503: provider/model configuration absent in audit backend.
- Later 409s: workflow prerequisites were not satisfied; they do not prove evaluator/hint/patch logic is broken.
- Validation HTTP 200 with status=unavailable: request processed, but Docker execution unavailable; not a test PASS.
- Pytest WinError 5: inaccessible temp-directory fixture setup; complete retry succeeded with isolated basetemp.

## Tests and release prerequisites

Initial backend: 52 passed, 0 failed, 48 setup errors, 0 skipped, 40 warnings, exit 1.
Complete backend retry: 99 passed, 0 failed, 0 errors, 1 Docker skip, 274 warnings, exit 0.
Project Python: 141 passed, 0 failed/errors/skipped, 146 warnings, exit 0.
Flutter pub get/analyze/test/build all exit 0; 7 tests passed; analysis no issues.
Original Windows build: 54.6 seconds. Separate light preview: 66.0 seconds.

Before sign-off require sanitized live provider requests, representative real model outputs, all three explanation outcomes, real patch proposal/review/copy application, real Docker target tests with isolation/limits/timeout/cleanup evidence, honest results/readiness UI and unchanged original hashes.

## How to use the following prompts

Paste the common preamble with ONE numbered prompt at a time. Finish and review that task before starting the next. Run P01 first. P02/P03 prepare live prerequisites. Do not modify the audit evidence or preserved checkouts to implement fixes.

For cross-component architecture/API/data changes: inspect dependencies and present CURRENT, REQUEST, WHY, AFFECTED COMPONENTS, REQUIRED CHANGES, RISKS and RECOMMENDATION before implementation. The prompt requests that proposal first; obtain approval before changing protected architecture/contracts.

### Common preamble for every task

You are working on CodeProof. Read applicable AGENTS.md and setup instructions. Use the integrated audited commit 911d45cc267d8972dd7b65d6cf260bd6e7a779db as the evidence baseline. Preserve C:\Codeproof-main\Codeproof-main, C:\Codeproof-mvp-audit and C:\Codeproof-mvp-audit-worktree, including all untracked files and audit evidence. Create a NEW isolated Git worktree and a unique codex/ branch for this task; verify both do not already exist and never overwrite/reset existing work. Use elevation for authorized local worktree metadata writes when needed. Do not push, modify main/teammate branches, stop user processes or edit C:\New folder\CodeProof-DummyApp. Application fixes are allowed only in the new fix worktree. Follow Guardian-only reads, temporary-copy-only mutations and Docker-only target execution. Keep secrets out of code/logs/reports. Do not replace real integration behavior with mocks to make checks pass. Report architecture/API/data impacts before protected cross-component changes and obtain approval. Run focused meaningful checks and required relevant suites. Finish with task, implemented, files changed, impacts, tests, known issues and next dependency. Do not start unrelated implementation.

### P01 — Fix Guardian signing-secret redaction (first)

Investigate F01 using runtime-secret-filter-check.json and the Guardian/SecretFilter/provider-context boundaries. Use synthetic harmless secret fixtures, never print the dummy signing key. Fix source/config signing-secret redaction before provider serialization, preserving useful nonsensitive code context. Cover supported assignment/config representations relevant to the scanner. Verify source literals cannot reach an intercepted provider payload, original bytes stay unchanged, and existing .env/path protections still pass. Report unsupported representations rather than promising perfect secret detection. Do not make live provider requests until this protection is verified. Run security-critical workspace/backend tests. Explain exactly what was leaking and which paths are now covered.

### P02 — Make AI setup and launcher reliable

Investigate F02/F03. Document the actual provider abstraction, environment variables and intended token-generating launcher. Reconcile .env instructions with real loading behavior; add a nonsecret CODEPROOF_MODEL example and actionable configuration errors. Keep process variables authoritative if loading local files. Propose any cross-component contract changes before implementing. Do not solicit or display API-key values in chat. After P01 is verified and private credentials/model are available, start your backend on an available loopback port and verify health plus an actual non-mocked provider analysis against a safe fixture. Check malformed output, authentication failure, timeout and unavailable provider handling. Separate mocked regression results from live evidence. If credentials are absent, complete safe setup fixes and report live verification NOT TESTABLE.

### P03 — Provision and verify real Docker validation

Investigate F04 without interrupting existing Docker/user workloads. Check Docker CLI, daemon, supported container mode and required trusted image. Explain missing prerequisites; obtain approval for any installation or host-setting changes outside existing authorization. Use the repository's sandbox image/build instructions. Run target code only through CodeProof's Docker path against a disposable fixture copy. Verify no original mount/write, network disabled by default, non-root execution, required capabilities/resource limits, timeout, stdout limits and cleanup on success/failure/timeout. Record actual test counts and readiness; do not use demo counts or mocked lifecycle as live PASS. Report remaining limits, including whether disk limits are actually enforced.

### P04 — Carry explanation classifications through backend and UI

Investigate F06. First propose the smallest compatible contract change supporting CORRECT, PARTIALLY_CORRECT and INCORRECT, with score/feedback and existing explanation-before-patch gates preserved. Map AI output, typed backend model and Dart/UI consumers; obtain approval before changing shared contracts. Then implement consistently. Use deterministic provider-output fixtures for regression tests and separately run live evaluation when prerequisites exist. Verify partial/incorrect explanations cannot unlock patching, correct explanations can, and malformed provider outputs fail safely. Do not use keyword demo results as proof of real evaluation quality.

### P05 — Expose actual validation test counts and honest results UI

Investigate F07. Trace real SandboxResult counts to connected API models and Dart results/readiness UI. Propose compatible typed fields for total/passed/failed/skipped or supported equivalents, define unavailable/error semantics without inventing zero-success results, and obtain approval before shared contract changes. Implement approved fields consistently. Verify failing tests, all-pass tests, no tests collected, unavailable Docker, timeout and parse failures. Ensure UI labels simulated results and readiness never treats unknown/unavailable counts as success. Include real Docker evidence when available.

### P06 — Define and implement three controlled challenges safely

Investigate F08 and the original MVP scope. List existing real and demo challenge behavior. Propose three deterministic supported incidents, their educational goals, prerequisites and restoration rules; do not assume the external dummy has the bundled credential bug. Obtain architecture/API approval before implementation. Create incidents only in registered temporary copies, never originals or host-executed target code. Bind challenge/hints/explanations/patch expectations to the incident actually present. Verify reproducibility, teardown, copy ownership, original hashes and Docker validation. Label any remaining static practice behavior explicit.ly

### P07 — Verify the complete connected Windows desktop journey

Work from the integrated fixes accepted so far. Build and launch the actual Windows app; start a new correctly configured CodeProof backend on a free loopback port. Do not reuse unrelated services. Select the external dummy read-only or another explicitly approved fixture. Record before hashes. Execute launch -> project selection -> analysis -> skill map -> challenge -> investigation -> four hints -> explanation/evaluation -> patch generation -> review -> managed-copy application -> Docker tests -> results -> readiness -> after hashes. Exercise correct/partial/incorrect explanations and failure states. Use fresh UI observations; if automation is unavailable, list precise manual checks. Fix only reproduced desktop-local defects in your fix worktree; propose shared-contract changes before editing. Stop at the exact missing prerequisite rather than fabricating success.

### P08 — Migrate the deprecated Gemini adapter

Investigate F10 and all actual google.generativeai usage. Check current official Google SDK documentation before selecting the supported replacement. Preserve the provider abstraction and public AI/backend contracts. Migrate the existing adapter's request/response/error behavior, dependency declaration and provider-specific tests without redesigning unrelated providers. Verify model selection, credentials, response parsing, retries/timeouts where supported, and redacted errors. Use transport fixtures plus a separately labeled live smoke test if private credentials exist. Do not suppress the support-ended warning without replacing the deprecated usage.

### P09 — Resolve Python warnings and dependency compatibility

Investigate F11 and saved warning logs. Fix deprecated UTC construction with timezone semantics checked against stored/API timestamps; do not silently change timestamp formats/contracts. Inspect the FastAPI/Starlette/httpx compatibility responsible for TestClient warnings and choose a compatible constrained set using official documentation. Avoid blanket upgrades. Verify serialization, ordering/time comparisons and test-client behavior. Run affected suites and report warnings before/after, dependency versions and remaining warnings. Handle architecture/API approvals if semantics change.

### P10 — Correct documentation and mock labeling

Investigate F12 and setup documentation against current integrated behavior. Rewrite desktop/backend startup and feature documentation to distinguish connected services, static practice/demo, mocked automated tests and live prerequisites. Document Guardian/temp-copy/Docker boundaries, actual launcher, matching pairing token/port, project filesystem path, health endpoint and provider/model setup without secrets. Clarify .env behavior after P02 and preserve accurate missing/unverified labels. Check practice/results/readiness UI wording; propose cross-component changes before implementation. Do not claim live AI/Docker support based solely on file existence or demo responses.

### P11 — Make Windows startup, pairing and test setup errors actionable

Investigate F15/F16 and original WinError 10048/pairing confusion. Preserve per-launch token authentication and loopback binding. Inspect supported port configuration; never kill unrelated listeners or silently connect to an unrelated service. Improve actionable busy-port/missing-token/invalid-port/wrong-token handling and tell users to use the CodeProof service port plus dummy filesystem path. Keep tokens out of error logs. Verify correct/wrong token, invalid/busy port, backend unavailable and launcher exits. For pytest, document/use a new writable basetemp with safe containment checks; do not delete existing temp trees. Propose shared API/UI changes before editing.

### P12 — Add optional permanent light mode (only if wanted)

The latest preview changed colors only in a separate copy. Inspect the real hardcoded theme/palette, all direct color uses and native title-bar behavior. Implement a desktop-local light/dark choice with a consistent readable palette, input/dialog/code/diff/status colors and accessible contrast. Keep dark as the current default unless requested otherwise. Define preference persistence and provide a session-only choice if needed. Do not change backend contracts or target behavior. Run flutter analyze/test/build and visually verify startup, connection dialog, workspace, review and results in both themes. Do not count the earlier preview as complete visual verification.

### P13 — Review Flutter dependencies without blanket upgrading

Investigate F13 using current constraints and official package release notes. Identify which newer packages are transitive and whether updates address a concrete bug/security/compatibility issue. Make the smallest justified desktop-only dependency update, or report no update needed. Preserve lockfile reproducibility. Run pub get, analyze, tests and Windows build, and check native behavior. Do not upgrade packages simply to eliminate update notices.

### P14 — Separate dummy-app signing-key remediation

F17 belongs to the selected target, not CodeProof. Do not edit C:\New folder\CodeProof-DummyApp without explicit separate authorization. Inspect only and propose a target-specific fix using a separate target worktree/copy: environment-supplied signing key, clear missing-key behavior, no insecure production fallback, and a development fixture for tests. Consider existing token invalidation and configuration migration. Keep actual secret values out of output. CodeProof F01 must still be fixed independently; a cleaner target is not a substitute for Guardian protection.

### P15 — Final release audit after fixes

Do not implement fixes in this task. Assemble approved fix branches in a NEW release-audit worktree; report starting commits and stop on conflicts. Preserve prior checkouts/evidence. Run complete backend/project Python suites, Flutter pub get/analyze/test/build, isolated audit backend health/OpenAPI and the real native/AI/PatchLab/Docker journey. Hash originals before/after, verify redacted provider payloads, test all explanation outcomes, unsafe patch paths, container limits/timeout/cleanup and honest readiness. Produce MVP-01 through MVP-18 matrix with exactly one PASS/PARTIAL/MISSING/BROKEN/NOT TESTABLE status per feature, real/mock evidence, blockers and owners. Save commands/exits/counts/warnings and report current audit-owned processes. Do not push/merge main or claim unexecuted checks passed.

## Recommended order

P01 -> P02 -> P03 -> P04/P05 -> P06 -> P07 -> P15.
Handle P08/P09/P10/P11 before release as evidence warrants.
P12 is optional product work. P13 is targeted maintenance. P14 is a separate authorized target task.
Do not run these as uncontrolled parallel implementation tasks.

## Existing full evidence

FULL-MVP-FEATURE-AUDIT.md contains the complete feature matrix, route inventory, warnings, architecture findings, command table and evidence index.
LIGHT-THEME-RUN-REPORT.md records the separate preview; it did not change the application audit verdict.
