# CodeProof remaining MVP completion report

Date: 2026-10-02. Worktree: C:\Codeproof-mvp-release-completion. Branch: codex/mvp-release-completion. Base: freshly fetched origin/codex/fix-ai-setup at 6040f8e5416d75481b37e2a52fae0928c3ca9661.

Implemented and tested: Guardian credential-context correction; hardened isolated dummy-copy preparation; environment-only signing; root test/import/HTTPX compatibility; reviewed trusted image provisioning; healthy copied database startup; new security/static regressions; updated Windows release package. Full connected release sign-off remains pending usable live model configuration and reliable native interaction. No claim that every possible defect or secret representation is covered.

## Git and scope

Fetch: git fetch origin --prune succeeded (exit 0) before creating this NEW worktree. No stale fallback. No new integration merges were required: the base already includes the clean backend fast-forward at 2874de18cfa1ed9fabbf04fa4f3b9af694e895a4 and Flutter merge parent e8ebf7c657db5379b98a384c947250e8096499db via 911d45cc267d8972dd7b65d6cf260bd6e7a779db. This is inherited ancestry, not newly performed merges. Before publication, freshly fetched main is 6efa548ab78a2b93075a395b777b2fe30206f403 and is an ancestor of this worktree; teammate heads are unchanged. The user subsequently explicitly authorized publishing CodeProof to GitHub main. Publication uses a normal fast-forward push from this isolated worktree; no force push or original-checkout branch/index change. This request supersedes the earlier branch-only publication restriction.

Existing original/fix/audit folders, indexes and HEADs are checked separately in PRESERVATION.json. Full hash inventories stay local; only reviewed count evidence is published. Git shared metadata changes are limited to authorized fetch/worktree/isolated-branch commit/remote-main push operations. Generated Flutter newline metadata stays uncommitted.

## Checks

| Check | Passed | Failed | Errors | Skipped | Warnings | Exit |
|---|---:|---:|---:|---:|---|---:|
| Complete backend Python | 265 | 0 | 0 | 0 | 0 | 0 |
| Complete final project Python | 250 | 0 | 0 | 0 | 0 | 0 |
| Focused signing/context/provider | 171 | 0 | 0 | 0 | 0 | 0 |
| Flutter tests | 37 | 0 | 0 | 0 | None reported | 0 |
| Flutter pub get | completed | — | — | — | Four constrained-package notices | 0 |
| Flutter analyze | no issues | 0 | — | — | No analyzer findings | 0 |
| Windows release build | built | — | — | — | Four package notices; no failure | 0 |
| Python pip check | no broken requirements | — | — | — | 0 | 0 |
| Healthy copied dummy, real Docker | 32 | 0 | 0 | 0 | 66 DeprecationWarnings | 0 runner |
| Copied signing checks, real Docker | 8 | 0 | 0 | 0 | 4 DeprecationWarnings | 0 runner |

The 515 Python tests include deterministic provider transports and real available Docker tests. They do not establish live model quality. Python warning classes were promoted to errors in CodeProof suites. Trusted repository tests/builds ran on the host as authorized; copied target code and startup subprocesses ran only through the production CodeProof Docker path.

Reproductions: nonsensitive credential plumbing 11 failures/6 passes before correction; external-copy hard-link escape 1 failure/3 passes before hardened adapter; harmless filtered signing fixture 6 failures/2 passes before environment enforcement; initial dummy discovery had unknown counts and missing main; intermediate copied dummy 31 passes/1 actual initialization failure; final healthy reference 32/32. Initial failed audit helper rejected Windows backslash paths before execution; corrected helper uses production capture normalization. Historical failures are retained locally, not recast as successes.

## Implemented and security impact

R01: workspace/secret_filter.py and tests/test_credential_context.py preserve Python credential parameter references, public field lookups, Depends calls, hashing calls and SQLAlchemy columns without embedded literal values; annotation whitespace handled. Source/config scalar literals and embedded credential/signing values remain redacted. Existing signing-specific assignment/config protections, .env/path exclusions, provider serialization interception and original-byte checks pass. Supported hashing/context fixes do not resolve arbitrary computed values, aliases, obfuscation, credential values concealed as lookup/dictionary labels or unsupported syntax. Ambiguous filtered representations need sensitivity review; snapshots may differ semantically from originals.

