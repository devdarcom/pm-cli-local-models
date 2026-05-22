import pytest
from unittest.mock import patch

from app.agent.tools import delete_file, list_directory, read_file, search_in_files, write_file


def test_read_file_returns_content_when_file_exists(tmp_path):
    target_file = tmp_path / "hello.txt"
    target_file.write_text("zawartość pliku")

    result = read_file(str(target_file))

    assert result == "zawartość pliku"


def test_list_directory_returns_file_list(tmp_path):
    (tmp_path / "plik_a.txt").write_text("a")
    (tmp_path / "plik_b.py").write_text("b")

    result = list_directory(str(tmp_path))

    assert "plik_a.txt" in result
    assert "plik_b.py" in result


def test_read_file_returns_error_when_file_not_found():
    result = read_file("/nonexistent/path/file.txt")

    assert "BŁĄD" in result
    assert "/nonexistent/path/file.txt" in result


def test_read_file_returns_error_on_permission_denied(tmp_path):
    target = tmp_path / "secret.txt"
    target.write_text("sekret")

    with patch("app.agent.tools.Path.read_text", side_effect=PermissionError):
        result = read_file(str(target))

    assert "BŁĄD" in result
    assert str(target) in result


def test_search_in_files_returns_files_containing_phrase(tmp_path):
    (tmp_path / "match.txt").write_text("szukana fraza tutaj")
    (tmp_path / "no_match.txt").write_text("zupełnie inna treść")

    result = search_in_files(str(tmp_path), "szukana fraza")

    assert "match.txt" in result
    assert "no_match.txt" not in result


def test_search_in_files_returns_empty_list_when_phrase_not_found(tmp_path):
    (tmp_path / "plik.txt").write_text("brak pasującej treści")

    result = search_in_files(str(tmp_path), "nieistniejąca fraza")

    assert result == []


def test_delete_file_returns_error_when_file_not_found():
    result = delete_file("/nonexistent/path/file.txt")

    assert "BŁĄD" in result
    assert "/nonexistent/path/file.txt" in result


def test_delete_file_removes_file_and_returns_status(tmp_path):
    target = tmp_path / "to_delete.txt"
    target.write_text("zawartość")

    result = delete_file(str(target))

    assert not target.exists()
    assert "to_delete.txt" in result


def test_list_directory_returns_error_when_directory_not_found():
    result = list_directory("/nonexistent/directory")

    assert len(result) == 1
    assert "BŁĄD" in result[0]


def test_write_file_returns_error_when_directory_not_found(tmp_path):
    result = write_file(str(tmp_path / "nonexistent" / "file.txt"), "treść")

    assert "BŁĄD" in result


def test_write_file_creates_file_with_given_content(tmp_path):
    target_file = tmp_path / "output.txt"

    result = write_file(str(target_file), "nowa treść")

    assert target_file.read_text(encoding="utf-8") == "nowa treść"
    assert "output.txt" in result
