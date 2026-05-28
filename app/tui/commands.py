from dataclasses import dataclass
from enum import Enum
from typing import Optional

NEW_COMMAND_LITERAL = "\\new"
RESET_COMMAND_LITERAL = "\\reset"
COMPRESS_COMMAND_LITERAL = "\\compress"
MODEL_COMMAND_PREFIX = "\\model "


class Command(Enum):
    NEW = "new"
    RESET = "reset"
    COMPRESS = "compress"
    MODEL = "model"


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
    if normalized_text.startswith(MODEL_COMMAND_PREFIX):
        model_name = normalized_text[len(MODEL_COMMAND_PREFIX) :].strip()
        if model_name:
            return ParsedCommand(command=Command.MODEL, arg=model_name)
    return None
