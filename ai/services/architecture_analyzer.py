from typing import Any, Dict, List
from ..models import ProjectAnalysis
from ..providers import BaseAIProvider


class ArchitectureAnalyzer:
    """Analyzes project architecture and detects architectural patterns."""

    def __init__(self, provider: BaseAIProvider):
        self.provider = provider

    async def analyze_architecture(self, project_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the architecture of a project."""
        prompt = self._build_architecture_prompt(project_snapshot)
        response = await self.provider.generate(
            prompt=prompt,
            system_prompt="You are a software architect analyzing system architecture."
        )
        return {"analysis": response}

    async def detect_patterns(self, project_snapshot: Dict[str, Any]) -> List[str]:
        """Detect architectural patterns in the project."""
        prompt = self._build_pattern_prompt(project_snapshot)
        response = await self.provider.generate(
            prompt=prompt,
            system_prompt="You are a software architect identifying architectural patterns."
        )
        return [line.strip("- ") for line in response.split("\n") if line.strip().startswith("-")]

    async def evaluate_changes(self, project_snapshot: Dict[str, Any], proposed_changes: str) -> Dict[str, Any]:
        """Evaluate proposed architectural changes."""
        prompt = self._build_evaluation_prompt(project_snapshot, proposed_changes)
        response = await self.provider.generate(
            prompt=prompt,
            system_prompt="You are a software architect evaluating proposed changes."
        )
        return {"evaluation": response}

    def _build_architecture_prompt(self, snapshot: Dict[str, Any]) -> str:
        structure = "\n".join([
            f"- {f['path']} ({f.get('type', 'file')})"
            for f in snapshot.get("files", [])[:50]
        ])
        return f"""
Analyze the architecture of this project:

File structure:
{structure}

Dependencies: {snapshot.get('dependencies', {})}
Config files: {snapshot.get('config', {})}

Identify:
1. Overall architecture style
2. Module organization
3. Data flow patterns
4. Potential architectural issues
"""

    def _build_pattern_prompt(self, snapshot: Dict[str, Any]) -> str:
        return f"""
Identify architectural patterns in this project:
{self._build_architecture_prompt(snapshot)}

List patterns found (one per line, prefixed with -):
"""

    def _build_evaluation_prompt(self, snapshot: Dict[str, Any], changes: str) -> str:
        return f"""
Evaluate these proposed architectural changes:

Current architecture:
{self._build_architecture_prompt(snapshot)}

Proposed changes:
{changes}

Provide evaluation covering:
1. Impact on existing architecture
2. Risks and benefits
3. Recommendations
"""