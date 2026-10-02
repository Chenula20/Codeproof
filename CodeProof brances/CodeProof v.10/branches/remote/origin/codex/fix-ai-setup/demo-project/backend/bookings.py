"""Bookings API module — handles event booking operations."""

from typing import Optional

from backend.database import get_db_connection, init_db


def create_booking(user_id: int, event_id: int, seats: int = 1) -> dict:
    """Create a new booking."""
    if seats < 1:
        raise ValueError("Seats must be at least 1")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if event exists
    cursor.execute("SELECT id, capacity FROM events WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    if event is None:
        conn.close()
        raise ValueError("Event not found")

    # Check existing bookings for this event
    cursor.execute(
        "SELECT SUM(seats) as total_booked FROM bookings WHERE event_id = ?",
        (event_id,),
    )
    row = cursor.fetchone()
    total_booked = row["total_booked"] or 0

    if total_booked + seats > event["capacity"]:
        conn.close()
        raise ValueError("Not enough seats available")

    cursor.execute(
        "INSERT INTO bookings (user_id, event_id, seats) VALUES (?, ?, ?)",
        (user_id, event_id, seats),
    )
    conn.commit()
    booking_id = cursor.lastrowid
    conn.close()

    return {
        "id": booking_id,
        "user_id": user_id,
        "event_id": event_id,
        "seats": seats,
    }


def get_user_bookings(user_id: int) -> list[dict]:
    """Get all bookings for a specific user."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM bookings WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    bookings = []
    for row in rows:
        bookings.append({
            "id": row["id"],
            "user_id": row["user_id"],
            "event_id": row["event_id"],
            "seats": row["seats"],
        })

    return bookings


def cancel_booking(booking_id: int, user_id: int) -> bool:
    """Cancel a booking. Returns True if cancelled, False if not found."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM bookings WHERE id = ? AND user_id = ?",
        (booking_id, user_id),
    )
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()

    return deleted
