"""Tiny stdlib-only training program; execute through the Docker sandbox."""
import json
import sqlite3


def request_name(payload):
    return payload["username"]


def serialize_date(value):
    return json.dumps({"created_at": value.isoformat()})


def fresh_count():
    with sqlite3.connect(":memory:") as connection:
        connection.execute("CREATE TABLE events (id INTEGER PRIMARY KEY)")
        return connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
