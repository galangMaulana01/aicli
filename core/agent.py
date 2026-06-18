import re
from core.llm import generate_response
from tools.read import read_file
from tools.edit import edit_file

SYSTEM_PROMPT = """Kamu adalah AI Assistant Developer pribadi.
Kamu memiliki kemampuan untuk MENGANALISIS, MEMBACA, dan MENGEDIT file di lokal komputer.

ATURAN PENGGUNAAN TOOLS:
1. Jika kamu butuh membaca file, berikan output dengan format persis:
[READ: path/ke/file.py]
2. Jika kamu butuh membuat atau mengedit file, berikan output dengan format persis:
[EDIT: path/ke/file.py]
```python
isi kode disini
Jika kamu menggunakan tool, tunggu system memberikan hasil balasan kepadamu.
Gunakan bahasa Indonesia yang singkat, jelas, dan profesional."""
class Agent:
    def __init__(self):
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def process_input(self, user_input, stream_callback):
        self.messages.append({"role": "user", "content": user_input})

        while True:
            response_stream = generate_response(self.messages)

            if isinstance(response_stream, str):
                stream_callback(f"\n[API Error] {response_stream}")
                return

            full_response = ""

            for chunk in response_stream:
                delta = chunk.choices[0].delta.content or ""
                full_response += delta
                stream_callback(delta)

            self.messages.append(
                {"role": "assistant", "content": full_response}
            )

            read_match = re.search(r'\[READ:\s*(.+?)\]', full_response)
            edit_match = re.search(
                r'\[EDIT:\s*(.+?)\]\s*```[a-zA-Z]*\n(.*?)```',
                full_response,
                re.DOTALL
            )

            if read_match:
                filepath = read_match.group(1).strip()
                stream_callback(f"\n\n[System: Membaca {filepath}...]\n")

                file_content = read_file(filepath)

                self.messages.append({
                    "role": "system",
                    "content": f"Isi file {filepath}:\n{file_content}"
                })

                stream_callback("\n🤖 AI: ")
                continue

            elif edit_match:
                filepath = edit_match.group(1).strip()
                new_content = edit_match.group(2)

                stream_callback(f"\n\n[System: Menyimpan {filepath}...]\n")

                result = edit_file(filepath, new_content)

                self.messages.append({
                    "role": "system",
                    "content": result
                })

                stream_callback("\n🤖 AI: ")
                continue

            break
