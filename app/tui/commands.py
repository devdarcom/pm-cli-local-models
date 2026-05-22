from enum import Enum
from typing import Optional

NEW_COMMAND_LITERAL = "\\new"


class Command(Enum):
    NEW = "new"


def parse_command(text: str) -> Optional[Command]:
    normalized_text = text.strip()
    if normalized_text == NEW_COMMAND_LITERAL:
        return Command.NEW
    return None
