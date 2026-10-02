"""Patch only registered disposable copies of Guardian snapshots."""
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from threading import RLock

from backend.models import PatchValidateResponse
from workspace.models import ProjectSnapshot
from .diff import apply_diff, parse_diff, safe_path
from .guardian import capture, contained_path, open_guardian


@dataclass
class Copy:
    owner: tempfile.TemporaryDirectory
    files: dict[str, str]


_copies: dict[str, Copy] = {}
_lock = RLock()


def _key(path: str) -> str:
    # Resolving here would erase evidence of a replaced root link.
    return os.path.normcase(os.path.abspath(path))


def materialize(snapshot: ProjectSnapshot) -> str:
    owner = tempfile.TemporaryDirectory(prefix='codeproof_patch_')
    root = Path(owner.name) / 'project'
    root.mkdir()
    try:
        aliases = set()
        for name, content in snapshot.files.items():
            safe_path(name)
            if name.casefold() in aliases:
                raise ValueError('Ambiguous snapshot paths')
            aliases.add(name.casefold())
            target = contained_path(root, name, exists=False)
            target.parent.mkdir(parents=True, exist_ok=True)
            contained_path(root, name, exists=False).write_text(content, encoding='utf-8', newline='')
        with _lock:
            _copies[_key(str(root))] = Copy(owner, dict(snapshot.files))
        return str(root)
    except Exception:
        owner.cleanup()
        raise


def create_temporary_copy(source_path: str) -> str:
    snapshot, _ = capture(open_guardian(source_path))
    return materialize(snapshot)


def cleanup_temporary_copy(temp_path: str) -> None:
    with _lock:
        copy = _copies.pop(_key(temp_path), None)
        if copy:
            copy.owner.cleanup()


def copy_files(project_path: str) -> dict[str, str]:
    with _lock:
        copy = _copies.get(_key(project_path))
        if copy is None:
            raise ValueError('Only managed temporary workspaces may be used')
        root = Path(project_path)
        for name, expected in copy.files.items():
            target = contained_path(root, name)
            if not target.is_file() or target.read_bytes() != expected.encode('utf-8'):
                raise ValueError('Temporary snapshot integrity check failed')
        return dict(copy.files)


def validate_patch(patch: str, files: dict[str, str] | None = None,
                   allowed: set[str] | None = None) -> PatchValidateResponse:
    try:
        parsed = parse_diff(patch)
        if files is not None:
            apply_diff(files, patch, allowed if allowed is not None else set(files))
        return PatchValidateResponse(valid=True, files_changed=len(parsed),
            message='Patch matches snapshot.' if files is not None else 'Diff syntax valid; snapshot validation still required.')
    except ValueError as exc:
        return PatchValidateResponse(valid=False, message=str(exc))


def apply_patch(project_path: str, patch: str, allowed: set[str] | None = None) -> tuple[bool, str]:
    with _lock:
        staged = []
        try:
            files = copy_files(project_path)
            updated = apply_diff(files, patch, allowed if allowed is not None else set(files))
            root = Path(project_path)
            changed = [name for name in files if files[name] != updated[name]]
            for name in changed:
                contained_path(root, name)
            for name in changed:
                target = contained_path(root, name)
                fd, temporary = tempfile.mkstemp(prefix='.codeproof-', dir=target.parent)
                staged.append((Path(temporary), name))
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(updated[name].encode('utf-8'))
                os.chmod(temporary, 0o644)
            copy_files(project_path)
            for temporary, name in staged:
                target = contained_path(root, name)
                os.replace(temporary, target)
            _copies[_key(project_path)].files = updated
            return True, f'Patch applied to temporary copy: {len(changed)} file(s).'
        except (OSError, ValueError) as exc:
            # A partial I/O failure leaves the manifest unchanged; subsequent
            # operations fail closed. Never roll back by writing to an original.
            return False, f'Patch rejected: {exc}'
        finally:
            for temporary, _ in staged:
                temporary.unlink(missing_ok=True)
