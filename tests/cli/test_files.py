import errno
import os

import pytest

from omoonodes import files


def test_directory_replacement_across_filesystems(tmp_path, monkeypatch):
    source = tmp_path / "prepared"
    source.mkdir()
    (source / "asset").write_text("new")
    target = tmp_path / "output"
    rename = os.rename

    def cross_device_rename(src, dst):
        if str(src) == str(source):
            raise OSError(errno.EXDEV, "Cross-device link")
        return rename(src, dst)

    monkeypatch.setattr(os, "rename", cross_device_rename)
    files.replace_directories([(source, target)])
    assert (target / "asset").read_text() == "new"
    assert not source.exists()


def test_directory_transaction_restores_both_libraries_on_failure(tmp_path, monkeypatch):
    prepared = tmp_path / "prepared"
    prepared.mkdir()
    target = tmp_path / "libraries/A"
    target.mkdir(parents=True)
    (target / "original").write_text("keep")
    (prepared / "replacement").write_text("new")
    missing = tmp_path / "missing"
    with pytest.raises(FileNotFoundError):
        files.replace_directories([(prepared, target), (missing, tmp_path / "libraries/B")])
    assert (target / "original").read_text() == "keep"
    assert not (target / "replacement").exists()
    assert not target.with_name("A.nodes-backup").exists()
