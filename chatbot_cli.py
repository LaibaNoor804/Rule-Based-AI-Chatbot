"""
chatbot_cli.py
==============
Terminal interface for RuleBot. Run with:
    python3 chatbot_cli.py
"""

from core.engine import ChatEngine

EXIT_COMMANDS = {"bye", "exit", "quit"}


def print_banner():
    print("=" * 55)
    print(" RuleBot Pro — Terminal Edition")
    print(" Type 'help' for ideas, 'teach: Q => A' to customize me,")
    print(" or 'bye' / 'exit' / 'quit' to stop.")
    print("=" * 55)


def run_chatbot():
    print_banner()
    engine = ChatEngine()

    while True:
        raw_input_text = input("\nYou: ")
        clean_input = raw_input_text.lower().strip()

        if clean_input in EXIT_COMMANDS:
            print("RuleBot: Goodbye! Have a great day. 👋")
            break

        if clean_input == "":
            continue

        turn = engine.get_response(raw_input_text)
        print(f"RuleBot: {turn.bot_reply}")


if __name__ == "__main__":
    run_chatbot()
