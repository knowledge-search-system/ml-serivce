from app.errors import FileTooLargeError, UnsupportedFormatError


def test_upload_returns_document_summary(client, fake_upload_service):
    response = client.post("/api/v1/documents", files={"file": ("a.txt", b"hello", "text/plain")})
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(fake_upload_service.result.id)
    assert body["file_name"] == "a.txt"
    assert body["chunks"] == 3
    assert fake_upload_service.calls == [("a.txt", b"hello")]


def test_upload_maps_unsupported_format_to_415(client, fake_upload_service):
    fake_upload_service.error = UnsupportedFormatError("unsupported file format: .exe")
    response = client.post(
        "/api/v1/documents", files={"file": ("a.exe", b"MZ", "application/octet-stream")}
    )
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "UNSUPPORTED_FORMAT"


def test_upload_maps_too_large_to_413(client, fake_upload_service):
    fake_upload_service.error = FileTooLargeError("too large")
    response = client.post("/api/v1/documents", files={"file": ("a.txt", b"x", "text/plain")})
    assert response.status_code == 413
