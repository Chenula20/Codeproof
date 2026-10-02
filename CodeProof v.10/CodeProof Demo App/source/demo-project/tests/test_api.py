"""Tests for API endpoints using FastAPI TestClient."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.auth import verify_token


client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, setup_database):
        """Test health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestAuthEndpoints:
    """Test authentication API endpoints."""

    def test_register_endpoint(self, setup_database):
        """Test user registration endpoint."""
        response = client.post("/api/auth/register", json={
            "username": "apitest",
            "email": "api@test.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["username"] == "apitest"

    def test_register_duplicate_endpoint(self, setup_database):
        """Test registration endpoint with duplicate user."""
        client.post("/api/auth/register", json={
            "username": "dup",
            "email": "dup@test.com",
            "password": "password123"
        })
        response = client.post("/api/auth/register", json={
            "username": "dup",
            "email": "dup2@test.com",
            "password": "password123"
        })
        assert response.status_code == 400

    def test_login_endpoint_success(self, setup_database):
        """Registration followed by valid login returns a usable bearer JWT."""
        registration = client.post("/api/auth/register", json={
            "username": "logintest",
            "email": "login@test.com",
            "password": "password123"
        })
        assert registration.status_code == 200
        response = client.post("/api/auth/login", json={
            "username": "logintest",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["token_type"] == "bearer"
        assert data["user"] == registration.json()["user"]
        assert "password_hash" not in data["user"]
        payload = verify_token(data["access_token"])
        assert payload is not None
        assert payload["sub"] == "logintest"
        assert payload["user_id"] == data["user"]["id"]

    def test_login_endpoint_rejects_stored_hash(self, setup_database, sample_user_hash):
        """Possession of a stored hash does not authenticate the account."""
        response = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": sample_user_hash
        })
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid credentials"}

    def test_login_endpoint_wrong_password(self, setup_database, sample_user):
        """An existing account still rejects an incorrect plaintext password."""
        response = client.post("/api/auth/login", json={
            "username": sample_user["username"],
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid credentials"}

    def test_login_endpoint_failure(self, setup_database):
        """Test login endpoint with invalid credentials."""
        response = client.post("/api/auth/login", json={
            "username": "nonexistent",
            "password": "wrong"
        })
        assert response.status_code == 401


class TestEventEndpoints:
    """Test event API endpoints."""

    def test_create_event_endpoint(self, setup_database):
        """Test event creation endpoint."""
        response = client.post("/api/events", json={
            "title": "API Test Event",
            "description": "Test",
            "date": "2026-12-01",
            "capacity": 50
        })
        assert response.status_code == 200
        assert response.json()["event"]["title"] == "API Test Event"

    def test_list_events_endpoint(self, setup_database):
        """Test events list endpoint."""
        response = client.get("/api/events")
        assert response.status_code == 200
        assert "events" in response.json()

    def test_get_event_endpoint(self, setup_database):
        """Test single event retrieval endpoint."""
        create_resp = client.post("/api/events", json={
            "title": "Get Test",
            "description": "",
            "date": "2026-12-01"
        })
        event_id = create_resp.json()["event"]["id"]
        response = client.get(f"/api/events/{event_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Get Test"

    def test_get_event_not_found(self, setup_database):
        """Test getting non-existent event returns 404."""
        response = client.get("/api/events/9999")
        assert response.status_code == 404


class TestBookingEndpoints:
    """Test booking API endpoints."""

    def test_create_booking_endpoint(self, setup_database):
        """Test booking creation endpoint."""
        # Create event first
        event_resp = client.post("/api/events", json={
            "title": "Booking Test",
            "description": "",
            "date": "2026-12-01",
            "capacity": 10
        })
        event_id = event_resp.json()["event"]["id"]

        response = client.post("/api/bookings", json={
            "event_id": event_id,
            "seats": 2
        })
        assert response.status_code == 200
        assert response.json()["booking"]["seats"] == 2

    def test_list_bookings_endpoint(self, setup_database):
        """Test user bookings list endpoint."""
        response = client.get("/api/bookings/1")
        assert response.status_code == 200
        assert "bookings" in response.json()
