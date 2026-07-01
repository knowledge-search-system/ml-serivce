from pathlib import Path

import pytest

from app.errors import ValidationError
from app.processing.extractors import (
    DocxExtractor,
    PdfExtractor,
    PlainTextExtractor,
    build_extractors,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_pdf_extractor_returns_numbered_pages():
    pages = PdfExtractor().extract((FIXTURES / "sample.pdf").read_bytes())
    assert len(pages) >= 1
    assert pages[0].number == 1
    assert pages[0].text.strip()


def test_pdf_extractor_rejects_broken_content():
    with pytest.raises(ValidationError):
        PdfExtractor().extract(b"%PDF-1.3 broken")


def test_docx_extractor_returns_text_without_page_numbers():
    pages = DocxExtractor().extract((FIXTURES / "sample.docx").read_bytes())
    assert len(pages) == 1
    assert pages[0].number is None
    assert pages[0].text.strip()


def test_plain_text_extractor_decodes_utf8():
    pages = PlainTextExtractor().extract((FIXTURES / "sample.txt").read_bytes())
    assert len(pages) == 1
    assert "databases" in pages[0].text


def test_registry_covers_all_supported_extensions():
    extractors = build_extractors()
    assert set(extractors) == {".pdf", ".docx", ".txt", ".md"}
