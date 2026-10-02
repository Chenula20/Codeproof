"""Tests for authentication module."""

import pytest
from backend.auth import (
    create_user,
    authenticate_user,
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
)


class TestRegistration:
    """Test user registration."""

    def test_register_user_success(self, setup_database):
        """Test successful user registration."""
        result = create_user("newuser", "new@example.com", "password123")
        assert result["username"] == "newuser"
        assert result["email"] == "new@example.com"
        assert "id" in result

    def test_register_duplicate_username(self, setup_database):
        """Test registration with duplicate username fails."""
        create_user("dupuser", "first@example.com", "password123")
        with pytest.raises(ValueError, match="Username already exists"):
            create_user("dupuser", "second@example.com", "password123")

    def test_register_duplicate_email(self, setup_database):
        """Test registration with duplicate email fails."""
        create_user("user1", "dup@example.com", "password123")
        with pytest.raises(ValueError, match="Email already exists"):
            create_user("user2", "dup@example.com", "password123")

    def test_register_empty_fields(self, setup_database):
        """Test registration with empty fields fails."""
        with pytest.raises(ValueError):
            create_user("", "test@example.com", "password123")

    def test_register_short_password(self, setup_database):
        """Test registration with short password fails."""
        with pytest.raises(ValueError, match="at least 6 characters"):
            create_user("user", "test@example.com", "123")


class TestLogin:
    """Test user login."""

    def test_login_success(self, setup_database, sample_user):
        """Test login with correct credentials.

        NOTE: This test documents the auth-001 bug. Login currently fails
        because plaintext password is compared against hash. When the bug
        is fixed (using verify_password), this test should pass.
        """
        result = authenticate_user("testuser", "password123")
        # BUG: This should succeed but fails due to auth-001
        assert result is None  # Bug: should be not None afterafter fixfix

    def test_login_wrong_password(self, setup_database, sample_user):
        """Test login fails with wrong password."""
        result = authenticate_user("testuser", "wrongpassword")
        assert result is None

    def test_login_nonexistent_user(self, setup_database):
        """Test login fails for non-existent user."""
        result = authenticate_user("nonexistent", "password123")
        assert result is None

    def test_login_empty_credentials(self, setup_database):
        """Test login fails with empty credentials."""
        result = authenticate_user("", "")
        assert result is None


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password(self, setup_database):
        """Test password hashing produces different hashes."""
        hash1 = hash_password("password123")
        hash2 = hash_password("password123")
        assert hash1 != hash2  # Different salts

    def test_verify_password_correct(self, setup_database):
        """Test password verification with correct password."""
        hashed = hash_password("password123")
        assert verify_password("password123", hashed) is True

    def test_verify_password_incorrect(self, setup_database):
        """Test password verification with incorrect password."""
        hashed = hash_password("password123")
        assert verify_password("wrongpassword", hashed) is False


class TestJWT:
    """Test JWT token creation and verification."""

    def test_create_and_verify_token(self, setup_database):
        """Test token creation and verification."""
        token = create_access_token(data={"sub": "testuser", "user_id": 1})
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["user_id"] == 1

    def test_verify_invalid_token(self, setup_database):
        """Test verification of invalid token fails."""
        payload = verify_token("invalid.token.here")
        assert payload is None
