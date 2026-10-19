from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from src.common.error import AppError
from src.common.constants import Status

async def app_error_handler(_request: Request, error: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"code": error.code, "message": error.message},
    )


async def integrity_error_handler(_request: Request, _error: IntegrityError) -> JSONResponse:
    # fallback so an unhandled constraint violation is a 409, not a 500
    return JSONResponse(
        status_code=Status.CONFLICT,
        content={"code": "conflict", "message": "Constraint violation"},
    )