R02: remediation/dummy-app contains reviewed copy tooling, noncollectable Docker test templates and trusted dependency image configuration. It refuses overlapping/existing output, uses hardened Guardian capture and removes the copied signing literal. Both JWT encode/decode use the same validated CODEPROOF_DUMMY_SIGNING_KEY process value; missing/empty/short/whitespace-only input fails safely with no fallback. Synthetic fixture keys test signing, mismatch, rotation and configuration failure. Private production deployment is untested. Key rotation requires restart and invalidates prior tokens; reauthentication is required. Length validation does not certify entropy. Original signing material was neither printed nor committed.

R03: the healthy copied reference initializes the existing database schema and verifies a fresh subprocess/database inside Docker. Tests use explicit HTTPX ASGITransport and isolated databases. Public event listing remains public; protected mutation/auth checks remain. No CodeProof architecture, API or data model change. No new host target runner, provider selection, sandbox command, secret forwarding or shared contract was added. Previously approved classifications, score >=0.7/CORRECT gate, immediate resubmission revocation, nullable measured counts, fail-closed readiness and exact-manifest LF incidents remain passing.

Ownership: Guardian/AI boundaries — Project Lead; target provisioning/sandbox — Friend 3 plus dummy owner; Flutter/native verification — Friend 1. Reviewers independently traced the signing boundary and found the linked-source copy concern, which was reproduced and fixed. No prohibited direct Flutter-provider call, provider access to originals, bypass of connected Guardian capture, patch outside registered copies or original-project execution was introduced.

## Runtime journey, prerequisites and native limits

Own intended launcher: python -u -m backend, loopback port 58305, owned PID 16316. It generated a valid-length token held only in memory. /health returned 200; missing/wrong bearer token returned 401; / and favicon are not frontend routes. The original dummy opened through the real connected API (24 filtered files), local inspection returned 200, sessions closed and original bytes matched. The owned backend stopped after checks; this port is historical evidence, not a current pairing instruction.

Private configuration was read only in memory from inherited process values/previous private CodeProof configuration. Process values stayed authoritative; no environment file or credential was copied/committed. Credential presence is not proof of validity. The model was still provider/model-id, an example rather than a usable selection. A non-mocked harmless analysis request returned 503: Replace the CODEPROOF_MODEL example provider/model-id with an available OpenRouter model ID, then restart the backend. No external provider request was sent. Live analysis, hints, three-way evaluation and patch quality are NOT TESTABLE in this run; this is a configuration prerequisite, not a proven provider implementation failure.

Actual connected API flow with deterministic provider HTTP transport separately completes analysis -> challenge -> explanation -> proposal -> managed application -> real Docker -> readiness. Four hints, correct/partial/incorrect/malformed outcomes and immediate resubmission revocation pass regressions. New OpenRouter fault fixtures cover auth 401, missing model 404, unavailable 503, timeout, connection error, malformed JSON, invalid schema and empty response, both during analysis and resubmission. Existing safe backend errors remain generic HTTP 500; details are not leaked, originals remain unchanged, prior approval is revoked and patching stays 409-blocked. These fixtures are not live quality evidence; a richer typed/actionable provider-error contract would require a new proposal and approval.

The rebuilt native app launched and responded. Fresh observations showed welcome and explicitly labeled Practice code/explorer screens. Current computer-use instructions were read. Activation/click attempts returned exactly: user input was detected in this window; call get_window_state before continuing. Fresh observation plus one retry did not permit reliable input. No stale coordinates, security/login dialogs or OS settings were automated.

Exact native stop: attempted Appearance & shortcuts interaction before reliable project selection/pairing. Native folder picker, connected consent/analysis, skill selection, controlled challenge, all four hints, correct/partial/incorrect evaluation, resubmission/failure UI, patch/diff review/application, measured/unknown results and readiness require manual verification. Both theme palettes/dialog/code/diff/results journeys and session-only/remember/clear semantics pass widget fixtures; native light/dark titlebar and remembered preference/relaunch remain NOT TESTABLE under the input guard. No native UI defect was reproduced, so no speculative Flutter source fix was made. Native evidence does not establish the complete connected journey.

