"""Legacy demo metadata; connected projects use the versioned session API."""
from pathlib import Path
from backend.models import ProjectResponse, SkillsResponse
from .guardian import capture, open_guardian
from .patch_lab import get_demo_project_path


def get_project_info(project_path: str | None = None) -> ProjectResponse:
    path = project_path or get_demo_project_path()
    snapshot, _ = capture(open_guardian(path))
    suffixes = {Path(name).suffix for name in snapshot.files}
    languages = [name for suffix, name in [('.py', 'Python'), ('.js', 'JavaScript'),
                  ('.ts', 'TypeScript'), ('.dart', 'Dart')] if suffix in suffixes]
    frameworks = []
    if any('fastapi' in content.lower() for content in snapshot.files.values()):
        frameworks.append('FastAPI')
    return ProjectResponse(name=Path(path).name, languages=languages, frameworks=frameworks)


def get_skills() -> SkillsResponse:
    """Deterministic practice estimates, never used by connected sessions."""
    return SkillsResponse(debugging=62, api=75, database=45,
                          authentication=38, testing=31, error_handling=52)
