"""Events API module — handles event CRUD operations."""

from typing import Optional

from backend.database import get_db_connection, init_db


def create_event(title: str, description: str, date: str, capacity: int = 50) -> dict:
    """Create a new event."""
    if not title or not date:
        raise ValueError("Title and date are required")

    if capacity < 1:
        raise ValueError("Capacity must be at least 1")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO events (title, description, date, capacity) VALUES (?, ?, ?, ?)",
        (title, description, date, capacity),
    )
    conn.commit()
    event_id = cursor.lastrowid
    conn.close()

    return {
        "id": event_id,
        "title": title,
        "description": description,
        "date": date,
        "capacity": capacity,
    }


def get_events() -> list[dict]:
    """Get all events."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM events ORDER BY date")
    rows = cursor.fetchall()
    conn.close()

    events = []
    for row in rows:
        events.append({
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "date": row["date"],
            "capacity": row["capacity"],
        })

    return events


def get_event(event_id: int) -> Optional[dict]:
    """Get a specific event by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "date": row["date"],
        "capacity": row["capacity"],
    }


def delete_event(event_id: int) -> bool:
    """Delete an event. Returns True if deleted, False if not found."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()

    return deleted