## Actual Docker evidence

Real production runner uses only registered fresh Guardian copies, never originals. Transparent SDK wrappers delegate to the real engine. Seven connected count/readiness scenarios pass assertions: all-pass 2/2 -> READY; 1 pass/1 fail -> BLOCKED; 1 pass/1 skip -> BLOCKED; empty measured zeros -> BLOCKED; timeout -> null/BLOCKED; unavailable image -> null/BLOCKED; suppressed/unsupported summary -> null/BLOCKED. Canonical unknown counts stay null; legacy scalar defaults are not measurements.

Six isolation/failure/timeout/unittest/Node/repair scenarios pass. Three additional runner scenarios validate unittest/Node 3 total, 1 pass/1 fail/1 skip, and all-skipped pytest 2 total/2 skips; all BLOCKED. In-container assertions pass for 128 MiB scratch tmpfs, noexec and CPU/memory/PID cgroups. Real inspection confirms user 65532:65532, no network, read-only root and snapshot, dropped capabilities, no-new-privileges, 2 CPUs, 512 MiB memory/swap cap and 64 PIDs. Timeouts remove owned containers. Scratch limits are not a universal host/image-storage disk quota.

The reviewed dummy extension is codeproof/dummy-remediation:20261002. Its Dockerfile is repository-owned and explicitly built; selected-project Dockerfiles/dependency scripts were never automatically executed. Healthy copied dummy and security tests run inside the same production restrictions. Remaining target DeprecationWarnings are reported without suppressing CodeProof warning classes.

## Full feature matrix

PASS applies only to exercised scope. PARTIAL means real subsystem or deterministic evidence exists while specified live/native checks remain unexecuted. Exactly one status is assigned to each feature; unexecuted prerequisites are not classified as failures.

FEATURE | STATUS | EVIDENCE | REAL OR MOCK | BLOCKER? | OWNER
---|---|---|---|---|---
MVP-01 Desktop startup | PASS | Fresh Windows release build; responding native welcome/practice explorer | Real native | No | Friend 1
MVP-02 Project selection | PARTIAL | Actual authenticated API opens dummy, local inspection; Dart connection tests; native picker/pairing pending | Real API/Dart; native unexecuted | Yes: native sign-off | Friend 1 + Friend 3
MVP-03 Guardian | PASS | Signing/context/path/payload interception and unchanged bytes; linked-copy escape regression fixed | Real Guardian; intercepted provider transport | No within stated lexical scope | Project Lead + Friend 3
MVP-04 Analysis | PARTIAL | Real local inspection; safe AI attempt 503 example-model config; structured fixtures | Real local; AI transport mocks; live NOT TESTABLE | Yes: live model | Project Lead
MVP-05 Skill map | PARTIAL | Typed provider fixture and widget rendering; live/native skill inference pending | Transport fixtures/practice | Yes: live/native | Project Lead + Friend 1
MVP-06 Controlled challenges | PARTIAL | Exact-manifest three incidents; actual Docker baseline/inject/repair tests; native/live pending | Real managed incidents/Docker; AI mocks | Yes: native/live | Project Lead + Friend 3 + Friend 1
MVP-07 Investigation | PARTIAL | Real session/context services; native practice code observed; connected native pending | Real services; fixture coaching | Yes: native/live | Project Lead + Friend 1
MVP-08 Four hints | PARTIAL | Four-tier serialization and context regressions; no live hints | Provider fixtures/static practice | Yes: live model | Project Lead
MVP-09 Explanation-before-patch | PASS | Only CORRECT and >=0.7 allowed; partial/incorrect/malformed blocked; resubmission faults revoke old permission | Real gate; deterministic AI outputs | No for gate | Project Lead + Friend 3
MVP-10 Evaluation | PARTIAL | Typed classifications/score/feedback and rejection tests; live quality unmeasured | Provider fixtures/keyword practice | Yes: live quality | Project Lead + Friend 1
MVP-11 Patch generation | PARTIAL | Structured proposal/context tests; no live proposal generation | Provider mocks; real downstream patch lab | Yes: live model | Project Lead
MVP-12 Patch review | PARTIAL | Diff/gate/theme widgets and rendering; native connected review pending | Widget fixtures; native unexecuted | Yes: native sign-off | Friend 1
MVP-13 Patch application | PASS | Real registered-copy repair, hostile path rejection and original protection | Real Patch Lab/Docker | No in tested scope | Friend 3
MVP-14 Docker | PASS | Actual isolation/limits/failure/timeout/cleanup; trusted extension validated | Real containers | No for tested images | Friend 3
MVP-15 Test runner | PASS | Actual pass/fail/skip/empty/unknown cases; copied dummy 32/32 after reproduced setup fixes | Real containers/count parsers | No for supported tested runners | Friend 3 + dummy owner
MVP-16 Results UI | PARTIAL | Actual API counts/null semantics plus labeled simulation widgets; native connected results pending | Real API; widget fixtures | Yes: native sign-off | Friend 1 + Friend 3
MVP-17 Readiness | PASS | Actual connected all-pass READY; failures/skips/empty/null BLOCKED; integrity checks | Real services/Docker | No for decision logic | Friend 3
MVP-18 Original protection | PASS | Accessible checkout hashes/HEAD/index and all 6398 original dummy files unchanged; registered-copy/container tests | Real hashes/Docker; inaccessible cache scope stated | No within recorded scope | Project Lead + Friend 3

