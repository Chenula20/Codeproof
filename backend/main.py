"""CodeProof Backend — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import project, challenges, patch, sandbox, release, sessions

app = FastAPI(
    title="CodeProof Backend",
    description="Backend API for CodeProof — AI-powered code repair platform",
    version="0.1.0",
)

# CORS for Flutter desktop app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(project.router)
app.include_router(challenges.router)
app.include_router(patch.router)
app.include_router(sandbox.router)
app.include_router(release.router)
app.include_router(sessions.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "codeproof-backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )