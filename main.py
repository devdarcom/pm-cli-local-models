from langchain_core.messages import BaseMessage, HumanMessage

from app.agent.graph import build_graph
from app.mcp.client import connect_mcp
from app.agent.nodes import compress_node
from app.agent.spawn import SessionContext, start_spawn_flow
from app.agent.state import AgentState
from app.session.manager import create_session, set_model
from app.skills.loader import list_skills
from app.tui.commands import Command, parse_command

DEFAULT_MODEL = "llama3.2:3b"
EXIT_COMMAND = "exit"


def run_chat_loop(graph, session) -> None:
    print(f"Agent gotowy (model: {session.model}). Wpisz '{EXIT_COMMAND}' aby zakończyć.\n")
    conversation_messages: list[BaseMessage] = []

    while True:
        user_input = input("Ty: ").strip()

        if user_input.lower() == EXIT_COMMAND:
            print("Do widzenia.")
            break

        if not user_input:
            continue

        parsed_command = parse_command(user_input)
        if parsed_command is not None:
            if parsed_command.command == Command.NEW:
                session = create_session(model=session.model)
                conversation_messages = []
            elif parsed_command.command == Command.RESET:
                conversation_messages = []
            elif parsed_command.command == Command.COMPRESS:
                if conversation_messages:
                    compression_state = AgentState(
                        session_id=session.session_id,
                        model_name=session.model,
                        messages=conversation_messages,
                    )
                    compression_result = compress_node(compression_state)
                    conversation_messages = list(compression_result["messages"])
            elif parsed_command.command == Command.MODEL:
                set_model(session, parsed_command.arg)
            elif parsed_command.command == Command.SPAWN:
                start_spawn_flow(SessionContext(
                    session_id=session.session_id,
                    model_name=session.model,
                ))
            elif parsed_command.command == Command.MCP:
                connect_mcp(session.session_id, parsed_command.arg)
            elif parsed_command.command == Command.SKILLS:
                available_skills = list_skills()
                print("\n".join(available_skills))
                print()
            continue

        turn_messages = conversation_messages + [HumanMessage(content=user_input)]
        result = graph.invoke({
            "session_id": session.session_id,
            "model_name": session.model,
            "messages": turn_messages,
        })
        conversation_messages = list(result["messages"])

        last_message = result["messages"][-1]
        print(f"\nAgent: {last_message.content}\n")


def main() -> None:
    session = create_session(model=DEFAULT_MODEL)
    graph = build_graph()
    run_chat_loop(graph, session)


if __name__ == "__main__":
    main()
