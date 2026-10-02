"""Tests for bookings API module."""

import pytest
from backend.bookings import create_booking, get_user_bookings, cancel_booking
from backend.events import create_event
from backend.auth import create_user


class TestBookingCreation:
    """Test booking creation."""

    def test_create_booking_success(self, setup_database, sample_user, sample_event):
        """Test successful booking creation."""
        result = create_booking(sample_user["id"], sample_event["id"], 2)
        assert result["user_id"] == sample_user["id"]
        assert result["event_id"] == sample_event["id"]
        assert result["seats"] == 2

    def test_create_booking_default_seats(self, setup_database, sample_user, sample_event):
        """Test booking with default seats."""
        result = create_booking(sample_user["id"], sample_event["id"])
        assert result["seats"] == 1

    def test_create_booking_invalid_event(self, setup_database, sample_user):
        """Test booking fails for non-existent event."""
        with pytest.raises(ValueError, match="Event not found"):
            create_booking(sample_user["id"], 9999)

    def test_create_booking_exceeds_capacity(self, setup_database, sample_user):
        """Test booking fails when exceeding event capacity."""
        event = create_event("Small Event", "", "2026-12-01", 2)
        with pytest.raises(ValueError, match="Not enough seats"):
            create_booking(sample_user["id"], event["id"], 5)

    def test_create_booking_invalid_seats(self, setup_database, sample_user, sample_event):
        """Test booking fails with invalid seats."""
        with pytest.raises(ValueError):
            create_booking(sample_user["id"], sample_event["id"], 0)


class TestBookingRetrieval:
    """Test booking retrieval."""

    def test_get_user_bookings_empty(self, setup_database, sample_user):
        """Test getting bookings when user has none."""
        bookings = get_user_bookings(sample_user["id"])
        assert bookings == []

    def test_get_user_bookings_with_data(self, setup_database, sample_user, sample_event):
        """Test getting user bookings returns correct data."""
        create_booking(sample_user["id"], sample_event["id"], 2)
        bookings = get_user_bookings(sample_user["id"])
        assert len(bookings) == 1
        assert bookings[0]["seats"] == 2


class TestBookingCancellation:
    """Test booking cancellation."""

    def test_cancel_booking_success(self, setup_database, sample_user, sample_event):
        """Test successful booking cancellation."""
        booking = create_booking(sample_user["id"], sample_event["id"])
        cancelled = cancel_booking(booking["id"], sample_user["id"])
        assert cancelled is True
        assert get_user_bookings(sample_user["id"]) == []

    def test_cancel_booking_wrong_user(self, setup_database, sample_user, sample_event):
        """Test cancellation fails for wrong user."""
        booking = create_booking(sample_user["id"], sample_event["id"])
        cancelled = cancel_booking(booking["id"], 9999)
        assert cancelled is False

    def test_cancel_booking_not_found(self, setup_database, sample_user):
        """Test cancelling non-existent booking returns False."""
        cancelled = cancel_booking(9999, sample_user["id"])
        assert cancelled is False
