# R01 Guardian credential context

TASK: Reproduce and repair nonsensitive Python expressions replaced by credential markers.
IMPLEMENTED: AST parsing without evaluation preserves calls, model columns, member access and public field labels without embedded credential values; trims annotation whitespace. Scalar literals, bare unknown config scalars and embedded literal credentials remain redacted. Signing-specific rules are unchanged.
FILES CREATED/CHANGED: workspace/secret_filter.py; tests/test_credential_context.py.
ARCHITECTURE/API/DATA MODEL IMPACT: None; internal filtering only, no new shared contract.
SECURITY IMPACT: Provider boundary and original read-only behavior preserved. Synthetic source/config signing tests and actual HTTP payload interception pass. Computed secrets, arbitrary aliases, credential values concealed as dictionary/subscript labels, unsupported syntax and general dataflow are not resolved. Conventional credential parameter names are preserved as context; ambiguous representations require manual sensitivity review. This is not perfect detection.
TESTS: Before: 11 failed, 6 passed (exit 1). After: 171 passed, zero failures/errors/skips, warnings promoted to errors (exit 0), including provider interception, signing/path protections, unchanged original bytes and bare config scalar regression.
KNOWN ISSUES: No usable CODEPROOF_MODEL configured; live model quality remains NOT TESTABLE. Filtered literals can still change target test semantics.
NEXT DEPENDENCY: Test target dependencies and test credentials must be supplied as controlled fixtures, not original production secrets.
