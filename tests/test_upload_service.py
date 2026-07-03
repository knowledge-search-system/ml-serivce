from pathlib import Path

import pytest
import tiktoken

from app.errors import UnsupportedFormatError, ValidationError
from app.processing.chunker import TokenChunker
from app.processing.extractors import build_extractors
from app.processing.validation import FileValidator
from app.services.upload import UploadService
from tests.fakes import FakeChunkRepository, FakeDocumentRepository, FakeEmbedder

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def embedder():
    return FakeEmbedder()


@pytest.fixture
def chunk_repository():
    return FakeChunkRepository()


@pytest.fixture
def service(embedder, chunk_repository):
    encoding = tiktoken.get_encoding("cl100k_base")
    return UploadService(
        validator=FileValidator(max_size_bytes=1024 * 1024),
        extractors=build_extractors(),
        chunker=TokenChunker(encoding, size=50, overlap=10),
        embedder=embedder,
        documents=FakeDocumentRepository(),
        chunks=chunk_repository,
    )


async def test_upload_stores_chunks_with_embeddings(service, embedder, chunk_repository):
    content = (FIXTURES / "sample.txt").read_bytes()
    result = await service.upload("sample.txt", content)
    assert result.chunks == 1
    assert embedder.batch_calls == [[content.decode().strip()]]
    document_id, chunks, embeddings = chunk_repository.saved[0]
    assert document_id == result.id
    assert len(chunks) == len(embeddings) == 1


async def test_upload_rejects_unsupported_format(service):
    with pytest.raises(UnsupportedFormatError):
        await service.upload("app.exe", b"MZ...")


async def test_upload_rejects_corrupted_pdf(service):
    content = (FIXTURES / "corrupted.pdf").read_bytes()
    with pytest.raises(ValidationError):
        await service.upload("corrupted.pdf", content)


async def test_upload_rejects_file_without_text(service):
    with pytest.raises(ValidationError):
        await service.upload("blank.txt", b"   \n   ")
