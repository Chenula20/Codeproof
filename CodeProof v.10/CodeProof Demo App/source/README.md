# CodeProof

A Windows desktop developer engineering environment that helps developers who use AI to build software but may not fully understand, debug, test, or maintain the software they create.

## Architecture

```
Flutter Desktop
    ↓
Workspace Guardian
    ↓
FastAPI Backend
    ↓
AI Engine
    ↓
Patch Lab
    ↓
Docker Sandbox
    ↓
Test Runner
    ↓
Release Readiness
```

## Core Principle

> The original user project is never directly modified by CodeProof.

## Repository Structure

```
codeproof/
├── AGENTS.md              # Project rules and context
├── README.md
├── .gitignore
├── .env.example
├── docs/
│   ├── ARCHITECTURE_V1.1.md
│   └── adrs/
├── desktop/               # Flutter Desktop (Friend 1)
├── backend/               # FastAPI Backend (Friend 3)
├── ai/                    # AI Engine (Project Lead)
├── workspace/             # Workspace Guardian (Project Lead)
├── sandbox/               # Docker Sandbox (Friend 3)
├── demo-project/          # Student Event Management (Friend 2)
├── tests/
└── scripts/
```

## Getting Started

1. If no root .env exists, copy .env.example to .env. Set OPENROUTER_API_KEY privately and replace the CODEPROOF_MODEL example for connected AI; inspection/practice work without them.
2. Install dependencies for each component
3. Run tests to verify setup. Start the desktop service with backend/.venv/Scripts/python.exe -m backend; this launcher loads only CodeProof's root .env, keeps process variables authoritative, and generates a pairing token. See backend/README.md for port, pairing, provider and Docker prerequisites.

## Development

See `AGENTS.md` for development rules and team roles.