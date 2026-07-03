import uuid
from dataclasses import dataclass

from app.adapters.embeddings import EmbeddingClient
from app.errors import ValidationError
from app.processing.chunker import TokenChunker
from app.processing.extractors import TextExtractor
from app.processing.validation import FileValidator
from app.repositories.chunks import ChunkRepository
from app.repositories.documents import DocumentRepository


@dataclass
class UploadResult:
    id: uuid.UUID
    file_name: str
    chunks: int


class UploadService:
    def __init__(
        self,
        validator: FileValidator,
        extractors: dict[str, TextExtractor],
        chunker: TokenChunker,
        embedder: EmbeddingClient,
        documents: DocumentRepository,
        chunks: ChunkRepository,
    ):
        self._validator = validator
        self._extractors = extractors
        self._chunker = chunker
        self._embedder = embedder
        self._documents = documents
        self._chunks = chunks

    async def upload(self, file_name: str, content: bytes) -> UploadResult:
        extension = self._validator.validate(file_name, content)
        pages = self._extractors[extension].extract(content)
        text_chunks = self._chunker.split(pages)
        if not text_chunks:
            raise ValidationError("file contains no extractable text")
        embeddings = await self._embedder.embed_batch([chunk.text for chunk in text_chunks])
        document = await self._documents.create(file_name)
        await self._chunks.add_all(document.id, text_chunks, embeddings)
        return UploadResult(id=document.id, file_name=file_name, chunks=len(text_chunks))
