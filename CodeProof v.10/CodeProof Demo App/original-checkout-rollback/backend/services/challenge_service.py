"""Challenge service — manages coding challenges for the demo project."""

from backend.models import (
    ChallengeSummary,
    ChallengeDetail,
    HintResponse,
    ExplanationResponse,
)


# ── Challenge Database ───────────────────────────────────────────────

CHALLENGES: dict[str, dict] = {
    "auth-001": {
        "id": "auth-001",
        "title": "Users cannot log in",
        "difficulty": "easy",
        "skill": "authentication",
        "description": "Users report that login always fails with 'Invalid credentials' even when they enter correct username and password.",
        "scenario": "The login endpoint compares plaintext password against a hashed password in the database, causing all authentication attempts to fail.",
        "expected_fix": "Use bcrypt.checkpw() to verify the hashed password instead of direct comparison.",
        "hints": [
            "Look at the authentication logic in the login endpoint.",
            "Check how passwords are stored vs how they are compared.",
            "The database stores hashed passwords, but the comparison uses plaintext.",
        ],
    },
    "API-001": {
        "id": "API-001",
        "title": "Events API returns 500 error",
        "difficulty": "medium",
        "skill": "api",
        "description": "The /api/events endpoint returns a 500 Internal Server Error when fetching the list of events.",
        "scenario": "The events endpoint tries to serialize a datetime object directly without converting it to a string, causing a JSON serialization error.",
        "expected_fix": "Convert datetime objects to ISO format strings before returning them in the JSON response.",
        "hints": [
            "Check the /api/events endpoint handler.",
            "Look at how the response data is constructed.",
            "Datetime objects are not JSON serializable by default.",
        ],
    },
    "DB-001": {
        "id": "DB-001",
        "title": "Database connection fails on startup",
        "difficulty": "hard",
        "skill": "database",
        "description": "The application crashes on startup with a database connection error when the database file doesn't exist.",
        "scenario": "The database initialization code tries to connect to a SQLite file that doesn't exist yet, and doesn't handle the FileNotFoundError.",
        "expected_fix": "Add a try-except block to create the database file and tables if they don't exist.",
        "hints": [
            "Look at the database initialization code.",
            "Check what happens when the SQLite file doesn't exist.",
            "The app should create the database and tables on first run.",
        ],
    },
}


def list_challenges() -> list[ChallengeSummary]:
    """List all available challenges."""
    return [
        ChallengeSummary(
            id=c["id"],
            title=c["title"],
            difficulty=c["difficulty"],
            skill=c["skill"],
        )
        for c in CHALLENGES.values()
    ]


def get_challenge(challenge_id: str) -> ChallengeDetail | None:
    """Get detailed information about a specific challenge."""
    if challenge_id not in CHALLENGES:
        return None

    c = CHALLENGES[challenge_id]
    return ChallengeDetail(
        id=c["id"],
        title=c["title"],
        difficulty=c["difficulty"],
        skill=c["skill"],
        description=c["description"],
        scenario=c["scenario"],
        expected_fix=c["expected_fix"],
        hints=c["hints"],
    )


def get_hint(challenge_id: str, level: int = 1) -> HintResponse | None:
    """Get a progressive hint for a challenge."""
    if challenge_id not in CHALLENGES:
        return None

    hints = CHALLENGES[challenge_id]["hints"]
    hint_index = min(level - 1, len(hints) - 1)

    return HintResponse(
        challenge_id=challenge_id,
        hint=hints[hint_index],
        level=level,
        next_level_available=level < 4,
    )


def evaluate_explanation(challenge_id: str, explanation: str) -> ExplanationResponse:
    """Evaluate a user's explanation of the challenge."""
    if challenge_id not in CHALLENGES:
        return ExplanationResponse(
            challenge_id=challenge_id,
            classification="UNKNOWN",
            feedback="Challenge not found.",
            score=0.0,
            passed=False,
        )

    expected = CHALLENGES[challenge_id]["expected_fix"].lower()
    user_text = explanation.lower()

    # Simple keyword matching for MVP
    keywords = [word for word in expected.split() if len(word) > 4]
    matches = sum(1 for kw in keywords if kw in user_text)

    if matches >= len(keywords) * 0.6:
        classification = "CORRECT"
        feedback = "Your explanation correctly identifies the issue and the fix needed."
        score = 0.85
    elif matches >= len(keywords) * 0.3:
        classification = "PARTIALLY_CORRECT"
        feedback = "You're on the right track, but your explanation is missing some key details."
        score = 0.5
    else:
        classification = "INCORRECT"
        feedback = "Your explanation doesn't match the expected fix. Review the challenge scenario again."
        score = 0.2

    return ExplanationResponse(
        challenge_id=challenge_id,
        classification=classification,
        feedback=feedback,
        score=score,
        passed=classification in ("CORRECT", "PARTIALLY_CORRECT"),
    )