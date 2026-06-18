import re
from typing import Generator

from config import MAX_ITERATIONS
from core.llm import chat
from tools.read import read_file
from tools.edit import edit_file
from tools.scan import scan_directory

SYSTEM_PROMPT = (
    "Kamu adalah AI Developer Agent CLI.\n"
    "SATU TOOL PER RESPONSE. STOP setelah tool.\n"
    "Gunakan tool hanya jika user minta eksplisit.\n\n"
    "[READ:], [EDIT:], [SCAN:] hanya format valid.\n"
    "Jangan auto scan, jangan auto edit.\n"
)

_RE_READ = re.compile(r"\[READ:\s*(?P<path>[^\]]+)\]")
_RE_SCAN = re.compile(r"\[SCAN:\s*(?P<path>[^\]]+)\]")
_RE_EDIT = re.compile(
    r"\[EDIT:\s*(?P<path>[^\]]+)\]\s*```(?:[a-zA-Z0-9_.-]*)\n(?P<code>.*?)```",
    re.DOTALL
)

PROTECTED_FILES = {
    "core/agent.py",
    "core/llm.py",
    "main.py",
    "config.py"
}


def _detect_tools(text: str):
    if "[TOOL_RESULT]" in text:
        return []

    hits = []

    for m in _RE_READ.finditer(text):
        hits.append({"type": "read", "path": m.group("path").strip()})

    for m in _RE_SCAN.finditer(text):
        hits.append({"type": "scan", "path": m.group("path").strip()})

    for m in _RE_EDIT.finditer(text):
        hits.append({
            "type": "edit",
            "path": m.group("path").strip(),
            "code": m.group("code")
        })

    return hits[:1]  # 1 tool only


def _execute_tool(tool: dict) -> str:
    kind = tool["type"]
    path = tool["path"]

    if kind == "edit" and path in PROTECTED_FILES:
        return f"BLOCKED: {path}"

    if kind == "read":
        result = read_file(path)
        return f"[TOOL_RESULT]\n{result}"

    if kind == "scan":
        result = scan_directory(path)
        return f"[TOOL_RESULT]\n{result}"

    if kind == "edit":
        result = edit_file(path, tool["code"])
        return f"[TOOL_RESULT]\n{result}"

    return "[TOOL_RESULT]\nERROR"


def run_agent(user_message: str, history: list[dict]) -> Generator[str, None, list[dict]]:
    history.append({"role": "user", "content": user_message})

    tool_used = False

    for _ in range(MAX_ITERATIONS):
        response = chat(history)

        history.append({"role": "assistant", "content": response})

        tools = _detect_tools(response)

        if not tools:
            yield response
            return history

        if tool_used:
            return history

        tool_used = True

        result = _execute_tool(tools[0])

        history.append({
            "role": "system",
            "content": result
        })

    yield "[STOP] max iteration reached"
    return history
