# Docker prerequisite setup and runtime attempt

Date: 2026-10-01 (Asia/Colombo)
Worktree used: C:\Codeproof-fix-ai-setup
Outcome: prerequisite installation succeeded; real container validation NOT TESTABLE until Windows restart.

## Discovery and original blocker

The installed CLI was not in the current shell PATH. It was found using refreshed
user PATH at:
C:\Users\binuj\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe

Docker CLI version: 29.8.1.
Docker Desktop UI version observed: 4.93.0.
Started the existing Docker Desktop installation; no new Docker installation was
performed. Its engine initially was absent, then API requests returned 500.
Its actual dashboard reported:
"Virtualization support not detected"
"Docker Desktop failed to start because virtualisation support wasn't detected."
"Engine stopped"

Read-only Windows checks:
VirtualMachinePlatform InstallState=2 (disabled).
Microsoft-Windows-Subsystem-Linux InstallState=2 (disabled).
Microsoft-Hyper-V-All InstallState=2 (disabled).
wsl --status exited 50: Windows Subsystem for Linux is not installed.
HypervisorPresent=true; CPU virtualization flags reported false. These flags alone
do not establish that firmware virtualization is disabled, especially with a
hypervisor present. Firmware/nested virtualization must be reassessed if Docker
still fails after required Windows feature installation and restart.

## Real CodeProof attempt before prerequisites

Used only a harmless synthetic test file, not the external dummy.
The actual sandbox.run_sandbox call reported status=unavailable:
"Docker or the prebuilt sandbox image is unavailable."
Readiness=BLOCKED.
Original fixture SHA256 unchanged.
Managed copies remaining=0.
No target code was executed on the host and no container was started.

Optional real Docker pytest check:
python -m pytest backend/tests/test_sandbox_safety.py::test_real_docker_when_available
-q -rs -p no:cacheprovider
--basetemp=C:\Codeproof-fix-ai-setup\.pytest-tmp-docker-real

Result: 1 skipped, exit 0; reason Docker daemon or prebuilt sandbox image unavailable.
A skipped check is not a real Docker PASS. CLI PATH was set for this command only.
No image build was attempted while the engine was unavailable.

## Approved prerequisite installation

User explicitly approved installing prerequisites without automatic restart.
The sandbox-elevated shell still had no Windows administrator token.
Initial wsl --install --no-distribution attempt exited 1.
Launched a Windows UAC-elevated PowerShell helper; no UAC/authentication UI was
automated.

The helper ran:
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -All -NoRestart
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -All -NoRestart
wsl.exe --install --no-distribution

Both feature commands completed with RestartNeeded=true.
WSL installer exited 0 and reported Windows Subsystem for Linux 3.0.1 installed.
It explicitly reported that changes will not be effective until reboot.
No Linux distribution was requested. No automatic reboot occurred.
Evidence: wsl-prerequisites-install.json and wsl-installer-process.json.

## Current state and next step

WSL package installed; required platform features enabled; Windows restart pending.
Real container isolation/test/timeout/cleanup verification remains NOT TESTABLE.
No trusted sandbox image was built and no successful container execution is claimed.
Docker Desktop was left open; no existing user-owned process was stopped.
The prerequisite helper completed.

Restart Windows manually after saving work. After restart:
1. Start Docker Desktop and verify its Linux engine through CLI and Python SDK.
2. Build only repository-owned sandbox/Dockerfile into codeproof/sandbox:latest.
3. Run actual CodeProof safe-fixture success/failure/timeout/isolation/cleanup
   checks and report real test counts, original hashes and readiness.
4. Reassess firmware/nested virtualization only if the engine still cannot start.

## Sources and evidence

Docker Windows requirements and per-user installation:
https://docs.docker.com/desktop/setup/install/windows-install/
Microsoft WSL installation:
https://learn.microsoft.com/en-us/windows/wsl/install
Win32_OptionalFeature numeric states:
https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-optionalfeature

Local evidence:
docker-runtime-result.json; docker-real-test.log;
wsl-prerequisites-install.json; wsl-installer-process.json;
docker-prerequisite-summary.json.

## Required task report

TASK: Start Docker and perform real CodeProof container validation.
IMPLEMENTED: Started installed Docker Desktop, diagnosed blockers, installed
user-approved WSL 3.0.1 and enabled WSL/Virtual Machine Platform without restart.
FILES CREATED/CHANGED: Setup evidence/report only; no additional app source edits.
ARCHITECTURE IMPACT: None.
API IMPACT: None.
DATA MODEL IMPACT: None.
SECURITY IMPACT: Authorized Windows feature installation; CodeProof original/
copy/Docker boundaries preserved; no host target execution.
TESTS: Actual sandbox availability attempt unavailable; optional real test skipped.
KNOWN ISSUES: Windows restart pending; image build and real container behavior untested.
NEXT DEPENDENCY: User-controlled restart, then resume Docker validation.
