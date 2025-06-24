from fastapi.testclient import TestClient

from llmops_api.main import app

client = TestClient(app)


def test_hello():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "hello"}
