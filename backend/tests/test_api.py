import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import get_db

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["ok", "error"]

def test_unauthorized_access():
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401

def test_login_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "wrong@example.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
