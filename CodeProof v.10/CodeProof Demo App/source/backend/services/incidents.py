"""Deterministic incidents restricted to the approved, exact training manifest."""
import hashlib
from dataclasses import dataclass

from backend.session_models import IncidentView

# Content hashes are pinned here; editing the bundled fixture cannot silently
# redefine which projects are eligible. Guardian-hidden paths never become input.
BASELINE_MANIFEST = {
    "app.py": "ea69fc7ef4f3bd915ec7c19e844f52064561b7d527a7b584e8c3e7614828203b",
    "tests/test_app.py": "d4a649a8e6c1d7645bf1602eb7cfc99bac6db4ac8a16bf34d87b833ec1110d18",
    "README.md": "bdfb6500a8344d80b3c6d7f91d5d2bf6e76ef9ceb2a8e9f4a4e29b05c2865aac",
}


@dataclass(frozen=True)
class Incident:
    id: str
    title: str
    goal: str
    description: str
    before: str
    after: str
    concepts: tuple[str, ...]
    target_file: str = "app.py"

    def view(self) -> IncidentView:
        return IncidentView(id=self.id, title=self.title, goal=self.goal,
                            target_file=self.target_file)


INCIDENTS = {
    item.id: item for item in (
        Incident(
            id="request-field", title="Request field mismatch",
            goal="Trace the request schema to the field read by the application.",
            description="The controlled request-name test fails for a request containing username. "
                        "Find the mismatch between the request and the lookup.",
            before='return payload["username"]', after='return payload["user_name"]',
            concepts=("The request supplies username but the application reads user_name.",
                      "Use the agreed request field and verify the request-name regression test."),
        ),
        Incident(
            id="date-serialization", title="Date serialization failure",
            goal="Convert boundary values into JSON-compatible primitives.",
            description="The controlled date-serialization test cannot produce JSON from a datetime. "
                        "Explain the boundary conversion and repair it.",
            before='return json.dumps({"created_at": value.isoformat()})',
            after='return json.dumps({"created_at": value})',
            concepts=("A datetime object is not directly JSON serializable.",
                      "Convert the date to ISO text before JSON encoding and verify its representation."),
        ),
        Incident(
            id="database-init", title="Missing database initialization",
            goal="Initialize the database schema before its first query.",
            description="The controlled fresh-database test queries events before that table exists. "
                        "Explain the required initialization order.",
            before='        connection.execute("CREATE TABLE events (id INTEGER PRIMARY KEY)")',
            after="        # Controlled incident: schema initialization is missing.",
            concepts=("A new in-memory SQLite database has no events table.",
                      "Create the schema before querying it and verify the fresh-database test."),
        ),
    )
}


def manifest(files: dict[str, str]) -> dict[str, str]:
    return {name: hashlib.sha256(content.encode("utf-8")).hexdigest()
            for name, content in files.items()}


def supported(files: dict[str, str],
              original_hashes: dict[str, str]) -> list[IncidentView]:
    # Both the entire visible file set and its original bytes must match. This
    # rejects added, missing, redacted or modified source/config/test files.
    if manifest(files) != BASELINE_MANIFEST or original_hashes != BASELINE_MANIFEST:
        return []
    return [item.view() for item in INCIDENTS.values()]


def inject(files: dict[str, str], original_hashes: dict[str, str],
           incident_id: str) -> tuple[Incident, dict[str, str]]:
    incident = INCIDENTS.get(incident_id)
    if incident is None:
        raise ValueError("Unknown controlled incident")
    if not supported(files, original_hashes):
        raise ValueError("Controlled incidents require the unchanged approved training fixture")
    content = files[incident.target_file]
    if content.count(incident.before) != 1:
        raise ValueError("Controlled incident prerequisite does not match")
    updated = dict(files)
    updated[incident.target_file] = content.replace(incident.before, incident.after, 1)
    return incident, updated
