from app.agent.nodes import AGENT_TOOLS
from app.agent.tools import delete_file, list_directory, read_file, search_in_files, write_file


EXPECTED_TOOL_FUNCTIONS = {read_file, list_directory, write_file, delete_file, search_in_files}


def test_agent_tools_exposes_all_five_tools() -> None:
    wrapped_functions = {t.func for t in AGENT_TOOLS}
    assert wrapped_functions == EXPECTED_TOOL_FUNCTIONS
