# ui/cli.py
import sys
import json
from pathlib import Path
from datetime import datetime
from core.agent import run_agent, SYSTEM_PROMPT
from config import MODEL_NAME, NVIDIA_API_KEY, MAX_TOKENS, MAX_ITERATIONS, PROJECT_ROOT
from utils.logger import log_interaction

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
DIM = "\033[2m"

_iteration_count = 0

def _print_banner():
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════╗
║ AI Developer Agent CLI               ║
║ Type /help for available commands    ║
╚══════════════════════════════════════╝{RESET}
""")

def _print_help():
    print(f"""
{YELLOW}Commands:{RESET}
  {BOLD}/help{RESET}          Show this help
  {BOLD}/history{RESET}       Show chat history
  {BOLD}/save{RESET}          Save history to log.txt
  {BOLD}/clear{RESET}         Clear history
  {BOLD}/status{RESET}        Show current status
  {BOLD}/export{RESET}        Export history to history_*.txt
  {BOLD}/log{RESET}           Show last 10 messages
  {BOLD}/exit{RESET}          Exit CLI
  {BOLD}/test{RESET}          Run internal system tests
  {BOLD}/config{RESET}        Show current configuration
  {BOLD}/session save <name>{RESET}  Save session
  {BOLD}/session load <name>{RESET}  Load session
  {BOLD}/session list{RESET}  List saved sessions
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

def _format_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def _run_internal_tests():
    print(f"{CYAN}{BOLD}Running internal system tests...{RESET}\n")
    passed = 0
    total = 7

    if not SYSTEM_PROMPT.strip():
        print(f"{RED}❌ Test 1 FAILED: SYSTEM_PROMPT is empty.{RESET}")
    else:
        print(f"{GREEN}✅ Test 1 PASSED: SYSTEM_PROMPT is defined.{RESET}")
        passed += 1

    import inspect
    if not callable(run_agent):
        print(f"{RED}❌ Test 2 FAILED: run_agent is not callable.{RESET}")
    else:
        print(f"{GREEN}✅ Test 2 PASSED: run_agent is callable.{RESET}")
        passed += 1

    test_history = [{"role": "system", "content": "test"}]
    try:
        gen = run_agent("What is the current directory?", test_history)
        next(gen)
        print(f"{GREEN}✅ Test 3 PASSED: Agent can respond to basic query.{RESET}")
        passed += 1
    except Exception as e:
        print(f"{RED}❌ Test 3 FAILED: {e}{RESET}")

    try:
        cwd = Path.cwd()
        print(f"{GREEN}✅ Test 4 PASSED: Current directory accessible: {cwd}{RESET}")
        passed += 1
    except Exception as e:
        print(f"{RED}❌ Test 4 FAILED: {e}{RESET}")

    temp_file = Path("test_temp.txt")
    try:
        temp_file.write_text("hello", encoding="utf-8")
        content = temp_file.read_text(encoding="utf-8")
        if content == "hello":
            print(f"{GREEN}✅ Test 5 PASSED: File I/O works.{RESET}")
            passed += 1
        else:
            print(f"{RED}❌ Test 5 FAILED: Content mismatch.{RESET}")
        temp_file.unlink()
    except Exception as e:
        print(f"{RED}❌ Test 5 FAILED: {e}{RESET}")

    non_existent = Path("non_existent_file_abc123.txt")
    try:
        non_existent.read_text(encoding="utf-8")
        print(f"{RED}❌ Test 6 FAILED: Should have raised FileNotFoundError.{RESET}")
    except FileNotFoundError:
        print(f"{GREEN}✅ Test 6 PASSED: FileNotFoundError caught.{RESET}")
        passed += 1
    except Exception as e:
        print(f"{RED}❌ Test 6 FAILED: {e}{RESET}")

    tools_dir = Path("./tools")
    try:
        if not tools_dir.exists():
            print(f"{RED}❌ Test 7 FAILED: tools/ not found.{RESET}")
        else:
            files = [f.name for f in tools_dir.iterdir() if f.is_file()]
            if files:
                print(f"{GREEN}✅ Test 7 PASSED: tools/ found {len(files)} files.{RESET}")
                passed += 1
            else:
                print(f"{YELLOW}⚠️ Test 7: tools/ empty.{RESET}")
                passed += 1
    except Exception as e:
        print(f"{RED}❌ Test 7 FAILED: {e}{RESET}")

    print(f"\n{CYAN}{BOLD}Test Summary:{RESET}")
    print(f" {passed}/{total} tests PASSED")
    if passed == total:
        print(f"{GREEN}🎉 ALL TESTS PASSED!{RESET}")
    else:
        print(f"{RED}⚠️ Some tests FAILED.{RESET}")
    print()

def _show_config():
    print(f"{CYAN}{BOLD}System Configuration:{RESET}")
    api_key_display = NVIDIA_API_KEY[:4] + "*" * (len(NVIDIA_API_KEY) - 4) if NVIDIA_API_KEY else "[NOT SET]"
    print(f"  NVIDIA_API_KEY: {api_key_display}")
    print(f"  MODEL_NAME: {MODEL_NAME or '[NOT SET]'}")
    print(f"  MAX_TOKENS: {MAX_TOKENS}")
    print(f"  MAX_ITERATIONS: {MAX_ITERATIONS}")
    print(f"  PROJECT_ROOT: {PROJECT_ROOT}")
    print()

