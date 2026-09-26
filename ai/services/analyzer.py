from typing import Any, Dict, List, Optional
from ..models import ProjectAnalysis, EngineeringSkillMap
from ..providers import BaseAIProvider


class ProjectAnalyzer:
    """Analyzes a project to understand its structure, technologies, and issues."""

    def __init__(self, provider: BaseAIProvider):
        self.provider = provider

    async def analyze(self, project_snapshot: Dict[str, Any]) -> ProjectAnalysis:
        """Analyze a project from its snapshot."""
        prompt = self._build_analysis_prompt(project_snapshot)
        return await self.provider.generate_structured(
            prompt=prompt,
            response_model=ProjectAnalysis,
            system_prompt="You are an expert software engineer analyzing a project."
        )

    async def map_skills(self, project_snapshot: Dict[str, Any]) -> EngineeringSkillMap:
        """Map engineering skills required for a project."""
        prompt = self._build_skill_prompt(project_snapshot)
        return await self.provider.generate_structured(
            prompt=prompt,
            response_model=EngineeringSkillMap,
            system_prompt="You are an expert software engineer identifying required skills."
        )

    def _build_analysis_prompt(self, snapshot: Dict[str, Any]) -> str:
        files_summary = "\n".join([
            f"- {f['path']}: {f.get('summary', 'No summary')}"
            for f in snapshot.get("files", [])[:20]
        ])
        return f"""
Analyze this project and provide:
1. A high-level summary
2. Technologies detected
3. Issues identified
4. Relevant engineering skills

Project files:
{files_summary}

Dependencies: {snapshot.get('dependencies', {})}
Configuration: {snapshot.get('config', {})}
"""

    def _build_skill_prompt(self, snapshot: Dict[str, Any]) -> str:
        files_summary = "\n".join([
            f"- {f['path']}"
            for f in snapshot.get("files", [])[:30]
        ])
        return f"""
Identify the engineering skills required to work on this project.

Project files:
{files_summary}

Technologies: {snapshot.get('technologies', [])}
"""