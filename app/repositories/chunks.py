import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Chunk, Document
from app.processing.chunker import TextChunk


@dataclass
class RetrievedChunk:
    text: str
    file_name: str
    page_number: int | None
    score: float


class ChunkRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_all(
        self,
        document_id: uuid.UUID,
        chunks: list[TextChunk],
        embeddings: list[list[float]],
    ) -> None:
        self._session.add_all(
            Chunk(
                document_id=document_id,
                chunk_index=index,
                page_number=chunk.page_number,
                text=chunk.text,
                embedding=embedding,
            )
            for index, (chunk, embedding) in enumerate(zip(chunks, embeddings, strict=True))
        )
        await self._session.flush()

    async def search_similar(
        self, embedding: list[float], top_k: int, min_score: float
    ) -> list[RetrievedChunk]:
        distance = Chunk.embedding.cosine_distance(embedding)
        query = (
            select(Chunk.text, Document.file_name, Chunk.page_number, distance.label("distance"))
            .join(Document, Chunk.document_id == Document.id)
            .order_by(distance)
            .limit(top_k)
        )
        rows = (await self._session.execute(query)).all()
        retrieved = [
            RetrievedChunk(
                text=row.text,
                file_name=row.file_name,
                page_number=row.page_number,
                score=1 - row.distance,
            )
            for row in rows
        ]
        return [chunk for chunk in retrieved if chunk.score >= min_score]
