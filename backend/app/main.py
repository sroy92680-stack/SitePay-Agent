#Owner::ANIKET::ANHOTRA = MR.Panda
"""FastAPI assembly with explicit startup validation and scoped routers."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import (
    auth_routes,
    health_routes,
    organization_routes,
    sync_routes,
    upload_routes,
    project_routes,
    site_routes,
)
from backend.app.config import get_settings
from backend.app.errors import install_error_handlers
from backend.app.logging_setup import configure_logging


@asynccontextmanager
async def application_lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Fail startup if the database URL or signing key is not configured.

    Migrations are performed separately, not from a web request.
    """
    configuration = get_settings()
    configure_logging(configuration.environment)
    yield


def create_application() -> FastAPI:
    """Assemble the site management API without in-memory fake data."""
    application = FastAPI(
        title="SitePay Agent API",
        version="0.1.0-dev",
        lifespan=application_lifespan,
    )
    origins = tuple(
        value.strip()
        for value in os.getenv("SITEPAY_CORS_ORIGINS", "").split(",")
        if value.strip()
    )
    if origins and "*" not in origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=list(origins),
            allow_methods=["GET", "POST"],
            allow_headers=["Authorization", "Content-Type"],
            allow_credentials=False,
        )
    application.include_router(auth_routes.router)
    application.include_router(organization_routes.router)
    application.include_router(project_routes.router)
    application.include_router(site_routes.router)
    application.include_router(health_routes.router)
    application.include_router(upload_routes.router)
    application.include_router(sync_routes.router)
    install_error_handlers(application)
    return application


app = create_application()
