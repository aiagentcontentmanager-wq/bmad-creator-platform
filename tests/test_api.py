"""Tests for the BMAD API endpoints."""

import pytest
import uuid
from fastapi.testclient import TestClient
import os

# Ensure test database
os.environ["DATABASE_PATH"] = ":memory:"
os.environ["SECRET_KEY"] = "test-secret-key"

from src.api.main import app

client = TestClient(app)


def _unique_name(prefix="user"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestRoot:
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "BMAD" in data["message"]

    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestAuth:
    def test_register_user(self):
        uname = _unique_name("reg")
        response = client.post("/auth/register", json={
            "username": uname,
            "email": f"{uname}@test.com",
            "password": "securepassword123"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == uname

    def test_register_duplicate_username(self):
        uname = _unique_name("dup")
        client.post("/auth/register", json={
            "username": uname,
            "email": f"{uname}1@test.com",
            "password": "securepassword123"
        })
        response = client.post("/auth/register", json={
            "username": uname,
            "email": f"{uname}2@test.com",
            "password": "securepassword123"
        })
        assert response.status_code == 400

    def test_login(self):
        uname = _unique_name("login")
        client.post("/auth/register", json={
            "username": uname,
            "email": f"{uname}@test.com",
            "password": "securepassword123"
        })
        response = client.post("/auth/token", data={
            "username": uname,
            "password": "securepassword123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        uname = _unique_name("wrongpw")
        client.post("/auth/register", json={
            "username": uname,
            "email": f"{uname}@test.com",
            "password": "securepassword123"
        })
        response = client.post("/auth/token", data={
            "username": uname,
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_get_me(self):
        uname = _unique_name("me")
        client.post("/auth/register", json={
            "username": uname,
            "email": f"{uname}@test.com",
            "password": "securepassword123"
        })
        login = client.post("/auth/token", data={
            "username": uname,
            "password": "securepassword123"
        })
        token = login.json()["access_token"]
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["username"] == uname


class TestCreators:
    def _get_token(self):
        uname = _unique_name("mgr")
        client.post("/auth/register", json={
            "username": uname,
            "email": f"{uname}@test.com",
            "password": "securepassword123",
            "role": "manager"
        })
        login = client.post("/auth/token", data={
            "username": uname,
            "password": "securepassword123"
        })
        return login.json()["access_token"]

    def test_create_creator(self):
        token = self._get_token()
        response = client.post("/creators/", json={
            "name": "Test Creator",
            "platform": "instagram",
            "persona": {"style": "casual", "language": "en"},
            "consent": True
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Creator"
        assert data["consent"] is True

    def test_list_creators(self):
        token = self._get_token()
        # Create one first
        client.post("/creators/", json={
            "name": "Creator A",
            "consent": True
        }, headers={"Authorization": f"Bearer {token}"})
        response = client.get("/creators/", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        # CreatorListResponse has "creators" key
        assert "creators" in data
        assert len(data["creators"]) > 0


class TestFinance:
    def _setup(self):
        uname = _unique_name("fin")
        client.post("/auth/register", json={
            "username": uname,
            "email": f"{uname}@test.com",
            "password": "securepassword123",
            "role": "manager"
        })
        login = client.post("/auth/token", data={
            "username": uname,
            "password": "securepassword123"
        })
        token = login.json()["access_token"]

        creator_resp = client.post("/creators/", json={
            "name": f"Finance Creator {uname}",
            "consent": True
        }, headers={"Authorization": f"Bearer {token}"})
        assert creator_resp.status_code == 201, f"Creator creation failed: {creator_resp.json()}"
        creator_id = creator_resp.json()["id"]
        return token, creator_id

    def test_record_revenue(self):
        token, creator_id = self._setup()
        response = client.post("/finance/revenue", json={
            "creator_id": creator_id,
            "source": "tips",
            "amount": 150.00
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201
        data = response.json()
        assert data["amount"] == 150.0

    def test_get_balance(self):
        token, creator_id = self._setup()
        client.post("/finance/revenue", json={
            "creator_id": creator_id,
            "source": "subscriptions",
            "amount": 500.00
        }, headers={"Authorization": f"Bearer {token}"})

        response = client.get(f"/finance/balance/{creator_id}",
                              headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["total_revenue"] == 500.0
        assert data["available_balance"] == 500.0

    def test_payout_request(self):
        token, creator_id = self._setup()
        client.post("/finance/revenue", json={
            "creator_id": creator_id,
            "source": "tips",
            "amount": 1000.00
        }, headers={"Authorization": f"Bearer {token}"})

        response = client.post("/finance/payout", json={
            "creator_id": creator_id,
            "amount": 500.00
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201
        data = response.json()
        assert data["commission"] == 200.0  # 40% default
        assert data["net_amount"] == 300.0
        assert data["status"] == "pending"
