import pytest
from unittest.mock import patch

from app.agent.tools import (
    MAX_SEARCH_FILE_SIZE,
    delete_file,
    list_directory,
    read_file,
    search_in_files,
    write_file,
)


def test_read_file_returns_content_when_file_exists(tmp_path):
    target_file = tmp_path / "hello.txt"
    target_file.write_text("zawartość pliku")

    result = read_file(str(target_file))

    assert result["ok"] is True
    assert result["data"] == "zawartość pliku"
    assert result["error"] is None


def test_list_directory_returns_file_list(tmp_path):
    (tmp_path / "plik_a.txt").write_text("a")
    (tmp_path / "plik_b.py").write_text("b")

    result = list_directory(str(tmp_path))

    assert result["ok"] is True
    assert "plik_a.txt" in result["data"]
    assert "plik_b.py" in result["data"]


def test_read_file_returns_error_when_file_not_found():
    result = read_file("/nonexistent/path/file.txt")

    assert result["ok"] is False
    assert "BŁĄD" in result["error"]
    assert "/nonexistent/path/file.txt" in result["error"]


def test_read_file_resolves_unique_filename_in_project_tree(tmp_path, monkeypatch):
    nested = tmp_path / "app" / "session"
    nested.mkdir(parents=True)
    manager = nested / "manager.py"
    manager.write_text("print('ok')")
    monkeypatch.chdir(tmp_path)

    result = read_file("manager.py")

    assert result["ok"] is True
    assert "print('ok')" in result["data"]


def test_read_file_resolves_unique_filename_ignoring_venv_files(tmp_path, monkeypatch):
    source_dir = tmp_path / "app" / "session"
    source_dir.mkdir(parents=True)
    (source_dir / "manager.py").write_text("print('source')")

    venv_dir = tmp_path / ".venv" / "lib"
    venv_dir.mkdir(parents=True)
    (venv_dir / "manager.py").write_text("print('venv')")

    monkeypatch.chdir(tmp_path)

    result = read_file("manager.py")

    assert result["ok"] is True
    assert result["data"] == "print('source')"


def test_read_file_returns_disambiguation_when_filename_not_unique(tmp_path, monkeypatch):
    first_dir = tmp_path / "app" / "session"
    second_dir = tmp_path / "tests"
    first_dir.mkdir(parents=True)
    second_dir.mkdir(parents=True)
    (first_dir / "manager.py").write_text("first")
    (second_dir / "manager.py").write_text("second")
    monkeypatch.chdir(tmp_path)

    result = read_file("manager.py")

    assert result["ok"] is False
    assert "wiele plików" in result["error"]
    assert len(result["data"]["candidates"]) == 2


def test_read_file_returns_error_on_permission_denied(tmp_path):
    target = tmp_path / "secret.txt"
    target.write_text("sekret")

    with patch("app.agent.tools.Path.read_text", side_effect=PermissionError):
        result = read_file(str(target))

    assert result["ok"] is False
    assert "BŁĄD" in result["error"]
    assert str(target) in result["error"]


def test_search_in_files_returns_files_containing_phrase(tmp_path):
    (tmp_path / "match.txt").write_text("szukana fraza tutaj")
    (tmp_path / "no_match.txt").write_text("zupełnie inna treść")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "second_match.txt").write_text("szukana fraza także tu")

    result = search_in_files(str(tmp_path), "szukana fraza")

    assert result["ok"] is True
    assert "match.txt" in result["data"]["matches"]
    assert "nested/second_match.txt" in result["data"]["matches"]
    assert "no_match.txt" not in result["data"]["matches"]


def test_search_in_files_returns_empty_list_when_phrase_not_found(tmp_path):
    (tmp_path / "plik.txt").write_text("brak pasującej treści")

    result = search_in_files(str(tmp_path), "nieistniejąca fraza")

    assert result["ok"] is True
    assert result["data"]["matches"] == []


def test_search_in_files_skips_large_files(tmp_path):
    big_file = tmp_path / "duzy.txt"
    big_file.write_text("x" * (MAX_SEARCH_FILE_SIZE + 1))

    result = search_in_files(str(tmp_path), "x")

    assert result["ok"] is True
    assert "duzy.txt" not in result["data"]["matches"]
    assert "duzy.txt" in result["data"]["skipped_files"]


def test_delete_file_returns_error_when_file_not_found():
    result = delete_file("/nonexistent/path/file.txt")

    assert result["ok"] is False
    assert "BŁĄD" in result["error"]
    assert "/nonexistent/path/file.txt" in result["error"]


def test_delete_file_removes_file_and_returns_status(tmp_path):
    target = tmp_path / "to_delete.txt"
    target.write_text("zawartość")

    result = delete_file(str(target))

    assert not target.exists()
    assert result["ok"] is True
    assert "to_delete.txt" in result["data"]


def test_list_directory_returns_error_when_directory_not_found():
    result = list_directory("/nonexistent/directory")

    assert result["ok"] is False
    assert "BŁĄD" in result["error"]


def test_write_file_returns_error_when_directory_not_found(tmp_path):
    result = write_file(str(tmp_path / "nonexistent" / "file.txt"), "treść")

    assert result["ok"] is False
    assert "BŁĄD" in result["error"]


def test_write_file_creates_file_with_given_content(tmp_path):
    target_file = tmp_path / "output.txt"

    result = write_file(str(target_file), "nowa treść")

    assert target_file.read_text(encoding="utf-8") == "nowa treść"
    assert result["ok"] is True
    assert "output.txt" in result["data"]
