from dataclasses import dataclass

from app.adapters.embeddings import EmbeddingClient
from app.adapters.llm import LlmClient
from app.errors import ValidationError
from app.repositories.chunks import ChunkRepository, RetrievedChunk

SYSTEM_PROMPT = (
    "You are an assistant answering questions strictly from the provided context. "
    "If the context does not contain the answer, say that the documents do not cover it. "
    "Answer in the language of the question."
)

NO_ANSWER = "Загруженные документы не содержат ответа на этот вопрос."


@dataclass
class AskResult:
    answer: str
    sources: list[tuple[str, int | None]]


class AskService:
    def __init__(
        self,
        embedder: EmbeddingClient,
        llm: LlmClient,
        chunks: ChunkRepository,
        top_k: int,
        min_score: float,
    ):
        self._embedder = embedder
        self._llm = llm
        self._chunks = chunks
        self._top_k = top_k
        self._min_score = min_score

    async def ask(self, question: str) -> AskResult:
        question = question.strip()
        if not question:
            raise ValidationError("question is empty")
        embedding = await self._embedder.embed_one(question)
        retrieved = await self._chunks.search_similar(embedding, self._top_k, self._min_score)
        if not retrieved:
            return AskResult(answer=NO_ANSWER, sources=[])
        answer = await self._llm.complete(SYSTEM_PROMPT, self._build_prompt(question, retrieved))
        return AskResult(answer=answer, sources=self._collect_sources(retrieved))

    def _build_prompt(self, question: str, retrieved: list[RetrievedChunk]) -> str:
        context = "\n\n".join(f"[{chunk.file_name}] {chunk.text}" for chunk in retrieved)
        return f"Context:\n{context}\n\nQuestion: {question}"

    def _collect_sources(self, retrieved: list[RetrievedChunk]) -> list[tuple[str, int | None]]:
        sources = []
        for chunk in retrieved:
            source = (chunk.file_name, chunk.page_number)
            if source not in sources:
                sources.append(source)
        return sources
