from openai import AsyncOpenAI


class EmbeddingClient:
    def __init__(self, client: AsyncOpenAI, model: str, batch_size: int, dimensions: int):
        self._client = client
        self._model = model
        self._batch_size = batch_size
        self._dimensions = dimensions

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        for start in range(0, len(texts), self._batch_size):
            batch = texts[start : start + self._batch_size]
            response = await self._client.embeddings.create(
                model=self._model, input=batch, dimensions=self._dimensions
            )
            embeddings.extend(item.embedding for item in response.data)
        return embeddings

    async def embed_one(self, text: str) -> list[float]:
        embeddings = await self.embed_batch([text])
        return embeddings[0]