## Preservation and evidence limits

ORIGINAL CHECKOUT: untouched within the recorded accessible scope. Original HEAD 2874de18cfa1ed9fabbf04fa4f3b9af694e895a4 and index bytes match the baseline. All 19,656 accessible files in C:\Codeproof-main\Codeproof-main match, including the protected desktop generated folders/files. Six preserved CodeProof folders plus the separate dummy total 56,186 accessible files: zero modified, added or removed; recorded links, HEADs and indexes match. PRESERVATION.json gives per-folder counts. Thirteen older original-checkout cache directories were access-denied; their inaccessible contents were not verified. No permissions, original files or original branches were changed to bypass this limitation. All 6,398 original dummy files match, with no unreadable-directory exception. Shared Git metadata is the authorized exception.

Current worktree: C:\Codeproof-mvp-release-completion, codex/mvp-release-completion. The earlier integration audit remains at C:\Codeproof-mvp-audit-worktree, test/mvp-integration; its files/HEAD/index are preserved. No fix was made inside an original checkout or selected original dummy. Actual filtered/reference copies stay local and uncommitted.

## API inventory

The intended launched service exposed 35 OpenAPI method/path entries. Connected /v1 routes use authenticated sessions; the /demo surface is practice evidence. Health is a service check, not an AI-quality or end-to-end check.

METHOD | PATH
---|---
GET | `/project`
GET | `/analysis`
GET | `/skills`
GET | `/challenges`
GET | `/challenges/{challenge_id}`
POST | `/challenges/{challenge_id}/hint`
POST | `/challenges/{challenge_id}/explanation`
POST | `/patch/validate`
POST | `/sandbox/run`
GET | `/release-readiness`
POST | `/release-readiness`
POST | `/v1/sessions`
DELETE | `/v1/sessions/{session_id}`
POST | `/v1/sessions/{session_id}/analysis`
POST | `/v1/sessions/{session_id}/challenge`
POST | `/v1/sessions/{session_id}/hint`
POST | `/v1/sessions/{session_id}/explanation`
POST | `/v1/sessions/{session_id}/patch`
POST | `/v1/sessions/{session_id}/validation`
GET | `/v1/sessions/{session_id}/report`
GET | `/demo/overview`
GET | `/demo/skill-map`
GET | `/demo/files`
GET | `/demo/file`
POST | `/demo/challenge/start`
GET | `/demo/challenge`
POST | `/demo/hint`
POST | `/demo/explanation`
GET | `/demo/patch`
POST | `/demo/patch/apply`
POST | `/demo/validation`
GET | `/demo/release-readiness`
GET | `/demo/state`
POST | `/demo/reset`
GET | `/health`

