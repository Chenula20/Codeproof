"""Patch Lab — validates and applies patches to temporary project copies."""

import os
import re
import shutil
import tempfile
from pathlib import Path

from backend.models import PatchValidateResponse


def get_demo_project_path() -> str:
    """Get the path to the demo project."""
    return str(Path(__file__).parent.parent.parent / "demo-project")


def create_temporary_copy(source_path: str) -> str:
    """Create a temporary copy of the project. Original is never modified."""
    temp_dir = tempfile.mkdtemp(prefix="codeproof_patch_")
    dest = os.path.join(temp_dir, "project")
    shutil.copytree(source_path, dest, ignore=shutil.ignore_patterns(
        "__pycache__", "*.pyc", ".git", "node_modules", ".venv", "venv"
    ))
    return dest


def cleanup_temporary_copy(temp_path: str) -> None:
    """Remove a temporary project copy."""
    if temp_path and os.path.exists(temp_path):
        shutil.rmtree(os.path.dirname(temp_path), ignore_errors=True)


def validate_patch(patch: str) -> PatchValidateResponse:
    """Validate a unified diff patch without applying it."""
    if not patch or not patch.strip():
        return PatchValidateResponse(
            valid=False,
            files_changed=0,
            message="Empty patch provided.",
        )

    # Check for basic unified diff format
    has_diff_header = bool(re.search(r'^--- ', patch, re.MULTILINE))
    has_new_file = bool(re.search(r'^\+\+\+ ', patch, re.MULTILINE))
    has_changes = bool(re.search(r'^[+-]', patch, re.MULTILINE))

    if not (has_diff_header and has_new_file and has_changes):
        return PatchValidateResponse(
            valid=False,
            files_changed=0,
            message="Patch is not in valid unified diff format.",
        )

    # Count changed files
    files_changed = len(re.findall(r'^\+\+\+ ', patch, re.MULTILINE))

    # Check for dangerous patterns
    dangerous_patterns = [
        (r'^\s*rm\s+-rf\s+/', "Dangerous command detected"),
        (r'^\s*sudo\s+', "Sudo command detected"),
        (r'>\s*/etc/', "System file modification detected"),
    ]

    for pattern, reason in dangerous_patterns:
        if re.search(pattern, patch, re.MULTILINE):
            return PatchValidateResponse(
                valid=False,
                files_changed=files_changed,
                message=f"Patch rejected: {reason}.",
            )

    return PatchValidateResponse(
        valid=True,
        files_changed=files_changed,
        message="Patch can be applied safely to temporary workspace.",
    )


def apply_patch(project_path: str, patch: str) -> tuple[bool, str]:
    """Apply a unified diff patch to a project directory.

    Returns (success, message).
    """
    validation = validate_patch(patch)
    if not validation.valid:
        return False, validation.message

    try:
        # Parse the unified diff and apply changes
        files_patched = _apply_unified_diff(project_path, patch)
        return True, f"Patch applied successfully. {files_patched} file(s) modified."
    except Exception as e:
        return False, f"Patch could not be applied: {str(e)}"


def _apply_unified_diff(project_path: str, patch: str) -> int:
    """Parse and apply a unified diff. Returns number of files modified."""
    lines = patch.split('\n')
    files_modified = 0
    i = 0

    while i < len(lines):
        line = lines[i]

        # Look for +++ lines (new file path)
        if line.startswith('+++ '):
            file_path = line[4:].strip()
            # Remove a/ or b/ prefixes
            if file_path.startswith('a/') or file_path.startswith('b/'):
                file_path = file_path[2:]
            # Handle /dev/null (file deletion)
            if file_path == '/dev/null':
                i += 1
                continue

            full_path = os.path.join(project_path, file_path)

            # Collect the diff hunks for this file
            i += 1
            file_lines = []
            while i < len(lines) and not lines[i].startswith('--- '):
                if lines[i].startswith('@@'):
                    # Parse hunk header
                    hunk_match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', lines[i])
                    if hunk_match:
                        file_lines.append(('hunk_header', lines[i], hunk_match))
                elif lines[i].startswith('+'):
                    file_lines.append(('add', lines[i][1:], None))
                elif lines[i].startswith('-'):
                    file_lines.append(('remove', lines[i][1:], None))
                elif lines[i].startswith(' '):
                    file_lines.append(('context', lines[i][1:], None))
                i += 1

            # Apply the changes to the file
            if full_path != '/dev/null' and os.path.exists(full_path):
                _apply_file_changes(full_path, file_lines)
                files_modified += 1
        else:
            i += 1

    return files_modified


def _apply_file_changes(file_path: str, file_lines: list) -> None:
    """Apply parsed diff lines to a single file."""
    with open(file_path, 'r') as f:
        original_lines = f.readlines()

    result_lines = []
    orig_idx = 0

    for entry in file_lines:
        if entry[0] == 'hunk_header':
            hunk_match = entry[2]
            orig_start = int(hunk_match.group(1)) - 1  # 0-indexed
            # Copy unchanged lines before this hunk
            while orig_idx < orig_start and orig_idx < len(original_lines):
                result_lines.append(original_lines[orig_idx])
                orig_idx += 1
        elif entry[0] == 'context':
            if orig_idx < len(original_lines):
                result_lines.append(original_lines[orig_idx])
                orig_idx += 1
        elif entry[0] == 'add':
            result_lines.append(entry[1] + '\n')
        elif entry[0] == 'remove':
            orig_idx += 1  # Skip this line in original

    # Copy remaining lines
    while orig_idx < len(original_lines):
        result_lines.append(original_lines[orig_idx])
        orig_idx += 1

    with open(file_path, 'w') as f:
        f.writelines(result_lines)
