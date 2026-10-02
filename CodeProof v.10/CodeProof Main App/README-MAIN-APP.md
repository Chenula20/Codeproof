# CodeProof Main App - MAIN APPLICATION

Run Windows\codeproof_desktop.exe from this folder with its DLL/data files. This is the rebuilt main release 1.0.10+11. It has no Open sample project action, implicit demo selection, demo API routes or controlled demo incidents.

source contains the separated main source. CodeProof-Main-Windows.zip and CodeProof-Main-Source.zip are portable packages. Synthetic regression fixtures under source\desktop\test are test-only and are not bundled into the executable.

Start a separately configured CodeProof backend from source before connecting your explicitly selected filesystem project. Configure credentials privately. Actual target tests require Docker and an approved image. The backend and Docker are not embedded in the EXE.

Use the sibling CodeProof Demo App folder for independent demonstration/sample content. Original-checkout rollback files are preserved there. Historical Merged application and branch archives predate separation.

See IMPLEMENTATION-REPORT.md, RELEASE-MANIFEST.json and the change/troubleshooting logs for exact verification and limitations.
