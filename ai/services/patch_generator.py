from typing import Any, Dict, List
from ..models import Patch
from ..providers import BaseAIProvider


class PatchGenerator:
    """Generates code patches for fixes or improvements."""

    def __init__(self, provider: BaseAIProvider):
        self.provider = provider

    async def generate_patch(
        self,
        issue_description: str,
        project_snapshot: Dict[str, Any],
        target_files: List[str]
    ) -> Patch:
        """Generate a patch to address an issue."""
        prompt = self._build_patch_prompt(issue_description, project_snapshot, target_files)
        return await self.provider.generate_structured(
            prompt=prompt,
            response_model=Patch,
            system_prompt="You are an expert software engineer generating code patches."
        )

    async def generate_patch_from_analysis(
        self,
        analysis: Dict[str, Any],
        project_snapshot: Dict[str, Any]
    ) -> List[Patch]:
        """Generate patches based on analysis results."""
        patches = []
        for issue in analysis.get("issues", []):
            if issue.get("auto_fixable", False):
                patch = await self.generate_patch(
                    issue_description=issue["description"],
                    project_snapshot=project_snapshot,
                    target_files=issue.get("affected_files", [])
                )
                patches.append(patch)
        return patches

    def _build_patch_prompt(
        self,
        issue_description: str,
        project_snapshot: Dict[str, Any],
        target_files: List[str]
    ) -> str:
        file_contents = []
        for f in project_snapshot.get("files", []):
            if f["path"] in target_files:
                file_contents.append(f"--- {f['path']} ---\n{f.get('content', '')}")

        return f"""
Generate a patch to fix this issue:

Issue: {issue_description}

Target files:
{chr(10).join(target_files)}

File contents:
{chr(10).join(file_contents)}

Generate a unified diff patch. Assess risk level (low/medium/high).
Note any validation warnings.
"""