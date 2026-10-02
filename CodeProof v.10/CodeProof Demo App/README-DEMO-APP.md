# CodeProof Demo App - SEPARATE DEMONSTRATION

This folder preserves the former CodeProof sample/practice application separately from CodeProof Main App.

Windows\codeproof_desktop.exe is the preserved v10 demonstration-capable desktop. Open sample project runs in-memory simulations. Its unchanged compiled build predates separation.

source\demo-project is the Student Event sample, including the pending authentication correction verified by 52 Docker tests. source\training-project is the controlled incident fixture. source\frontend is the browser UI demo. source\remediation\dummy-app is separate copy-preparation tooling.

The preserved demonstration backend retains the old demo and /v1 route composition. Use a different pairing token/port from the main app. The Windows executable still needs its full DLL/data directory. Actual sample/target execution remains Docker-only.

The external original dummy app at C:\New folder\CodeProof-DummyApp was not modified or copied wholesale. No private .env, databases, dependencies or Git metadata are included.

This is the independent DEMO folder. Use the sibling CodeProof Main App folder for the separated main release.
