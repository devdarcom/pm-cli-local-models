from app.tui.commands import Command, ParsedCommand, parse_command


def test_parse_command_returns_new_for_new_command():
    result = parse_command("\\new")

    assert result == ParsedCommand(command=Command.NEW)


def test_parse_command_returns_reset_for_reset_command():
    result = parse_command("\\reset")

    assert result == ParsedCommand(command=Command.RESET)


def test_parse_command_returns_compress_for_compress_command():
    result = parse_command("\\compress")

    assert result == ParsedCommand(command=Command.COMPRESS)


def test_parse_command_returns_model_with_argument_for_model_command():
    result = parse_command("\\model llama3.2:3b")

    assert result == ParsedCommand(command=Command.MODEL, arg="llama3.2:3b")
