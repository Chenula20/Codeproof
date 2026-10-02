# R04 connected provider failure verification

TASK: Exercise requested default-provider failure handling separately from live quality.
IMPLEMENTED: Sixteen deterministic OpenRouter transport regressions cover authentication, missing model, unavailable provider, timeout/connection, malformed JSON/schema and empty envelope during analysis and explanation resubmission.
FILES: backend/tests/test_provider_failures.py. No application-source change was necessary for these failure paths.
ARCHITECTURE/API/DATA/SECURITY IMPACT: None. Existing generic safe HTTP 500 responses and gate revocation preserved; provider details never reach client responses; originals and session cleanup verified. A more specific typed provider-error contract is future work requiring a proposal/approval.
TESTS: 16/16 focused; full backend 265/265; project 250/250, warning classes treated as errors. Mocked provider transport is explicitly labeled. Real safe analysis returned configuration 503 before transport because CODEPROOF_MODEL still uses the example; live provider behavior remains NOT TESTABLE.
KNOWN ISSUES: Generic error diagnostics have limited usability; live model quality and native connected flow remain unverified.
NEXT DEPENDENCY: Privately configure a usable model, then perform actual safe analysis/hints/evaluation/patch checks; do not submit secret values to chat.
