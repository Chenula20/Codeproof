"""CodeProof loopback FastAPI entry point; one process owns ephemeral sessions."""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from backend.routers import project, challenges, patch, sandbox, release, sessions, demo
from backend.services.sessions import configured_provider

logger = logging.getLogger('codeproof.backend')


def create_app(token: str | None = None, provider_factory=None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app):
        try:
            yield
        finally:
            for session in list(app.state.sessions.values()):
                session.close()
            app.state.sessions.clear()

    app = FastAPI(title='CodeProof Backend', version='1.0.0', lifespan=lifespan,
        description='Connected projects use /v1/sessions. Unversioned routes are deterministic demo mode only.')
    app.state.token = token if token is not None else os.getenv('CODEPROOF_TOKEN', '')
    app.state.sessions = {}
    app.state.provider_factory = provider_factory or configured_provider
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', 'localhost', 'testserver'])

    @app.middleware('http')
    async def local_boundary(request: Request, call_next):
        if request.headers.get('origin'):
            return JSONResponse({'detail': 'Browser origins cannot access this desktop service'}, status_code=403)
        length = request.headers.get('content-length', '0')
        if not length.isdigit() or int(length) > 256_000 or request.headers.get('transfer-encoding'):
            return JSONResponse({'detail': 'Request is too large or unsupported'}, status_code=413)
        return await call_next(request)

    @app.exception_handler(ValueError)
    async def invalid(request, exc):
        return JSONResponse({'detail': str(exc)}, status_code=400)

    @app.exception_handler(Exception)
    async def failure(request, exc):
        # Provider exceptions may contain credentials, source, or local paths.
        logger.error('request_failed', extra={'error_type': type(exc).__name__})
        return JSONResponse({'detail': 'Operation failed; check local service configuration.'}, status_code=500)

    for router in (project.router, challenges.router, patch.router, sandbox.router, release.router, sessions.router, demo.router):
        app.include_router(router)

    @app.get('/health')
    def health():
        return {'status': 'healthy', 'service': 'codeproof-backend', 'version': '1.0.0'}

    return app


app = create_app()
