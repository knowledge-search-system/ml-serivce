from dataclasses import dataclass

import tiktoken

from app.processing.extractors import Page


@dataclass
class TextChunk:
    text: str
    page_number: int | None


class TokenChunker:
    def __init__(self, encoding: tiktoken.Encoding, size: int, overlap: int):
        self._encoding = encoding
        self._size = size
        self._stride = size - overlap

    def split(self, pages: list[Page]) -> list[TextChunk]:
        chunks = []
        for page in pages:
            text = page.text.strip()
            if text:
                chunks.extend(self._split_page(text, page.number))
        return chunks

    def _split_page(self, text: str, page_number: int | None) -> list[TextChunk]:
        tokens = self._encoding.encode(text)
        chunks = []
        for start in range(0, len(tokens), self._stride):
            window = tokens[start : start + self._size]
            chunks.append(TextChunk(text=self._encoding.decode(window), page_number=page_number))
            if start + self._size >= len(tokens):
                break
        return chunks
