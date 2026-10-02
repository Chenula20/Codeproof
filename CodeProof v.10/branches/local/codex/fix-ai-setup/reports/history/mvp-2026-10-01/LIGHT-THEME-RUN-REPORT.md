Historical initial audit (2026-10-01), before later fixes. Read [the latest release audit](../../p06-p15/FULL-MVP-RELEASE-AUDIT.md) for current results. Prior missing/deprecated/unavailable findings below are historical evidence, not a claim that the fixes are absent.

# CodeProof: one-time light-theme run report

Date: 2026-10-01 (Asia/Colombo)

## Task and outcome

Requested: launch CodeProof in light theme only for this time.
Outcome: a separate light-theme preview was built successfully and launched. The existing application source and its default dark theme were preserved. This does not implement a permanent theme selector.

## Why a separate preview was necessary

The integrated desktop application hardcodes AppTheme.darkTheme. Its current settings offer reduced transparency and motion, but no light/dark theme switch. Merely changing Windows theme or supplying a launch flag would not change the hardcoded application colors.

The preview uses a separate copy of the desktop project under audit-evidence. Existing original and integrated desktop sources were not edited.

## Preview-only changes

- lib/app/theme.dart: light Material brightness and ColorScheme; light backgrounds/surfaces, dark primary and secondary text, suitable accent/status/border colors and light input fill.
- lib/ui/glass.dart: light ambient/background and brand gradients; white foreground for gradient primary buttons.
- The existing darkTheme getter name was retained inside the preview, but its returned theme is light; this was a temporary preview adaptation.
- Flutter generated dependency/build files in the preview directory.

No backend, AI, Guardian, API, data-model or project-processing behavior was changed. No persistent user theme preference was written.

## Build and launch evidence

Commands ran from the preview project:
- C:\flutter\bin\flutter.bat pub get — exit 0.
- C:\flutter\bin\flutter.bat build windows — exit 0; reported 66.0 seconds.
- Start-Process against the preview build with WindowStyle Normal — launched PID 7020.

Dependency resolution reported four newer package versions incompatible with current constraints. This was a notice; the build succeeded.

Existing desktop source preservation check:
git diff --quiet -- desktop/lib — exit 0 in C:\Codeproof-mvp-audit-worktree.

## Verification scope and limitations

Verified: dependency setup, Windows build, launch returning a process, and unchanged integrated desktop source.
Not executed for this preview: flutter analyze, flutter test, automated screenshot/visual verification, native workspace journey, AI/Docker validation.
The launch is not evidence that all screens have been visually checked. Any remaining contrast issues require visual verification.
This run did not start an audit backend and did not change the earlier MVP audit verdict.

## Required task report

TASK: One-time light-theme launch.
IMPLEMENTED: Separate light-theme preview build and launch.
FILES CREATED/CHANGED: Preview copy, preview-only theme.dart/glass.dart, dependency/build artifacts, launch.json, audit-evidence/light-preview-path.txt and this report.
ARCHITECTURE IMPACT: None.
API IMPACT: None.
DATA MODEL IMPACT: None.
SECURITY IMPACT: Presentation-only adaptation; original application source preserved.
TESTS: Dependency/build/launch checks; no new automated or end-to-end test suite.
KNOWN ISSUES: No permanent theme selector; full visual coverage unverified.
NEXT DEPENDENCY: None required for this temporary run. Permanent light-mode support would be a separate task.

No commit, push, merge into main, protected-folder cleanup or user-process interruption was performed.

## Exact preview paths and current process state

Preview directory: C:\Codeproof-mvp-audit-worktree\audit-evidence\light-preview-20261001-202042
Executable: C:\Codeproof-mvp-audit-worktree\audit-evidence\light-preview-20261001-202042\build\windows\x64\runner\Release\codeproof_desktop.exe

No matching preview process currently running.
