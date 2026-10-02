"""Project analysis service — provides project metadata for the UI."""

import os
from pathlib import Path
from typing import Optional

from backend.models import ProjectResponse, SkillsResponse


# Language detection by extension
LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "JavaScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".cpp": "C++",
    ".c": "C",
    ".cs": "C#",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".kt": "Kotlin",
}

# Framework detection by file patterns
FRAMEWORK_PATTERNS = {
    "React": ["package.json"],
    "FastAPI": ["requirements.txt", "pyproject.toml"],
    "Flutter": ["pubspec.yaml"],
    "Django": ["manage.py"],
    "Express": ["package.json"],
    "Spring": ["pom.xml", "build.gradle"],
}


def detect_languages(project_path: str) -> list[str]:
    """Detect programming languages used in the project."""
    languages = set()
    project = Path(project_path)

    for ext in LANGUAGE_MAP:
        if any(project.rglob(f"*{ext}")):
            languages.add(LANGUAGE_MAP[ext])

    return sorted(languages) if languages else ["Python"]


def detect_frameworks(project_path: str) -> list[str]:
    """Detect frameworks used in the project."""
    frameworks = set()
    project = Path(project_path)

    for framework, patterns in FRAMEWORK_PATTERNS.items():
        for pattern in patterns:
            if any(project.rglob(pattern)):
                frameworks.add(framework)
                break

    return sorted(frameworks) if frameworks else ["FastAPI"]


def get_project_info(project_path: Optional[str] = None) -> ProjectResponse:
    """Get project metadata for the UI."""
    if project_path is None:
        project_path = os.getenv(
            "CODEPROOF_PROJECT_PATH",
            str(Path(__file__).parent.parent / "demo-project"),
        )

    project = Path(project_path)
    name = project.name if project.exists() else "Unknown Project"

    return ProjectResponse(
        name=name,
        languages=detect_languages(project_path),
        frameworks=detect_frameworks(project_path),
    )


def get_skills() -> SkillsResponse:
    """Get engineering skill estimates for the current project."""
    return SkillsResponse(
        debugging=62,
        api=75,
        database=45,
        authentication=38,
        testing=31,
        error_handling=52,
    )
