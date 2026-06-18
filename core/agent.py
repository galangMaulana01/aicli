import re
from typing import Generator
from config import MAX_ITERATIONS
from core.llm import chat
from tools.read import read_file
from tools.edit import edit_file
from tools.scan import scan_directory

# core/agent.py (bagian SYSTEM_PROMPT)
SYSTEM_PROMPT = (
    "Kamu adalah AI Developer Agent CLI.\n"
    "Tugasmu: memahami instruksi bahasa alami dari user, lalu menjalankan tindakan yang diminta.\n"
    "Kamu TIDAK perlu meminta konfirmasi untuk setiap langkah — lakukan langsung.\n"
    "Jika instruksi kompleks, bagi menjadi langkah-langkah kecil dan eksekusi satu per satu.\n\n"
    "CARA MENJALANKAN TINDAKAN:\n"
    "1. Jika user minta membaca file → tulis [READ: path/to/file]\n"
    "2. Jika user minta scan direktori → tulis [SCAN: path/to/dir]\n"
    "3. Jika user minta mengubah file → tulis [EDIT: path/to/file] diikuti blok kode lengkap dalam triple backticks.\n"
    "   Contoh:\n"
    "   [EDIT: ./ui/cli.py]\n"
    "   ```python\n"
    "   # kode baru\n"
    "   ```\n\n"
    "Aturan:\n"
    "- SATU TOOL per respons. Jangan gabungkan beberapa tool.\n"
    "- Jika tool sudah dieksekusi, lihat hasilnya dan lanjutkan ke langkah berikutnya.\n"
    "- Jangan ulangi tool yang sama jika sudah berhasil.\n"
    "- Jika menemui error, beritahu user dan tawarkan solusi.\n"
    "- Jangan mengubah file yang diproteksi: core/agent.py, core/llm.py, main.py, config.py.\n"
    "- Jika user meminta sesuatu yang tidak bisa dilakukan, jelaskan dengan jelas.\n"
    "- PENTING: Setelah semua langkah selesai, berikan ringkasan akhir dan JANGAN keluarkan tool apapun lagi. Akhiri respons tanpa tag [READ:], [SCAN:], atau [EDIT:].\n"
)

# Regex untuk mendeteksi tag (tetap sama)
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
        return f"BLOCKED: {path} (protected)"
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
    for _ in range(MAX_ITERATIONS):
        response = chat(history)
        history.append({"role": "assistant", "content": response})
        tools = _detect_tools(response)
        if not tools:
            # Tidak ada tool — kirim respons langsung
            yield response
            return history
        # Eksekusi tool
        result = _execute_tool(tools[0])
        history.append({"role": "system", "content": result})
        yield f"[TOOL RESULT]\n{result}"  # tampilkan hasil ke user
        # Loop berlanjut agar agent bisa merespons hasil
    yield "[STOP] max iteration reached"
    return history
