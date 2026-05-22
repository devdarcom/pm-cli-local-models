import pytest

from app.agent.tools import list_directory, read_file, write_file


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


def test_write_file_creates_file_with_given_content(tmp_path):
    target_file = tmp_path / "output.txt"

    result = write_file(str(target_file), "nowa treść")

    assert target_file.read_text(encoding="utf-8") == "nowa treść"
    assert "output.txt" in result
