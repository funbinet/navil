from __future__ import annotations

from fastapi.testclient import TestClient

from navil.api.server import app


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_findings_endpoint_requires_token() -> None:
    with TestClient(app) as client:
        response = client.get("/api/findings", headers={"Authorization": "Bearer local-dev-token"})
        assert response.status_code == 200
        body = response.json()
        assert "count" in body
