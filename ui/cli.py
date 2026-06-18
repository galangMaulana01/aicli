# ui/cli.py
import sys
from pathlib import Path

from core.agent import run_agent, SYSTEM_PROMPT

RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[36m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
RED    = "\033[31m"
DIM    = "\033[2m"


def _print_banner():
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════╗
║        AI Developer Agent CLI        ║
║   Type /help for available commands  ║
╚══════════════════════════════════════╝{RESET}
""")


def _print_help():
    print(f"""
{YELLOW}Commands:{RESET}
  {BOLD}/help{RESET}      Show help
  {BOLD}/history{RESET}   Show chat history
  {BOLD}/save{RESET}      Save history to log.txt
  {BOLD}/clear{RESET}     Clear history
  {BOLD}/exit{RESET}      Exit CLI
""")


def _format_history(history: list[dict], ansi: bool = True) -> str:
    lines = []
    for msg in history:
        role = msg["role"].upper()
        color = CYAN if role == "ASSISTANT" else GREEN if role == "USER" else DIM

        if ansi:
            lines.append(f"{color}{BOLD}[{role}]{RESET}\n{msg['content']}\n")
        else:
            lines.append(f"[{role}]\n{msg['content']}\n")

    return "\n".join(lines)


def run_cli():
    _print_banner()

    history: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    while True:
        try:
            user_input = input(f"{GREEN}{BOLD}You:{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{DIM}Goodbye.{RESET}")
            sys.exit(0)

        if not user_input:
            continue

        # ─────────────────────────────
        # COMMAND MODE
        # ─────────────────────────────
        if user_input.startswith("/"):
            cmd = user_input.lower()

            if cmd == "/exit":
                sys.exit(0)

            elif cmd == "/help":
                _print_help()

            elif cmd == "/clear":
                history = [{"role": "system", "content": SYSTEM_PROMPT}]
                print(f"{YELLOW}History cleared.{RESET}")

            elif cmd == "/history":
                display = [m for m in history if m["role"] != "system"]
                print(_format_history(display))

            elif cmd == "/save":
                display = [m for m in history if m["role"] != "system"]
                content = _format_history(display, ansi=False)

                Path("log.txt").write_text(content, encoding="utf-8")
                print(f"{YELLOW}Saved to log.txt{RESET}")

            else:
                print(f"{RED}Unknown command.{RESET}")

            continue

        # ─────────────────────────────
        # AGENT MODE
        # ─────────────────────────────
        print(f"\n{CYAN}{BOLD}Agent:{RESET}")

        gen = run_agent(user_input, history)

        for chunk in gen:
            if not isinstance(chunk, str):
                continue

            # 🔥 FILTER: jangan tampilkan tool result mentah
            if "[TOOL_RESULT]" in chunk:
                continue

            print(chunk)

        print()