## Mock inventory and architecture

- Static practice/demo project, skills, challenges, hints, keyword explanations, patch and simulated validation/readiness are explicitly practice evidence. They cannot establish connected provider quality or actual Docker success.
- Deterministic AI/provider-output fixtures and intercepted HTTP transports establish serialization, parsing, gates and error behavior. They do not establish live analysis/evaluation/patch quality.
- Flutter widget/native-channel fixtures establish UI logic and both theme palettes; they do not establish complete native connected interaction, picker or titlebar behavior.
- Real Guardian, authenticated HTTP, managed patch operations, Docker execution, measured counts and hash comparisons are identified separately in the matrix/runtime evidence. Synthetic test signing keys are test-only, with no production fallback.

No new cross-component architecture/API/data-model changes were introduced in these completion fixes. The previously approved shared classifications/counts/incidents contracts remain in place. The linked-source capture concern was reproduced and corrected through the existing hardened Guardian adapter. Docker continues executing registered temporary copies only. Unsupported lexical secret representations and filtered-copy semantic changes remain documented limitations, not a claim of perfect detection. The review found no remaining reproduced bypass in the exercised paths; it is not an exhaustive proof over all possible input or execution environments.

## Remaining release blockers and next dependencies

Release blockers: usable private model configuration and real provider quality verification; a complete native connected journey with reliable exclusive interaction. The exact live stop is Analyze with AI -> configuration 503 before provider transport. The exact native stop is input-guard rejection at Appearance & shortcuts, before reliable project selection/pairing. These are unexecuted checks, not evidence of application crashes. A successful Docker gate or mocked provider journey alone is insufficient for full release sign-off.

Non-blocking issues: 66 copied-target dependency/UTC deprecation warnings; four constrained Flutter-package update notices; generic safe HTTP 500 provider-failure feedback; platform-dependent native titlebar support. Private production dummy signing-key deployment/rotation is unverified. Secret detection remains lexical and supported-representation scoped. Scratch limits do not cap all host Docker image storage.

What works: real desktop launch/build, authenticated local service/Guardian inspection, protected context serialization, explanation/approval revocation gates, controlled managed-copy incidents, safe patch application, real restricted Docker runners, measured counts and fail-closed readiness, filtered healthy dummy 32/32, and recorded original protection. What remains: live model quality and complete connected native sign-off, plus production dummy-key deployment evidence.

Next three tasks:

1. Privately configure a usable CODEPROOF_MODEL and verify real analysis, four hints, three explanation outcomes and generated patch against a safe fixture. Do not put credentials in reports or Git.
2. Complete the native connected journey without competing input, including picker/pairing, consent, patch review, results/readiness, light/dark titlebars and session-only/remembered preference relaunch.
3. Validate private dummy signing-key deployment/rotation in an isolated target deployment and address its dependency/UTC warnings. Any shared secret-forwarding/API redesign requires a separate impact proposal and approval.

## Deliverables and processes

New changed source: workspace/secret_filter.py. New regression modules: tests/test_credential_context.py, tests/test_dummy_preparation.py, backend/tests/test_provider_failures.py. New remediation files: remediation/dummy-app/prepare_copy.py, README.md, overlay/pytest.ini, overlay/tests/conftest.py.in, overlay/tests/test_signing_configuration.py.in, sandbox/Dockerfile, sandbox/requirements.txt. New curated reports/check evidence: reports/release-completion. Updated Windows frontend: deliverables/codeproof-windows-release-20261002-completion.zip, with checksum/size in WINDOWS-PACKAGE.json.

The Windows package has 12 built runtime files plus run instructions. It contains no backend environment, Docker installer, selected original project, API keys or pairing token. The repository supplies the matching backend. Raw hash inventories, temporary copies, private environment files, build caches and generated Flutter metadata are excluded from commits. Published historical reports/packages are dated evidence; current results are in this report.

The owned audit backend PID 16316 was stopped. The rebuilt native frontend PID 20276 was still running at publication preparation and is left open. Docker Desktop remains running; owned probe containers were removed. User-owned processes were not stopped. This publication does not certify a full live/native production release.
