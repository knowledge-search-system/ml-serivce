import pytest
import tiktoken

from app.processing.chunker import TokenChunker
from app.processing.extractors import Page


@pytest.fixture(scope="module")
def encoding():
    return tiktoken.get_encoding("cl100k_base")


def test_short_page_stays_single_chunk(encoding):
    chunker = TokenChunker(encoding, size=100, overlap=20)
    chunks = chunker.split([Page(number=1, text="short text")])
    assert len(chunks) == 1
    assert chunks[0].text == "short text"
    assert chunks[0].page_number == 1


def test_long_page_splits_with_overlap(encoding):
    words = " ".join(f"word{i}" for i in range(100))
    chunker = TokenChunker(encoding, size=50, overlap=10)
    chunks = chunker.split([Page(number=1, text=words)])
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(encoding.encode(chunk.text)) <= 50
    first_tail = encoding.encode(chunks[0].text)[-10:]
    second_head = encoding.encode(chunks[1].text)[:10]
    assert first_tail == second_head


def test_chunks_do_not_cross_pages(encoding):
    chunker = TokenChunker(encoding, size=50, overlap=10)
    chunks = chunker.split([Page(number=1, text="page one"), Page(number=2, text="page two")])
    assert [chunk.page_number for chunk in chunks] == [1, 2]


def test_blank_pages_are_skipped(encoding):
    chunker = TokenChunker(encoding, size=50, overlap=10)
    chunks = chunker.split([Page(number=1, text="   \n  "), Page(number=2, text="real")])
    assert len(chunks) == 1
    assert chunks[0].page_number == 2
