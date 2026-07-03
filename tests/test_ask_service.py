import pytest

from app.errors import ValidationError
from app.repositories.chunks import RetrievedChunk
from app.services.ask import AskService
from tests.fakes import FakeChunkRepository, FakeEmbedder, FakeLlm


@pytest.fixture
def llm():
    return FakeLlm()


@pytest.fixture
def chunk_repository():
    return FakeChunkRepository()


@pytest.fixture
def service(llm, chunk_repository):
    return AskService(
        embedder=FakeEmbedder(),
        llm=llm,
        chunks=chunk_repository,
        top_k=5,
        min_score=0.35,
    )


def _retrieved(text="context text", file_name="a.pdf", page_number=2, score=0.8):
    return RetrievedChunk(text=text, file_name=file_name, page_number=page_number, score=score)


async def test_ask_answers_from_retrieved_context(service, llm, chunk_repository):
    chunk_repository.results = [_retrieved()]
    result = await service.ask("what is it about?")
    assert result.answer == "generated answer"
    assert result.sources == [("a.pdf", 2)]
    system, user = llm.calls[0]
    assert "context text" in user
    assert "what is it about?" in user


async def test_ask_without_relevant_chunks_skips_llm(service, llm):
    result = await service.ask("unknown topic?")
    assert result.sources == []
    assert result.answer
    assert llm.calls == []


async def test_ask_deduplicates_sources(service, chunk_repository):
    chunk_repository.results = [
        _retrieved(text="one"),
        _retrieved(text="two"),
        _retrieved(text="three", file_name="b.txt", page_number=None),
    ]
    result = await service.ask("question?")
    assert result.sources == [("a.pdf", 2), ("b.txt", None)]


async def test_ask_rejects_blank_question(service):
    with pytest.raises(ValidationError):
        await service.ask("   ")
