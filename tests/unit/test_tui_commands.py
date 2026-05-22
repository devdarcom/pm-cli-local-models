from app.tui.commands import Command, parse_command


def test_parse_command_returns_new_for_new_command():
    result = parse_command("\\new")

    assert result == Command.NEW
