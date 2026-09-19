from fastapi.testclient import TestClient

ALLOWED_ORIGIN = "http://localhost:5173"


def test_cors_allows_configured_origin(client: TestClient) -> None:
    response = client.get("/api/v1/health", headers={"Origin": ALLOWED_ORIGIN})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == ALLOWED_ORIGIN


def test_cors_omits_header_for_other_origin(client: TestClient) -> None:
    response = client.get(
        "/api/v1/health",
        headers={"Origin": "http://evil.example"},
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers
