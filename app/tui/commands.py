from enum import Enum
from typing import Optional

NEW_COMMAND_LITERAL = "\\new"
RESET_COMMAND_LITERAL = "\\reset"
COMPRESS_COMMAND_LITERAL = "\\compress"


class Command(Enum):
    NEW = "new"
    RESET = "reset"
    COMPRESS = "compress"


def parse_command(text: str) -> Optional[Command]:
    normalized_text = text.strip()
    if normalized_text == NEW_COMMAND_LITERAL:
        return Command.NEW
    if normalized_text == RESET_COMMAND_LITERAL:
        return Command.RESET
    if normalized_text == COMPRESS_COMMAND_LITERAL:
        return Command.COMPRESS
    return None
