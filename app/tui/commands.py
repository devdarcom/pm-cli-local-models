from dataclasses import dataclass
from enum import Enum
from typing import Optional

NEW_COMMAND_LITERAL = "\\new"
RESET_COMMAND_LITERAL = "\\reset"
COMPRESS_COMMAND_LITERAL = "\\compress"
SPAWN_COMMAND_LITERAL = "\\spawn"
SKILLS_COMMAND_LITERAL = "\\skills"
STOP_COMMAND_LITERAL = "\\stop"
HELP_COMMAND_LITERAL = "\\help"
MCP_COMMAND_PREFIX = "\\mcp "
MODEL_COMMAND_PREFIX = "\\model "


class Command(Enum):
    NEW = "new"
    RESET = "reset"
    COMPRESS = "compress"
    MODEL = "model"
    SPAWN = "spawn"
    MCP = "mcp"
    SKILLS = "skills"
    STOP = "stop"
    HELP = "help"


@dataclass(frozen=True)
class ParsedCommand:
    command: Command
    arg: Optional[str] = None


def parse_command(text: str) -> Optional[ParsedCommand]:
    normalized_text = text.strip()
    if normalized_text == NEW_COMMAND_LITERAL:
        return ParsedCommand(command=Command.NEW)
    if normalized_text == RESET_COMMAND_LITERAL:
        return ParsedCommand(command=Command.RESET)
    if normalized_text == COMPRESS_COMMAND_LITERAL:
        return ParsedCommand(command=Command.COMPRESS)
    if normalized_text == SPAWN_COMMAND_LITERAL:
        return ParsedCommand(command=Command.SPAWN)
    if normalized_text == SKILLS_COMMAND_LITERAL:
        return ParsedCommand(command=Command.SKILLS)
    if normalized_text == STOP_COMMAND_LITERAL:
        return ParsedCommand(command=Command.STOP)
    if normalized_text == HELP_COMMAND_LITERAL:
        return ParsedCommand(command=Command.HELP)
    if normalized_text.startswith(MCP_COMMAND_PREFIX):
        server_url = normalized_text[len(MCP_COMMAND_PREFIX) :].strip()
        if server_url:
            return ParsedCommand(command=Command.MCP, arg=server_url)
    if normalized_text.startswith(MODEL_COMMAND_PREFIX):
        model_name = normalized_text[len(MODEL_COMMAND_PREFIX) :].strip()
        if model_name:
            return ParsedCommand(command=Command.MODEL, arg=model_name)
    return None
