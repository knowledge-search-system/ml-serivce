def test_ask_returns_answer_with_sources(client, fake_ask_service):
    response = client.post("/api/v1/ask", json={"question": "what?"})
    assert response.status_code == 200
    assert response.json() == {
        "answer": "42",
        "sources": [
            {"file_name": "a.pdf", "page": 2},
            {"file_name": "b.txt", "page": None},
        ],
    }
    assert fake_ask_service.questions == ["what?"]


def test_ask_validates_body_shape(client):
    response = client.post("/api/v1/ask", json={})
    assert response.status_code == 422
