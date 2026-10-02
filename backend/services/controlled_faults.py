"""Controlled faults in selected Guardian snapshots; no bundled demo projects."""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import PurePosixPath

from backend.session_models import IncidentView


@dataclass(frozen=True)
class ControlledFault:
    incident: IncidentView
    runner: str
    marker: str
    statement: str

    def inject(self, source: str) -> str:
        return source + ('\n' if source and not source.endswith('\n') else '') + self.statement + '\n'

    def hints(self, source: str) -> tuple[str, ...]:
        target = self.incident.target_file
        line = len(self.inject(source).splitlines())
        return (
            'Read the Docker failure evidence. A syntax error stops a module from loading before its normal behavior can run.',
            f'Trace the import or load failure to {target}. Compare the temporary copy with the protected original.',
            f'Inspect the appended statement at line {line} in {target}. Its conditional syntax is incomplete.',
            f'Remove the statement marked {self.marker} from {target} in a reviewed temporary-copy patch. Then rerun {self.runner}; the healthy baseline already passed this runner.',
        )


def catalog(files: dict[str, str]) -> list[ControlledFault]:
    """Bounded server-derived choices; never accept arbitrary mutation paths."""
    result = []
    for target, source in sorted(files.items()):
        path = PurePosixPath(target)
        if (not source.strip() or len(target) > 512 or any(
                part.startswith('.') or part.lower() in {'tests', 'test', '__tests__', 'node_modules', 'venv', 'env', 'build', 'dist'}
                for part in path.parts) or path.name.startswith('test_')
                or path.stem.endswith(('_test', '.test', '.spec'))
                or path.name in {'conftest.py', 'setup.py', '__init__.py'}):
            continue
        runners = ('python-pytest', 'python-unittest') if path.suffix == '.py' else (
            ('node-test',) if path.suffix in {'.js', '.mjs', '.cjs'} else ())
        for runner in runners:
            digest = sha256((runner + '\0' + target + '\0' + source).encode()).hexdigest()[:20]
            marker = 'CODEPROOF_FAULT_' + digest
            statement = (f'if True print("{marker}")' if path.suffix == '.py'
                         else f'if (true {{ /* {marker} */')
            incident = IncidentView(id='syntax-' + digest,
                title=f'Syntax failure · {runner} · {target}',
                goal='Find why this module cannot load, explain the syntax error, and restore a passing test suite in the temporary copy.',
                target_file=target)
            result.append(ControlledFault(incident, runner, marker, statement))
            if len(result) == 60:
                return result
    return result
