"""Test configuration and fixtures."""

import os
import sys
import pytest

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.database import init_db, reset_db, get_db_connection


@pytest.fixture(scope="function")
def setup_database():
    """Reset database before each test."""
    reset_db()
    yield


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    from backend.auth import create_user
    return create_user("testuser", "test@example.com", "password123")


@pytest.fixture
def sample_event():
    """Create a sample event for testing."""
    from backend.events import create_event
    return create_event("Test Event", "A test event", "2026-12-01", 100)
