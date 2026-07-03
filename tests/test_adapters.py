from types import SimpleNamespace

from app.adapters.embeddings import EmbeddingClient
from app.adapters.llm import LlmClient


class FakeOpenAi:
    def __init__(self):
        self.embedding_calls = []
        self.chat_calls = []
        self.embeddings = SimpleNamespace(create=self._create_embeddings)
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create_completion))

    async def _create_embeddings(self, model, input):
        self.embedding_calls.append((model, list(input)))
        return SimpleNamespace(
            data=[SimpleNamespace(embedding=[float(i)]) for i, _ in enumerate(input)]
        )

    async def _create_completion(self, model, messages):
        self.chat_calls.append((model, messages))
        message = SimpleNamespace(content="llm answer")
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


async def test_embed_batch_respects_batch_size():
    openai = FakeOpenAi()
    client = EmbeddingClient(openai, model="emb-model", batch_size=2)
    embeddings = await client.embed_batch(["a", "b", "c"])
    assert len(embeddings) == 3
    assert [len(texts) for _, texts in openai.embedding_calls] == [2, 1]
    assert all(model == "emb-model" for model, _ in openai.embedding_calls)


async def test_embed_one_returns_single_vector():
    client = EmbeddingClient(FakeOpenAi(), model="emb-model", batch_size=10)
    embedding = await client.embed_one("question")
    assert embedding == [0.0]


async def test_llm_complete_builds_messages():
    openai = FakeOpenAi()
    client = LlmClient(openai, model="llm-model")
    answer = await client.complete("system prompt", "user prompt")
    assert answer == "llm answer"
    model, messages = openai.chat_calls[0]
    assert model == "llm-model"
    assert messages == [
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": "user prompt"},
    ]
