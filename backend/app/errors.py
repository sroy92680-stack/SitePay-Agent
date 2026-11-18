#Owner::ANIKET::ANHOTRA = MR.Panda
"""Safe API validation responses that do not echo sensitive inputs."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def install_error_handlers(application: FastAPI) -> None:
    """Hide raw request contents from validation error responses.

    Logs and clients must not accidentally receive submitted passwords.
    """

    @application.exception_handler(RequestValidationError)
    async def handle_validation_failure(
        request: Request, exception: RequestValidationError
    ) -> JSONResponse:
        """Return a stable client error without reflecting secret inputs."""
        return JSONResponse(status_code=422, content={"detail": "Invalid request data"})
