"""Tests for events API module."""

import pytest
from backend.events import create_event, get_events, get_event, delete_event


class TestEventCreation:
    """Test event creation."""

    def test_create_event_success(self, setup_database):
        """Test successful event creation."""
        result = create_event("Test Event", "Description", "2026-12-01", 100)
        assert result["title"] == "Test Event"
        assert result["description"] == "Description"
        assert result["date"] == "2026-12-01"
        assert result["capacity"] == 100
        assert "id" in result

    def test_create_event_default_capacity(self, setup_database):
        """Test event creation with default capacity."""
        result = create_event("Test Event", "", "2026-12-01")
        assert result["capacity"] == 50

    def test_create_event_empty_title(self, setup_database):
        """Test event creation fails with empty title."""
        with pytest.raises(ValueError):
            create_event("", "Description", "2026-12-01")

    def test_create_event_invalid_capacity(self, setup_database):
        """Test event creation fails with invalid capacity."""
        with pytest.raises(ValueError):
            create_event("Test", "Desc", "2026-12-01", 0)


class TestEventRetrieval:
    """Test event retrieval."""

    def test_get_events_empty(self, setup_database):
        """Test getting events when none exist."""
        events = get_events()
        assert events == []

    def test_get_events_with_data(self, setup_database):
        """Test getting events returns all events."""
        create_event("Event 1", "Desc 1", "2026-12-01")
        create_event("Event 2", "Desc 2", "2026-12-02")
        events = get_events()
        assert len(events) == 2

    def test_get_event_by_id(self, setup_database, sample_event):
        """Test getting a specific event by ID."""
        event = get_event(sample_event["id"])
        assert event is not None
        assert event["title"] == "Test Event"

    def test_get_event_not_found(self, setup_database):
        """Test getting non-existent event returns None."""
        event = get_event(9999)
        assert event is None


class TestEventDeletion:
    """Test event deletion."""

    def test_delete_event_success(self, setup_database, sample_event):
        """Test successful event deletion."""
        deleted = delete_event(sample_event["id"])
        assert deleted is True
        assert get_event(sample_event["id"]) is None

    def test_delete_event_not_found(self, setup_database):
        """Test deleting non-existent event returns False."""
        deleted = delete_event(9999)
        assert deleted is False
