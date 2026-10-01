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


def _is_absolute_path(path: str) -> bool:
    """Check if a path is absolute (works for both Windows and Unix-style paths)."""
    if not path:
        return False
    # Unix-style absolute path
    if path.startswith('/'):
        return True
    # Windows-style absolute path (drive letter)
    if len(path) >= 2 and path[1] == ':' and path[0].isalpha():
        return True
    # Windows UNC path
    if path.startswith('\\\\') or path.startswith('//'):
        return True
    return False


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

    # Check for path traversal in patch file paths
    # Extract all +++ file paths and check for ..
    file_paths = re.findall(r'^\+\+\+ (.+)$', patch, re.MULTILINE)
    for fp in file_paths:
        fp = fp.strip()
        if fp.startswith('a/') or fp.startswith('b/'):
            fp = fp[2:]
        if fp != '/dev/null' and ('..' in fp or _is_absolute_path(fp)):
            return PatchValidateResponse(
                valid=False,
                files_changed=files_changed,
                message=f"Patch rejected: Path traversal or absolute path detected in file path: {fp}",
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


def _resolve_safe_path(base_path: str, target_path: str) -> str:
    """
    Resolve target path and ensure it's contained within base_path.
    
    Raises ValueError if target_path escapes base_path or is a symlink/reparse point
    that points outside base_path.
    """
    base = Path(base_path).resolve()
    target = Path(target_path).resolve()
    
    # Check if target is within base
    try:
        target.relative_to(base)
    except ValueError:
        raise ValueError(f"Path traversal detected: {target_path} escapes workspace")
    
    # Check if any parent of target is a symlink/reparse point
    # that could have been used to escape
    for parent in target.parents:
        if parent == base:
            break
        if parent.is_symlink() or _is_reparse_point(parent):
            # The parent is a symlink/reparse point - check if its target is outside base
            try:
                real_parent = parent.resolve()
                real_parent.relative_to(base)
            except ValueError:
                raise ValueError(f"Symlink/reparse point escape detected: {parent}")
    
    return str(target)


def _is_reparse_point(path: Path) -> bool:
    """Check if a path is a Windows reparse point (symlink, junction, mount point)."""
    try:
        # On Windows, check for reparse points
        if os.name == 'nt':
            import ctypes
            
            FILE_ATTRIBUTE_REPARSE_POINT = 0x400
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
            if attrs != -1 and (attrs & FILE_ATTRIBUTE_REPARSE_POINT):
                return True
    except Exception:
        pass
    return False


def _apply_unified_diff(project_path: str, patch: str) -> int:
    """Parse and apply a unified diff. Returns number of files modified."""
    # Get canonical project path for containment checks
    canonical_project_path = Path(project_path).resolve()
    
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

            # Construct full path and validate containment
            full_path = os.path.join(project_path, file_path)
            
            # SECURITY: Resolve and verify the target path is within the project
            try:
                safe_path = _resolve_safe_path(str(canonical_project_path), full_path)
            except ValueError as e:
                raise ValueError(f"Security violation: {e}")

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
            if safe_path != '/dev/null' and os.path.exists(safe_path):
                _apply_file_changes(safe_path, file_lines)
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