import uuid

from pydantic import BaseModel


class UploadOut(BaseModel):
    id: uuid.UUID
    file_name: str
    chunks: int


class AskIn(BaseModel):
    question: str


class SourceOut(BaseModel):
    file_name: str
    page: int | None


class AskOut(BaseModel):
    answer: str
    sources: list[SourceOut]
