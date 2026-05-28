from app.tui.commands import Command, parse_command


def test_parse_command_returns_new_for_new_command():
    result = parse_command("\\new")

    assert result == Command.NEW


def test_parse_command_returns_reset_for_reset_command():
    result = parse_command("\\reset")

    assert result == Command.RESET


def test_parse_command_returns_compress_for_compress_command():
    result = parse_command("\\compress")

    assert result == Command.COMPRESS
