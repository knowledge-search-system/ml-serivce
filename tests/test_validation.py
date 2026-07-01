from pathlib import Path

import pytest

from app.errors import FileTooLargeError, UnsupportedFormatError, ValidationError
from app.processing.validation import FileValidator

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def validator():
    return FileValidator(max_size_bytes=1024 * 1024)


@pytest.mark.parametrize("file_name", ["sample.pdf", "sample.docx", "sample.txt", "sample.md"])
def test_accepts_supported_files(validator, file_name):
    content = (FIXTURES / file_name).read_bytes()
    assert validator.validate(file_name, content) == Path(file_name).suffix


def test_rejects_unknown_extension(validator):
    with pytest.raises(UnsupportedFormatError):
        validator.validate("app.exe", b"MZ...")


def test_rejects_empty_file(validator):
    with pytest.raises(ValidationError):
        validator.validate("empty.pdf", b"")


def test_rejects_too_large_file():
    validator = FileValidator(max_size_bytes=10)
    with pytest.raises(FileTooLargeError):
        validator.validate("sample.txt", b"x" * 11)


def test_rejects_pdf_with_wrong_magic_bytes(validator):
    content = (FIXTURES / "corrupted.pdf").read_bytes()
    with pytest.raises(ValidationError):
        validator.validate("corrupted.pdf", content)


def test_rejects_docx_with_wrong_magic_bytes(validator):
    with pytest.raises(ValidationError):
        validator.validate("fake.docx", b"not a zip archive")
