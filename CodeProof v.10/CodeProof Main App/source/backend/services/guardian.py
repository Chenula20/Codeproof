"""Backend adapter: all original-project content is read by Guardian."""
import stat
from pathlib import Path

from workspace import WorkspaceGuardian
from workspace.scanner import ProjectScanner
from workspace.snapshot import SnapshotBuilder

from .diff import safe_path


def contained_path(root: Path, name: str, *, exists: bool = True) -> Path:
    """Reject links/reparse points at every component before resolving a target."""
    safe_path(name)
    root = root.absolute()
    target = root / name
    # A replaced parent of the workspace can relocate root and target together.
    # Check the whole lexical ancestry, not just components beneath root.
    for part in [*reversed(target.parents), target]:
        if not part.exists() and not part.is_symlink():
            if exists:
                raise ValueError("Snapshot target is missing")
            continue
        info = part.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError("Symlink/reparse-point paths are forbidden")
        if part == target and stat.S_ISREG(info.st_mode) and info.st_nlink > 1:
            raise ValueError("Hard-linked targets are forbidden")
    canonical = target.resolve(strict=exists)
    if not canonical.is_relative_to(root.resolve(strict=True)):
        raise ValueError("Target escapes temporary workspace")
    return target


class ContainedScanner(ProjectScanner):
    def _is_ignored(self, path: Path) -> bool:
        if super()._is_ignored(path):
            return True
        try:
            contained_path(self.project_root, path.relative_to(self.project_root).as_posix())
        except (OSError, ValueError):
            return True
        return False


class ControlledBuilder(SnapshotBuilder):
    def _read_file_safely(self, file_meta):
        try:
            contained_path(self.scanner.project_root, file_meta.path.replace('\\', '/'))
            return self.guardian.read_file(file_meta.path)
        except (OSError, ValueError):
            return None


def open_guardian(path: str) -> WorkspaceGuardian:
    guardian = WorkspaceGuardian(path)
    if not guardian.validate_project():
        raise ValueError("Select an existing project directory")
    guardian.scanner = ContainedScanner(str(guardian.project_root))
    builder = ControlledBuilder(guardian.scanner, guardian.secret_filter)
    builder.guardian = guardian
    guardian.snapshot_builder = builder
    return guardian


def hashes(guardian: WorkspaceGuardian) -> dict[str, str]:
    return {f.path.replace('\\', '/'): f.hash for f in guardian.list_files(force_refresh=True)}


def capture(guardian: WorkspaceGuardian):
    before = hashes(guardian)
    snapshot = guardian.create_snapshot()
    if before != hashes(guardian):
        raise ValueError("Project changed while creating snapshot; try again")
    normalized = {}
    for name, content in snapshot.files.items():
        name = safe_path(name.replace('\\', '/'))
        if name.casefold() in {p.casefold() for p in normalized}:
            raise ValueError("Ambiguous snapshot paths")
        normalized[name] = content
    snapshot.files = normalized
    snapshot.project_root = 'guardian-snapshot'
    return snapshot, before
