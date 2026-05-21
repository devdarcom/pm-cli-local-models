import pytest

from app.agent.tools import read_file


def test_read_file_returns_content_when_file_exists(tmp_path):
    target_file = tmp_path / "hello.txt"
    target_file.write_text("zawartość pliku")

    result = read_file(str(target_file))

    assert result == "zawartość pliku"
