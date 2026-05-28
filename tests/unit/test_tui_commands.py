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


def test_parse_command_returns_spawn_for_spawn_command():
    result = parse_command("\\spawn")

    assert result == ParsedCommand(command=Command.SPAWN)


def test_parse_command_returns_mcp_with_url_for_mcp_command():
    result = parse_command("\\mcp http://localhost:8080")

    assert result == ParsedCommand(command=Command.MCP, arg="http://localhost:8080")


def test_parse_command_returns_skills_for_skills_command():
    result = parse_command("\\skills")

    assert result == ParsedCommand(command=Command.SKILLS)


def test_parse_command_returns_stop_for_stop_command():
    result = parse_command("\\stop")

    assert result == ParsedCommand(command=Command.STOP)
