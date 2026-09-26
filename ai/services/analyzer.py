from typing import List
from ..models import ProjectAnalysis, EngineeringSkillMap
from ..providers import BaseAIProvider
from workspace.models import ProjectSnapshot


class ProjectAnalyzer:
    """Analyzes a project to understand its structure, technologies, and issues."""

    def __init__(self, provider: BaseAIProvider):
        self.provider = provider

    async def analyze(self, project_snapshot: ProjectSnapshot) -> ProjectAnalysis:
        """Analyze a project from its snapshot."""
        prompt = self._build_analysis_prompt(project_snapshot)
        return await self.provider.generate_structured(
            prompt=prompt,
            response_model=ProjectAnalysis,
            system_prompt="You are an expert software engineer analyzing a project."
        )

    async def map_skills(self, project_snapshot: ProjectSnapshot) -> EngineeringSkillMap:
        """Map engineering skills required for a project."""
        prompt = self._build_skill_prompt(project_snapshot)
        return await self.provider.generate_structured(
            prompt=prompt,
            response_model=EngineeringSkillMap,
            system_prompt="You are an expert software engineer identifying required skills."
        )

    def _build_analysis_prompt(self, snapshot: ProjectSnapshot) -> str:
        files_summary = "\n".join([
            f"- {path}: {content[:200]}..."
            for path, content in list(snapshot.files.items())[:20]
        ])
        return f"""
Analyze this project and provide:
1. A high-level summary
2. Technologies detected
3. Issues identified
4. Relevant engineering skills

Project files:
{files_summary}

Dependencies: {snapshot.dependencies}
Configuration: {snapshot.config}
"""

    def _build_skill_prompt(self, snapshot: ProjectSnapshot) -> str:
        files_summary = "\n".join([
            f"- {path}"
            for path in list(snapshot.files.keys())[:30]
        ])
        return f"""
Identify the engineering skills required to work on this project.

Project files:
{files_summary}

Dependencies: {snapshot.dependencies}
Configuration: {snapshot.config}
"""