from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.common.error import AppError

async def app_error_handler(_request: Request, error: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"code": error.code, "message": error.message},
    )