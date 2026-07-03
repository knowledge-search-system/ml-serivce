import uuid

import pytest
from fastapi.testclient import TestClient

from app.deps import get_ask_service, get_upload_service
from app.errors import AppError
from app.main import create_app
from app.services.ask import AskResult
from app.services.upload import UploadResult


class FakeUploadService:
    def __init__(self):
        self.result = UploadResult(id=uuid.uuid4(), file_name="a.txt", chunks=3)
        self.error: AppError | None = None
        self.calls = []

    async def upload(self, file_name, content):
        self.calls.append((file_name, content))
        if self.error:
            raise self.error
        return self.result


class FakeAskService:
    def __init__(self):
        self.result = AskResult(answer="42", sources=[("a.pdf", 2), ("b.txt", None)])
        self.error: AppError | None = None
        self.questions = []

    async def ask(self, question):
        self.questions.append(question)
        if self.error:
            raise self.error
        return self.result


@pytest.fixture
def fake_upload_service():
    return FakeUploadService()


@pytest.fixture
def fake_ask_service():
    return FakeAskService()


@pytest.fixture
def client(fake_upload_service, fake_ask_service, monkeypatch):
    monkeypatch.setenv("ML_SERVICE_OPENAI_API_KEY", "test-key")
    app = create_app()
    app.dependency_overrides[get_upload_service] = lambda: fake_upload_service
    app.dependency_overrides[get_ask_service] = lambda: fake_ask_service
    with TestClient(app) as test_client:
        yield test_client
