from langchain_core.messages import HumanMessage

from app.agent.graph import build_graph
from app.session.manager import create_session

DEFAULT_MODEL = "qwen2.5:3b"
EXIT_COMMAND = "exit"


def run_chat_loop(graph, session) -> None:
    print(f"Agent gotowy (model: {session.model}). Wpisz '{EXIT_COMMAND}' aby zakończyć.\n")

    while True:
        user_input = input("Ty: ").strip()

        if user_input.lower() == EXIT_COMMAND:
            print("Do widzenia.")
            break

        if not user_input:
            continue

        result = graph.invoke({
            "session_id": session.session_id,
            "model_name": session.model,
            "messages": [HumanMessage(content=user_input)],
        })

        last_message = result["messages"][-1]
        print(f"\nAgent: {last_message.content}\n")


def main() -> None:
    session = create_session(model=DEFAULT_MODEL)
    graph = build_graph()
    run_chat_loop(graph, session)


if __name__ == "__main__":
    main()
