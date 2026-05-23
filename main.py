from langchain_core.messages import BaseMessage, HumanMessage

from app.agent.graph import build_graph
from app.session.manager import create_session
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
        if parsed_command == Command.NEW:
            session = create_session(model=session.model)
            conversation_messages = []
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
