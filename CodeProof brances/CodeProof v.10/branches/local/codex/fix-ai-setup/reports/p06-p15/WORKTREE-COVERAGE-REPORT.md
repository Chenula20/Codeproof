# Signing fix and MVP worktree coverage

All application source work from the signing-secret and MVP integration worktrees is included in the consolidated published codex/fix-ai-setup branch. Older worktrees are preserved; no old source was copied over the newer tested implementation and no private signing key is published.

| Worktree | Recorded state | Included in GitHub |
|---|---|---|
| C:\Codeproof-main\Codeproof-main | Original feature/backend-integration checkout at 2874de1; protected files/HEAD/index unchanged | Backend commit is an ancestor of published branch; original not modified |
| C:\Codeproof-mvp-audit | Separate preserved clean repository, test/mvp-integration at 2874de1 | No unique working changes; its backend baseline already included |
| C:\Codeproof-mvp-audit-worktree | test/mvp-integration at 911d45c; earlier merged backend + Flutter; no unique application-source changes | Both feature heads and integration commit in published ancestry; reviewed historical audit documents now in reports/history/mvp-2026-10-01 |
| C:\Codeproof-fix-signing-secret-redaction | Uncommitted P01 changes in SecretFilter, backend provider test and signing test file | Already incorporated into later fixes; complete signing regression file byte-identical and original signing provider assertions retained |
| C:\Codeproof-fix-ai-setup | Consolidated source/configuration, contracts, tests, reports and delivery packages | Published on codex/fix-ai-setup |
| C:\Codeproof-release-audit-p06-p15 | Isolated 62-file tested assembly at integrated base | Approved source published; final reports, reviewed check logs/JUnit and Windows/source ZIPs available |

## Signing-secret fix mapping

- workspace/secret_filter.py: original signing-assignment grammar and helpers retained, with later credential-assignment/context improvements. No downgrade to the older snapshot.
- tests/test_signing_secret_redaction.py: byte-identical to the original signing-fix worktree test file.
- backend/tests/test_sessions.py: original signing literal/context assertions retained in the complete provider HTTP flow, plus later outcome/gate/count/credential cases. Actual provider transport interception ensures the synthetic literals do not reach serialized requests.
- Existing .env/secret-file/path protections and original-byte assertions remain in the passing suites. Unsupported representations are documented in the current release audit; detection is not promised to be perfect.

## Newly added historical audit documents

reports/history/mvp-2026-10-01 contains eight selected initial reports/source references/boolean findings plus context README. Historical outcomes are clearly separated from the later 477 Python/37 Flutter passing checks and actual Docker validation. The earlier one-time light preview is superseded by the implemented optional theme selector; its report is retained as history.

## Remaining local data

Dependencies, .dart_tool, private .env, actual keys/tokens, temporary project/test copies, and raw historical evidence are not missing application code. They remain local. Bulk raw-evidence publication was rejected by automatic approval review; only the reviewed document subset is added here. No original or older audit worktree is cleaned/reset/stashed/committed or overwritten.

TASK: Ensure signing-secret/MVP worktree work is included in GitHub. IMPLEMENTED: Read-only source/ancestry comparison, reviewed missing historical docs and explicit coverage mapping. FILES: This report, verification JSON and reports/history/mvp-2026-10-01. ARCHITECTURE/API/DATA IMPACT: None. SECURITY IMPACT: Actual secret values excluded; earlier safe redaction/tests preserved. TESTS: Source file identity, retained assertion ASTs and Git ancestor checks, with previous full-suite results unchanged; no new source implementation. KNOWN ISSUES: Existing live-AI/native/target setup blockers. NEXT DEPENDENCY: Use the consolidated branch and latest audit; do not mistake historical findings for current status.
