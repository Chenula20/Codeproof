"""Tests for database failure handling."""

import pytest
import os
from unittest.mock import patch
from backend.database import get_db_connection, init_db, reset_db, DATABASE_PATH


class TestDatabaseFailureHandling:
    """Test database failure scenarios."""

    def test_init_db_creates_tables(self, setup_database):
        """Test that init_db creates all required tables."""
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert cursor.fetchone() is not None

        # Check events table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
        assert cursor.fetchone() is not None

        # Check bookings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bookings'")
        assert cursor.fetchone() is not None

        conn.close()

    def test_reset_db_drops_and_recreates(self, setup_database):
        """Test that reset_db drops and recreates tables."""
        # Create some data
        init_db()
        conn = get_db_connection()
        conn.execute("INSERT INTO users (username, email, password_hash) VALUES ('test', 't@t.com', 'hash')")
        conn.commit()
        conn.close()

        # Reset should remove all data
        reset_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        assert count == 0
        conn.close()

    def test_database_connection_failure(self, setup_database):
        """Test handling of database connection failure."""
        with patch("backend.database.DATABASE_PATH", "/nonexistent/path/db.sqlite"):
            with pytest.raises(Exception):
                conn = get_db_connection()
                conn.close()

    def test_concurrent_connections(self, setup_database):
        """Test multiple database connections work correctly."""
        init_db()
        conn1 = get_db_connection()
        conn2 = get_db_connection()

        conn1.execute("INSERT INTO users (username, email, password_hash) VALUES ('user1', 'u1@t.com', 'hash')")
        conn1.commit()

        cursor = conn2.cursor()
        cursor.execute("SELECT * FROM users WHERE username = 'user1'")
        result = cursor.fetchone()
        assert result is not None

        conn1.close()
        conn2.close()
