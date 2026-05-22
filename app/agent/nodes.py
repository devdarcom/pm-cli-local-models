from pathlib import Path
from typing import Optional

from langchain_core.messages import SystemMessage
from langchain_core.tools import tool as langchain_tool
from langchain_ollama import ChatOllama

from app.agent.state import AgentState
from app.agent.tools import delete_file, list_directory, read_file, search_in_files, write_file

AGENT_TOOLS = [
    langchain_tool(read_file),
    langchain_tool(list_directory),
    langchain_tool(write_file),
    langchain_tool(delete_file),
    langchain_tool(search_in_files),
]

PROJECT_CONTEXT_FILENAME = "PROJECT.md"
AGENTS_MD_FILENAME = "AGENTS.md"
SYSTEM_PROMPT_FILENAME = "system_prompt.md"
CONTEXT_SEPARATOR = "\n\n"


def load_project_context(project_dir: Path = Path(".")) -> Optional[str]:
    project_md = project_dir / PROJECT_CONTEXT_FILENAME
    try:
        return project_md.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except PermissionError as e:
        raise RuntimeError(f"Brak uprawnień do odczytu {project_md}") from e


def load_system_prompt(prompt_path: Path) -> str:
    try:
        return prompt_path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise RuntimeError(f"Wymagany plik nie istnieje: {prompt_path}") from e
    except PermissionError as e:
        raise RuntimeError(f"Brak uprawnień do odczytu {prompt_path}") from e


def load_agents_md(agents_dir: Path = Path(".")) -> Optional[str]:
    agents_md = agents_dir / AGENTS_MD_FILENAME
    try:
        return agents_md.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except PermissionError as e:
        raise RuntimeError(f"Brak uprawnień do odczytu {agents_md}") from e


def _has_system_message(messages: list) -> bool:
    return any(isinstance(m, SystemMessage) for m in messages)


def load_context_node(state: AgentState) -> dict:
    if _has_system_message(state.messages):
        return {}

    project_dir = Path(".")
    system_prompt = load_system_prompt(project_dir / SYSTEM_PROMPT_FILENAME)
    project_context = load_project_context(project_dir)

    # AGENTS.md is a developer guide — not injected into the model context.
    prompt_parts = build_prompt(
        system_prompt=system_prompt,
        project_context=project_context,
    )
    system_message = SystemMessage(content=prompt_parts[0]["content"])
    return {"messages": [system_message] + list(state.messages)}


def _order_messages_for_llm(messages: list) -> list:
    # LLM APIs require system messages to precede user/assistant messages.
    # add_messages reducer appends new messages by ID, so SystemMessage may
    # land at a position other than 0 in state — normalize here before the call.
    system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
    conversation_msgs = [m for m in messages if not isinstance(m, SystemMessage)]
    return system_msgs + conversation_msgs


def call_model(state: AgentState) -> dict:
    model = ChatOllama(model=state.model_name).bind_tools(AGENT_TOOLS)
    response = model.invoke(_order_messages_for_llm(state.messages))
    return {
        "messages": state.messages + [response],
        "recursion_count": state.recursion_count + 1,
    }


def build_prompt(
    system_prompt: str,
    project_context: Optional[str] = None,
    agents_context: Optional[str] = None,
) -> list:
    content = system_prompt
    if agents_context:
        content += CONTEXT_SEPARATOR + agents_context
    if project_context:
        content += CONTEXT_SEPARATOR + project_context
    return [{"role": "system", "content": content}]
