from enum import StrEnum

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ErrorCode(StrEnum):
    NOT_FOUND = "NOT_FOUND"
    VALIDATION = "VALIDATION"
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INTERNAL = "INTERNAL"


class AppError(Exception):
    code = ErrorCode.INTERNAL


class NotFoundError(AppError):
    code = ErrorCode.NOT_FOUND


class ValidationError(AppError):
    code = ErrorCode.VALIDATION


class UnsupportedFormatError(AppError):
    code = ErrorCode.UNSUPPORTED_FORMAT


class FileTooLargeError(AppError):
    code = ErrorCode.FILE_TOO_LARGE


class InternalError(AppError):
    code = ErrorCode.INTERNAL


HTTP_STATUS_BY_CODE = {
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.VALIDATION: 400,
    ErrorCode.UNSUPPORTED_FORMAT: 415,
    ErrorCode.FILE_TOO_LARGE: 413,
    ErrorCode.INTERNAL: 500,
}


def _error_response(code: ErrorCode, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=HTTP_STATUS_BY_CODE[code],
        content={"error": {"code": code, "message": message}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return _error_response(exc.code, str(exc))

    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        return _error_response(ErrorCode.INTERNAL, "internal error")

    app.add_exception_handler(AppError, handle_app_error)
    app.add_exception_handler(Exception, handle_unexpected)
