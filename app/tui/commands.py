from enum import Enum
from typing import Optional

NEW_COMMAND_LITERAL = "\\new"
RESET_COMMAND_LITERAL = "\\reset"


class Command(Enum):
    NEW = "new"
    RESET = "reset"


def parse_command(text: str) -> Optional[Command]:
    normalized_text = text.strip()
    if normalized_text == NEW_COMMAND_LITERAL:
        return Command.NEW
    if normalized_text == RESET_COMMAND_LITERAL:
        return Command.RESET
    return None
