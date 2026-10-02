# R03 healthy copied-target database startup

TASK: Repair the reproduced fresh-database initialization defect only in a new isolated healthy dummy reference.
IMPLEMENTED: Copy preparation activates the existing Base.metadata.create_all(bind=engine) call. The copied startup test now launches the real target in a separate Python process inside the production Docker container, from a fresh temporary directory/database, then checks users/events/bookings tables. Other tests use isolated databases. The original target retains its training fault.
FILES CREATED/CHANGED: remediation/dummy-app/prepare_copy.py; overlay/tests/conftest.py.in; tests/test_dummy_preparation.py. Generated healthy copy: tmp/dummy-remediation-healthy (untracked).
ARCHITECTURE/API/DATA MODEL IMPACT: No CodeProof change; no target endpoint/schema changes or migrations. Existing target schema initialized at startup in writable ephemeral container storage.
SECURITY IMPACT: Environment-only signing validation preserved. All copied target execution, including child startup checks, takes place inside CodeProof's non-root/network-disabled managed-copy Docker runner. Original input never runs on the host and remains unchanged.
TESTS: Before: complete copied suite 31 passed/1 failed. After: 32 passed/0 failed/errors/skips; separate signing checks 8/8; static copy-tool regressions 4/4; full CodeProof project suite 250/250 after final changes. Target suite retains 66 DeprecationWarnings (legacy datetime/passlib dependencies); CodeProof's own suites are warning-free with FutureWarning/DeprecationWarning treated as errors.
KNOWN ISSUES: The copy is Guardian-filtered and uses synthetic test credentials; no production dummy credential/deployment sign-off. Live AI/native connected journey remain unverified.
NEXT DEPENDENCY: Use this healthy copy as a test/reference, or the preserved original as the intentionally broken target. Neither constitutes live model-quality evidence.