def _save_session(history: list[dict], name: str):
    try:
        session_data = [msg for msg in history if msg["role"] in ("user", "assistant")]
        filename = f"session_{name}.json"
        Path(filename).write_text(
            json.dumps({
                "timestamp": datetime.now().isoformat(),
                "session_name": name,
                "message_count": len(session_data),
                "messages": session_data
            }, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"{GREEN}✅ Session saved to {filename}{RESET}")
        log_interaction("system", f"Session saved as {filename}")
    except Exception as e:
        print(f"{RED}❌ Failed to save session: {e}{RESET}")

def _load_session(name: str) -> list[dict]:
    filename = f"session_{name}.json"
    try:
        data = json.loads(Path(filename).read_text(encoding="utf-8"))
        messages = data.get("messages", [])
        print(f"{GREEN}✅ Loaded session '{name}' with {len(messages)} messages.{RESET}")
        return messages
    except FileNotFoundError:
        print(f"{RED}❌ Session '{name}' not found.{RESET}")
        return []
    except Exception as e:
        print(f"{RED}❌ Failed to load session: {e}{RESET}")
        return []

def _list_sessions():
    sessions = list(Path(".").glob("session_*.json"))
    if not sessions:
        print(f"{YELLOW}No saved sessions found.{RESET}")
        return
    print(f"{CYAN}Saved sessions:{RESET}")
    for s in sessions:
        print(f"  - {s.name}")

def run_cli():
    global _iteration_count
    _print_banner()
    history: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_input = input(f"{GREEN}{BOLD}You:{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{DIM}Goodbye.{RESET}")
            sys.exit(0)
        if not user_input:
            continue

        if user_input.startswith("/"):
            parts = user_input.split()
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else None

            if cmd == "/exit":
                sys.exit(0)
            elif cmd == "/help":
                _print_help()
            elif cmd == "/clear":
                history = [{"role": "system", "content": SYSTEM_PROMPT}]
                _iteration_count = 0
                print(f"{YELLOW}History cleared.{RESET}")
            elif cmd == "/history":
                display = [m for m in history if m["role"] != "system"]
                print(_format_history(display))
            elif cmd == "/save":
                display = [m for m in history if m["role"] != "system"]
                content = _format_history(display, ansi=False)
                Path("log.txt").write_text(content, encoding="utf-8")
                print(f"{YELLOW}Saved to log.txt{RESET}")
            elif cmd == "/status":
                print(f"{CYAN}Status:{RESET}")
                print(f"  Working dir: {Path.cwd()}")
                print(f"  Total messages: {len([m for m in history if m['role'] != 'system'])}")
                print(f"  Iterations used: {_iteration_count}")
                total_chars = sum(len(m["content"]) for m in history)
                est_tokens = total_chars // 4
                print(f"  Estimated tokens: ~{est_tokens}")
            elif cmd == "/export":
                display = [m for m in history if m["role"] != "system"]
                content = _format_history(display, ansi=False)
                filename = f"history_{_format_timestamp()}.txt"
                Path(filename).write_text(content, encoding="utf-8")
                print(f"{YELLOW}Exported to {filename}{RESET}")
            elif cmd == "/log":
                display = [m for m in history if m["role"] != "system"]
                last10 = display[-10:] if len(display) >= 10 else display
                print(_format_history(last10))
            elif cmd == "/test":
                _run_internal_tests()
            elif cmd == "/config":
                _show_config()
            elif cmd == "/session":
                if arg == "save" and len(parts) > 2:
                    _save_session(history, parts[2])
                elif arg == "load" and len(parts) > 2:
                    loaded = _load_session(parts[2])
                    if loaded:
                        history = [{"role": "system", "content": SYSTEM_PROMPT}] + loaded
                        print(f"{GREEN}Session loaded. Continue chatting!{RESET}")
                elif arg == "list":
                    _list_sessions()
                else:
                    print(f"{RED}Usage: /session save <name> | /session load <name> | /session list{RESET}")
            else:
                print(f"{RED}Unknown command. Type /help for list.{RESET}")
            continue

        print(f"\n{CYAN}{BOLD}Agent:{RESET}")
        gen = run_agent(user_input, history)
        while True:
            try:
                chunk = next(gen)
                if isinstance(chunk, str):
                    if chunk.startswith("[TOOL RESULT]"):
                        content = chunk.split("\n", 1)[-1]
                        if content.strip():
                            print(f"{DIM}└─ {content}{RESET}")
                    elif chunk == "[STOP] max iteration reached":
                        pass
                    else:
                        print(chunk)
            except StopIteration as e:
                history = e.value
                tool_results = [m for m in history if m["role"] == "system" and "[TOOL_RESULT]" in m["content"]]
                _iteration_count = len(tool_results)
                break
        print()
