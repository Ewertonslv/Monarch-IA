import pytest
import os
from tools.fs_tools import FsTools


@pytest.fixture
def fs(tmp_path):
    return FsTools(workdir=str(tmp_path))


def test_write_and_read(fs, tmp_path):
    fs.write("src/app.py", "print('hello')")
    content = fs.read("src/app.py")
    assert content == "print('hello')"


def test_write_creates_directories(fs, tmp_path):
    fs.write("a/b/c/deep.py", "# deep")
    assert (tmp_path / "a" / "b" / "c" / "deep.py").exists()


def test_read_missing_raises(fs):
    with pytest.raises(FileNotFoundError):
        fs.read("nonexistent.py")


def test_delete(fs, tmp_path):
    fs.write("del_me.py", "x = 1")
    fs.delete("del_me.py")
    assert not (tmp_path / "del_me.py").exists()


def test_list_returns_relative_paths(fs, tmp_path):
    fs.write("pkg/__init__.py", "")
    fs.write("pkg/mod.py", "")
    paths = fs.list("pkg")
    assert "pkg/__init__.py" in paths
    assert "pkg/mod.py" in paths


def test_exists(fs):
    assert not fs.exists("missing.py")
    fs.write("present.py", "")
    assert fs.exists("present.py")
