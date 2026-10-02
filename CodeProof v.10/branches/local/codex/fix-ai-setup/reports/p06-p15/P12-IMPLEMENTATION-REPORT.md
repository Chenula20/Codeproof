# P12 implementation report
TASK: Optional permanent light mode plus session-only choice.
IMPLEMENTED: Immutable context-selected light/dark palettes for all direct widget colors, gradients, inputs, code/diff/status/dialog/footer. Dark is default. Appearance exposes Light theme and opt-in Remember theme; off is session-only. Native app preference uses HKCU Software\CodeProof\Preferences LightTheme, and application titlebar follows app choice on supported Windows builds. No new packages or backend changes.
FILES: desktop/lib/app/{app.dart,theme.dart}, desktop/lib/ui/glass.dart, desktop/lib/features/startup/startup_screen.dart, desktop/lib/features/workspace/{pages.dart,coach.dart,evidence.dart,workspace_shell.dart}, desktop/windows/runner/{flutter_window.cpp,win32_window.cpp,win32_window.h}, desktop/test/theme_test.dart.
ARCHITECTURE/API/DATA IMPACT: Desktop-local native appearance methods only; no backend/AI/target contract.
SECURITY: Preference contains one nonsecret boolean. No global OS theme changes or target writes.
TESTS: p12-analyze-verified.log no issues. Eight combined P11/P12 tests passed; both palettes meet >=4.5 text contrast on panels; session-only/remember/clear options and both simulated complete journeys tested. Rendered light welcome/review/results and dark review inspected; preview PNGs under desktop/build/previews. Native Windows build/titlebar verification remains final audit work.
KNOWN ISSUES: Older Windows may ignore DWM caption attributes; Flutter content still uses selected palette. Live connected workflow requires provider configuration.
NEXT DEPENDENCY: Use Appearance & shortcuts; leave Remember theme off for one session.
