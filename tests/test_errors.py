import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.errors import (
    AppError,
    FileTooLargeError,
    InternalError,
    NotFoundError,
    UnsupportedFormatError,
    ValidationError,
    register_exception_handlers,
)


def _app_raising(error: AppError) -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    async def boom():
        raise error

    return app


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (NotFoundError("nope"), 404),
        (ValidationError("bad"), 400),
        (UnsupportedFormatError("exe"), 415),
        (FileTooLargeError("huge"), 413),
        (InternalError("oops"), 500),
    ],
)
def test_handler_maps_app_errors_to_http(error, expected_status):
    client = TestClient(_app_raising(error))
    response = client.get("/boom")
    assert response.status_code == expected_status
    assert response.json() == {"error": {"code": error.code, "message": str(error)}}
