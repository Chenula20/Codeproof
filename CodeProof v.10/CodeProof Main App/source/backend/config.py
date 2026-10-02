"""Local service configuration; never search a selected project's environment files."""
import os
from pathlib import Path

from dotenv import load_dotenv


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_MODEL = "provider/model-id"


def load_local_environment(path: Path | None = None) -> None:
    """Load only CodeProof's root .env; inherited process values always win.

    Disable interpolation: API-key characters and missing variables must not be
    expanded or resolved using other secrets. This is invoked by the launcher,
    not by library imports or Guardian project reads.
    """
    try:
        load_dotenv(
            dotenv_path=path if path is not None else REPOSITORY_ROOT / ".env",
            override=False,
            interpolate=False,
            encoding="utf-8",
        )
    except (OSError, UnicodeError):
        raise SystemExit("Cannot read CodeProof's root .env. Check its permissions and UTF-8 encoding.") from None


def backend_port() -> int:
    """Validate a loopback service port without echoing supplied configuration."""
    try:
        port = int(os.getenv("BACKEND_PORT", "8000"))
    except ValueError:
        raise SystemExit("BACKEND_PORT must be an integer from 1 to 65535.") from None
    if not 1 <= port <= 65535:
        raise SystemExit("BACKEND_PORT must be an integer from 1 to 65535.")
    return port


def provider_settings() -> tuple[str, str]:
    """Return configured credentials/model, or a safe actionable diagnostic."""
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    model = os.getenv("CODEPROOF_MODEL", "").strip()
    missing = [name for name, value in (
        ("OPENROUTER_API_KEY", key), ("CODEPROOF_MODEL", model)
    ) if not value]
    if missing:
        raise ValueError(
            "Missing AI configuration: " + ", ".join(missing) +
            ". Set these process variables or CodeProof's root .env, then restart "
            "with python -m backend. Local inspection remains available."
        )
    if model == EXAMPLE_MODEL:
        raise ValueError(
            "Replace the CODEPROOF_MODEL example provider/model-id with an available "
            "OpenRouter model ID, then restart the backend."
        )
    return key, model
