from fastapi.testclient import TestClient


def test_unknown_route_standard_404(client: TestClient) -> None:
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert set(body["error"].keys()) == {"code", "message", "details"}
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"]
    assert "x-request-id" in {k.lower() for k in response.headers}


def test_invalid_body_standard_422(client: TestClient) -> None:
    response = client.post("/api/v1/_test/echo", json={})
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["message"]
    assert isinstance(error["details"], list)
    assert error["details"]


def test_unhandled_exception_standard_500(client: TestClient) -> None:
    response = client.get("/api/v1/_test/boom")
    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "Internal server error",
            "details": None,
        }
    }
    assert "forced failure" not in response.text
    assert "Traceback" not in response.text
