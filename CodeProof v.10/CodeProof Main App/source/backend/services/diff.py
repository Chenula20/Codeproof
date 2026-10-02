"""Strict unified diffs for existing, explicitly approved snapshot files."""
import re
from dataclasses import dataclass
from pathlib import PurePosixPath


def safe_path(value: str) -> str:
    if not value or any(c in value for c in '\\:\x00\r\n\t'):
        raise ValueError("Invalid patch path")
    parts = value.split('/')
    reserved = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)),
                *(f'LPT{i}' for i in range(1, 10))}
    if PurePosixPath(value).is_absolute() or any(
        p in ('', '.', '..') or p.endswith(('.', ' ')) or
        p.split('.')[0].upper() in reserved or any(c in p for c in '<>"|?*')
        for p in parts
    ):
        raise ValueError("Patch path must be relative, contained, and unambiguous")
    return value


@dataclass
class Hunk:
    old_start: int
    new_start: int
    lines: list[tuple[str, str]]


def parse_diff(diff: str) -> dict[str, list[Hunk]]:
    if not diff.strip() or len(diff) > 200_000:
        raise ValueError("Empty or oversized patch")
    lines = diff.replace('\r\n', '\n').splitlines(keepends=True)
    result: dict[str, list[Hunk]] = {}
    aliases: set[str] = set()
    i = 0
    while i < len(lines):
        if lines[i].startswith(('diff --git ', 'index ')):
            i += 1
            continue
        if not lines[i].startswith('--- ') or i + 1 >= len(lines):
            raise ValueError("Expected unified diff headers")
        old = lines[i][4:].removesuffix('\n')
        if not lines[i + 1].startswith('+++ '):
            raise ValueError("Missing new-file header")
        new = lines[i + 1][4:].removesuffix('\n')
        old = safe_path(old[2:] if old.startswith('a/') else old)
        new = safe_path(new[2:] if new.startswith('b/') else new)
        if old != new or old.casefold() in aliases:
            raise ValueError("Renames and duplicate targets are not supported")
        aliases.add(old.casefold())
        hunks = []
        i += 2
        while i < len(lines) and lines[i].startswith('@@ '):
            match = re.fullmatch(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@[^\n]*\n?', lines[i])
            if not match:
                raise ValueError("Malformed hunk header")
            start, count, new_start, new_count = match.groups()
            old_count, new_count = int(count or 1), int(new_count or 1)
            offset = int(start) - bool(old_count)
            new_offset = int(new_start) - bool(new_count)
            if min(offset, new_offset) < 0 or not (old_count or new_count):
                raise ValueError("Invalid hunk range")
            consumed = produced = 0
            body = []
            i += 1
            while consumed < old_count or produced < new_count:
                if i >= len(lines) or lines[i][0] not in ' +-':
                    raise ValueError("Hunk line counts do not match")
                kind, content = lines[i][0], lines[i][1:]
                if not content.endswith('\n'):
                    raise ValueError("Unterminated diff line")
                consumed += kind in ' -'
                produced += kind in ' +'
                i += 1
                if i < len(lines) and lines[i].rstrip('\n') == '\\ No newline at end of file':
                    content = content[:-1]
                    i += 1
                if consumed > old_count or produced > new_count:
                    raise ValueError("Hunk line counts do not match")
                body.append((kind, content))
            hunks.append(Hunk(offset, new_offset, body))
        if not hunks or not any(k in '+-' for h in hunks for k, _ in h.lines):
            raise ValueError("Patch has no changes")
        result[old] = hunks
    if not result:
        raise ValueError("Patch has no files")
    return result


def apply_diff(files: dict[str, str], diff: str, allowed: set[str]) -> dict[str, str]:
    result = dict(files)
    for name, hunks in parse_diff(diff).items():
        if name not in allowed or name not in files:
            raise ValueError("Patch target is not an allowed snapshot file")
        original = files[name].replace('\r\n', '\n').splitlines(keepends=True)
        output = []
        cursor = 0
        for hunk in hunks:
            if hunk.old_start < cursor or hunk.old_start > len(original):
                raise ValueError("Overlapping or out-of-range hunk")
            output.extend(original[cursor:hunk.old_start])
            cursor = hunk.old_start
            if len(output) != hunk.new_start:
                raise ValueError("Invalid new-file offset")
            for kind, content in hunk.lines:
                if kind in ' -':
                    if cursor >= len(original) or original[cursor] != content:
                        raise ValueError("Patch context no longer matches snapshot")
                    cursor += 1
                if kind in ' +':
                    output.append(content)
        output.extend(original[cursor:])
        updated = ''.join(output)
        if '\r\n' in files[name] and '\n' not in files[name].replace('\r\n', ''):
            updated = updated.replace('\n', '\r\n')
        if updated == files[name]:
            raise ValueError("Patch makes no changes")
        result[name] = updated
    return result
