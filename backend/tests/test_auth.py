import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_user_register_and_login():
    email = f"researcher_{uuid.uuid4().hex[:6]}@sanskrit.org"
    password = "SecurePassword123!"

    # Register
    res = client.post("/api/v1/auth/register", json={"email": email, "password": password, "role": "researcher"})
    assert res.status_code == 200, res.text
    data = res.json()
    assert "access_token" in data
    assert data["email"] == email

    # Login
    res_login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]

    # Get Me
    headers = {"Authorization": f"Bearer {token}"}
    res_me = client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["email"] == email
