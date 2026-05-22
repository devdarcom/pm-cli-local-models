from pathlib import Path
from typing import Any, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool as langchain_tool
from langchain_ollama import ChatOllama

from app.agent.state import AgentState, RECURSION_LIMIT
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
MAX_MODEL_RETRIES = 3
COMPRESSION_MODEL_NAME = "gemma3:4b"
COMPRESSED_CONTEXT_PREFIX = "[Skompresowany kontekst]"
_BOUND_MODEL_CACHE: dict[str, Any] = {}


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


def _get_bound_model(model_name: str) -> Any:
    if model_name not in _BOUND_MODEL_CACHE:
        _BOUND_MODEL_CACHE[model_name] = ChatOllama(model=model_name).bind_tools(AGENT_TOOLS)
    return _BOUND_MODEL_CACHE[model_name]


def call_model(state: AgentState) -> dict:
    if state.recursion_count >= RECURSION_LIMIT:
        return {
            "error_type": "recursion_limit",
            "error_node": "call_model",
            "last_error": (
                f"Osiągnięto limit kroków agenta ({RECURSION_LIMIT}). "
                "Zatrzymuję dalsze wywołania modelu."
            ),
        }

    model = _get_bound_model(state.model_name)
    try:
        response = model.invoke(_order_messages_for_llm(state.messages))
    except Exception as e:
        return {
            "error_type": "model_error",
            "error_node": "call_model",
            "last_error": str(e),
        }

    return {
        "messages": [response],
        "recursion_count": state.recursion_count + 1,
        "retry_count": 0,
        "last_error": None,
        "error_node": None,
        "error_type": None,
    }


def error_handler_node(state: AgentState) -> dict:
    next_retry_count = state.retry_count + 1
    error_feedback = HumanMessage(
        content=(
            f"[FEEDBACK BŁĘDU — próba {next_retry_count}/{MAX_MODEL_RETRIES}]\n"
            f"{state.last_error or 'Nieznany błąd'}\n\n"
            "Spróbuj innego podejścia i zwróć poprawny wynik."
        )
    )
    return {
        "messages": [error_feedback],
        "retry_count": next_retry_count,
        "error_type": None,
        "error_node": None,
    }


def escalate_to_user_node(state: AgentState) -> dict:
    if state.error_type == "recursion_limit":
        message = (
            f"⚠️ Osiągnięto limit kroków agenta ({RECURSION_LIMIT}). "
            "Przerywam bieżące zadanie, aby uniknąć zapętlenia."
        )
    else:
        message = (
            f"⚠️ Nie udało się wykonać zadania po {MAX_MODEL_RETRIES} próbach.\n"
            f"Ostatni błąd: {state.last_error or 'nieznany'}"
        )

    return {
        "messages": [AIMessage(content=message)],
        "retry_count": 0,
        "last_error": None,
        "error_node": None,
        "error_type": None,
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


def compress_history(messages: list[dict[str, str]], summary: str) -> list[dict[str, str]]:
    if not messages:
        return []

    system_message = next((message for message in messages if message.get("role") == "system"), messages[0])
    summary_message = {
        "role": "assistant",
        "content": f"{COMPRESSED_CONTEXT_PREFIX} {summary}",
    }
    return [system_message, summary_message]


def _format_messages_for_summary(messages: list[Any]) -> str:
    formatted_lines: list[str] = []
    for message in messages:
        role = getattr(message, "type", message.__class__.__name__)
        content = getattr(message, "content", str(message))
        formatted_lines.append(f"{role}: {content}")
    return "\n".join(formatted_lines)


def compress_node(state: AgentState) -> dict:
    compression_prompt = (
        "Skompresuj poniższą historię rozmowy do krótkiego podsumowania, "
        "zachowując kluczowe decyzje i stan zadania.\n\n"
        f"{_format_messages_for_summary(state.messages)}"
    )
    compression_model = ChatOllama(model=COMPRESSION_MODEL_NAME)
    response = compression_model.invoke([HumanMessage(content=compression_prompt)])
    return {"summary": response.content}
