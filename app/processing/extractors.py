import io
from abc import ABC, abstractmethod
from dataclasses import dataclass

from docx import Document as DocxDocument
from pypdf import PdfReader

from app.errors import ValidationError


@dataclass
class Page:
    number: int | None
    text: str


class TextExtractor(ABC):
    @abstractmethod
    def extract(self, content: bytes) -> list[Page]: ...


class PdfExtractor(TextExtractor):
    def extract(self, content: bytes) -> list[Page]:
        try:
            reader = PdfReader(io.BytesIO(content))
            return [
                Page(number=index, text=page.extract_text() or "")
                for index, page in enumerate(reader.pages, start=1)
            ]
        except Exception as error:
            raise ValidationError("failed to read pdf file") from error


class DocxExtractor(TextExtractor):
    def extract(self, content: bytes) -> list[Page]:
        try:
            document = DocxDocument(io.BytesIO(content))
        except Exception as error:
            raise ValidationError("failed to read docx file") from error
        text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        return [Page(number=None, text=text)]


class PlainTextExtractor(TextExtractor):
    def extract(self, content: bytes) -> list[Page]:
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValidationError("file is not valid utf-8 text") from error
        return [Page(number=None, text=text)]


def build_extractors() -> dict[str, TextExtractor]:
    plain = PlainTextExtractor()
    return {
        ".pdf": PdfExtractor(),
        ".docx": DocxExtractor(),
        ".txt": plain,
        ".md": plain,
    }
