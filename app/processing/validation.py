from pathlib import Path

from app.errors import FileTooLargeError, UnsupportedFormatError, ValidationError

MAGIC_BYTES = {
    ".pdf": b"%PDF",
    ".docx": b"PK\x03\x04",
}

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


class FileValidator:
    def __init__(self, max_size_bytes: int):
        self._max_size_bytes = max_size_bytes

    def validate(self, file_name: str, content: bytes) -> str:
        extension = Path(file_name).suffix.lower()
        if extension not in SUPPORTED_EXTENSIONS:
            raise UnsupportedFormatError(f"unsupported file format: {extension or file_name}")
        if not content:
            raise ValidationError("file is empty")
        if len(content) > self._max_size_bytes:
            raise FileTooLargeError(f"file exceeds the {self._max_size_bytes} bytes limit")
        magic = MAGIC_BYTES.get(extension)
        if magic and not content.startswith(magic):
            raise ValidationError(f"file content does not match the {extension} format")
        return extension
