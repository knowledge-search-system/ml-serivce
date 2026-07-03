from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.chunks import ChunkRepository
from app.repositories.documents import DocumentRepository
from app.services.ask import AskService
from app.services.upload import UploadService


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    session_factory = request.app.state.session_factory
    async with session_factory() as session, session.begin():
        yield session


Session = Annotated[AsyncSession, Depends(get_session)]


def get_upload_service(request: Request, session: Session) -> UploadService:
    state = request.app.state
    return UploadService(
        validator=state.validator,
        extractors=state.extractors,
        chunker=state.chunker,
        embedder=state.embedder,
        documents=DocumentRepository(session),
        chunks=ChunkRepository(session),
    )


def get_ask_service(request: Request, session: Session) -> AskService:
    state = request.app.state
    return AskService(
        embedder=state.embedder,
        llm=state.llm,
        chunks=ChunkRepository(session),
        top_k=state.settings.top_k,
        min_score=state.settings.min_score,
    )
