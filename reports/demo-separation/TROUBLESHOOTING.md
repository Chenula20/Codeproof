# Troubleshooting after separation

## Which app should I open?
MAIN: C:\CodeProof brances\CodeProof v.10\CodeProof Main App\Windows\codeproof_desktop.exe
DEMO: C:\CodeProof brances\CodeProof v.10\CodeProof Demo App\Windows\codeproof_desktop.exe
The rebuilt main title is CodeProof Main App and its welcome action is Connect your project. The Demo folder preserves the former sample/practice desktop. Keep DLL/data files with each EXE.

## Why is Open sample project gone?
It was intentionally removed from the main executable. Open the separate Demo App for practice. A missing project path no longer chooses a sample silently.

## Why do /demo or legacy routes return 404?
The main service serves only /health and authenticated /v1 sessions. The independently preserved Demo source/backend serves the old demo/legacy composition. Run it separately using a distinct loopback port/token if both are used. The browser demo must target that demo service rather than the main service.

## Why does the main EXE not connect?
The EXE does not contain FastAPI or Docker. Start the matching backend from the Main App source using python -m backend after installing its trusted dependencies. Use the pairing token from that successfully running service privately, its loopback port and a nonempty filesystem project folder. A target app URL/port is not the CodeProof service address. Check /health; do not stop unrelated listeners.

## Why does AI analysis fail?
Set provider credentials/model privately in CodeProof's own environment, replace the example model, and restart its service. Opening/inspection does not need a provider request. Review sensitivity before enabling AI. Test results use intercepted transport and do not establish live provider quality.

## Why is validation unavailable or readiness blocked?
Docker must run with an explicitly provisioned trusted sandbox image supporting the chosen runner and dependencies. Unknown/empty counts, errors and skips cannot certify readiness. The main app never installs selected project dependencies or executes targets on the host. Demo simulation is not real Docker/test evidence.

## What happened to the original checkout?
C:\Codeproof-main\Codeproof-main remains on feature/backend-integration with its existing schemas. Its sample/browser/demo service files were moved out, its blank-project fallback removed, and its runtime replaced with the rebuilt main EXE. Removed/pre-change files and its old runtime are preserved under Demo App\original-checkout-rollback. Unrelated files and other worktrees remain. Matching newest main Flutter/backend source is in Main App\source.

## Was the authentication bug fixed?
Yes, in Demo App\source\demo-project: login now invokes the existing bcrypt verifier rather than comparing plaintext with its stored hash. Its constrained Docker suite passed 52 tests. This Student Event backend source is separate from the preserved demonstration desktop's in-memory practice simulation. Historical originals in rollback/branch archives retain their old behavior intentionally.

## How do I roll back?
Consult ORIGINAL-CHANGE-LOG.json and restore only the listed original paths from Demo App\original-checkout-rollback if needed. Preserve any edits made after separation; never reset/clean the whole checkout. The prior mixed release is retained as historical material, labelled superseded. Current GitHub source has a normal forward commit, so history is recoverable.

## What does the 24-hour log cover?
All commits/file actions available across local refs in the stated rolling window, local reflog events, pending authentication/original states, and the new separation action log. Git cannot recover every intermediate uncommitted edit or machine-wide filesystem event. Full per-file commit changes are in CHANGES-LAST-24-HOURS.json; separation paths/hashes are recorded separately.
