import pytest
from fastapi.testclient import TestClient
from presentation.api import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "gemini_active" in data


def test_cliches_endpoint():
    response = client.get("/api/v1/cliches")
    assert response.status_code == 200
    data = response.json()
    assert data["banned_count"] > 10
    assert "delve" in data["cliches"]


def test_audit_only_endpoint():
    response = client.post(
        "/api/v1/audit-only",
        json={"text": "We delve into this tapestry to unlock insights."}
    )
    assert response.status_code == 200
    report = response.json()
    assert "metrics" in report
    assert "delve" in report["metrics"]["cliche_matches"]
