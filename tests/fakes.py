import uuid
from types import SimpleNamespace


class FakeEmbedder:
    def __init__(self):
        self.batch_calls = []

    async def embed_batch(self, texts):
        self.batch_calls.append(list(texts))
        return [[0.1, 0.2, 0.3] for _ in texts]

    async def embed_one(self, text):
        return [0.1, 0.2, 0.3]


class FakeLlm:
    def __init__(self, answer="generated answer"):
        self.answer = answer
        self.calls = []

    async def complete(self, system, user):
        self.calls.append((system, user))
        return self.answer


class FakeDocumentRepository:
    def __init__(self):
        self.created = []

    async def create(self, file_name):
        document = SimpleNamespace(id=uuid.uuid4(), file_name=file_name)
        self.created.append(document)
        return document


class FakeChunkRepository:
    def __init__(self):
        self.saved = []
        self.results = []

    async def add_all(self, document_id, chunks, embeddings):
        self.saved.append((document_id, list(chunks), list(embeddings)))

    async def search_similar(self, embedding, top_k, min_score):
        return self.results
