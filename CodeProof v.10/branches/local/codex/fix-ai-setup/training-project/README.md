# CodeProof controlled training project

This repository-owned fixture has three healthy stdlib Python tests. It contains
no credentials or production authentication. Open this directory as a connected
project, enable AI analysis, and select a controlled incident. CodeProof injects
exactly one known failure into a registered temporary copy; this directory stays
unchanged. The incidents teach request-field tracing, JSON date serialization,
and SQLite schema initialization.

Use the CodeProof Docker validation runner (Python unittest or pytest). Do not
execute target-project code on the host. The baseline passes three tests; each
incident breaks one test. A correct explanation and reviewed repair must restore
the failing test before release readiness is possible.

Supported incidents require the complete Guardian-visible fixture manifest to
match the approved baseline. Modified or unrelated projects support ordinary
investigation instead. Close and reopen the session to discard the incident
and restore a new healthy temporary copy. No original-file reset is performed.
