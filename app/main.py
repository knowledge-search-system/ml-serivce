from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import tiktoken
from fastapi import FastAPI
from openai import AsyncOpenAI

from app.adapters.embeddings import EmbeddingClient
from app.adapters.llm import LlmClient
from app.config import Settings
from app.db import create_engine, create_session_factory
from app.errors import register_exception_handlers
from app.processing.chunker import TokenChunker
from app.processing.extractors import build_extractors
from app.processing.validation import FileValidator
from app.routers import ask, documents, health


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = Settings()
    engine = create_engine(settings.postgres_dsn)
    openai = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
    encoding = tiktoken.get_encoding("cl100k_base")
    app.state.settings = settings
    app.state.session_factory = create_session_factory(engine)
    app.state.embedder = EmbeddingClient(
        openai,
        model=settings.embedding_model,
        batch_size=settings.embedding_batch_size,
        dimensions=settings.embedding_dimensions,
    )
    app.state.llm = LlmClient(openai, model=settings.llm_model)
    app.state.validator = FileValidator(max_size_bytes=settings.max_file_size_bytes)
    app.state.extractors = build_extractors()
    app.state.chunker = TokenChunker(
        encoding, size=settings.chunk_size_tokens, overlap=settings.chunk_overlap_tokens
    )
    try:
        yield
    finally:
        await openai.close()
        await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="ml-service", lifespan=lifespan)
    register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(documents.router)
    app.include_router(ask.router)
    return app


app = create_app()
