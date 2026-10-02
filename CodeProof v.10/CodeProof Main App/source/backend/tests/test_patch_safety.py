import os
from pathlib import Path

import pytest

from backend.services import patch_lab


def diff(path='file.py', before='old', after='new'):
    return f'--- a/{path}\n+++ b/{path}\n@@ -1 +1 @@\n-{before}\n+{after}\n'


@pytest.fixture
def copy(tmp_path):
    source = tmp_path / 'original'
    source.mkdir()
    (source / 'file.py').write_text('old\n')
    result = Path(patch_lab.create_temporary_copy(str(source)))
    yield source, result
    patch_lab.cleanup_temporary_copy(str(result))


def test_symlink_cannot_write_external_sentinel(copy, tmp_path):
    source, root = copy
    sentinel = tmp_path / 'sentinel.py'
    sentinel.write_text('old\n')
    target = root / 'file.py'
    target.unlink()
    target.symlink_to(sentinel)
    success, _ = patch_lab.apply_patch(str(root), diff())
    assert sentinel.read_text() == 'old\n'
    assert not success
    assert (source / 'file.py').read_text() == 'old\n'


def test_valid_patch_changes_only_copy(copy):
    source, root = copy
    assert patch_lab.apply_patch(str(root), diff())[0]
    assert (root / 'file.py').read_text() == 'new\n'
    assert (source / 'file.py').read_text() == 'old\n'


@pytest.mark.parametrize('path', ['../sentinel.py', '/tmp/sentinel', 'C:/sentinel',
    'C:sentinel', '//server/share/file', r'\\server\share\file', r'..\sentinel',
    'file.py:stream', './file.py', 'dir//file.py', 'NUL.py', 'file.py.', 'file.py '])
def test_reject_unsafe_paths(copy, path):
    _, root = copy
    assert not patch_lab.validate_patch(diff(path)).valid
    assert not patch_lab.apply_patch(str(root), diff(path))[0]
    assert (root / 'file.py').read_text() == 'old\n'


@pytest.mark.parametrize('patch', [diff(before='stale'), diff('unknown.py'),
    diff().replace('@@ -1 +1 @@', '@@ -1,3 +1,3 @@'),
    diff().replace('--- a/file.py', '--- a/../file.py'),
    diff().replace('+++ b/file.py', '+++ b/other.py'),
    diff() + diff('unknown.py'), diff() + diff()])
def test_bad_patch_never_partially_applies(copy, patch):
    _, root = copy
    assert not patch_lab.apply_patch(str(root), patch)[0]
    assert (root / 'file.py').read_text() == 'old\n'


def test_original_and_unapproved_targets_rejected(copy):
    source, root = copy
    assert not patch_lab.apply_patch(str(source), diff())[0]
    assert not patch_lab.apply_patch(str(root), diff(), allowed=set())[0]
    patch_lab.cleanup_temporary_copy(str(source))
    assert (source / 'file.py').read_text() == 'old\n'


def test_hardlink_cannot_modify_original(copy):
    source, root = copy
    (root / 'file.py').unlink()
    os.link(source / 'file.py', root / 'file.py')
    assert not patch_lab.apply_patch(str(root), diff())[0]
    assert (source / 'file.py').read_text() == 'old\n'


def test_directory_link_cannot_escape(tmp_path):
    source = tmp_path / 'original'
    (source / 'sub').mkdir(parents=True)
    (source / 'sub' / 'file.py').write_text('old\n')
    root = Path(patch_lab.create_temporary_copy(str(source)))
    try:
        (root / 'sub' / 'file.py').unlink()
        (root / 'sub').rmdir()
        (root / 'sub').symlink_to(source / 'sub', target_is_directory=True)
        assert not patch_lab.apply_patch(str(root), diff('sub/file.py'))[0]
        assert (source / 'sub' / 'file.py').read_text() == 'old\n'
    finally:
        patch_lab.cleanup_temporary_copy(str(root))


def test_junction_rejected_on_windows(tmp_path):
    if os.name != 'nt':
        pytest.skip('Windows junction regression')
    import subprocess
    source = tmp_path / 'original'
    (source / 'sub').mkdir(parents=True)
    (source / 'sub' / 'file.py').write_text('old\n')
    root = Path(patch_lab.create_temporary_copy(str(source)))
    try:
        (root / 'sub' / 'file.py').unlink()
        (root / 'sub').rmdir()
        subprocess.run(['cmd', '/c', 'mklink', '/J', str(root / 'sub'), str(source / 'sub')],
                       check=True, capture_output=True)
        assert not patch_lab.apply_patch(str(root), diff('sub/file.py'))[0]
        assert (source / 'sub' / 'file.py').read_text() == 'old\n'
    finally:
        patch_lab.cleanup_temporary_copy(str(root))


def test_crlf_and_no_final_newline():
    from backend.services.diff import apply_diff
    assert apply_diff({'file.py': 'old\r\n'}, diff(), {'file.py'})['file.py'] == 'new\r\n'
    patch = '--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n-old\n\\ No newline at end of file\n+new\n\\ No newline at end of file\n'
    assert apply_diff({'file.py': 'old'}, patch, {'file.py'})['file.py'] == 'new'


def test_guardian_filters_secrets_and_external_links(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    (source / 'file.py').write_text('value = 1\n')
    (source / '.env').write_text('PASSWORD=do-not-copy')
    outside = tmp_path / 'secret.py'
    outside.write_text('outside sentinel')
    (source / 'link.py').symlink_to(outside)
    from backend.services.guardian import capture, open_guardian
    snapshot, _ = capture(open_guardian(str(source)))
    assert snapshot.files == {'file.py': 'value = 1\n'}
    assert snapshot.project_root == 'guardian-snapshot'


def test_tampered_copy_rejected(copy):
    _, root = copy
    (root / 'file.py').write_text('tampered\n')
    assert not patch_lab.apply_patch(str(root), diff(before='tampered'))[0]


def test_owner_directory_link_cannot_redirect_writes(copy, tmp_path):
    source, root = copy
    outside = tmp_path / 'outside'
    (outside / 'project').mkdir(parents=True)
    sentinel = outside / 'project' / 'file.py'
    sentinel.write_bytes(b'old\n')
    owner = root.parent
    backup = owner.with_name(owner.name + '-held')
    assert owner.resolve().parent == backup.absolute().parent
    owner.rename(backup)
    try:
        owner.symlink_to(outside, target_is_directory=True)
        success, _ = patch_lab.apply_patch(str(root), diff())
        assert sentinel.read_text() == 'old\n'
        assert not success
    finally:
        owner.unlink()
        backup.rename(owner)
