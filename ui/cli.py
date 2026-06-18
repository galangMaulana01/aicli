import sys
from core.agent import Agent
from tools.read import get_project_structure

def print_stream(text):
    """Callback untuk menampilkan teks dari Groq secara real-time (streaming)."""
    sys.stdout.write(text)
    sys.stdout.flush()

def run_cli():
    print("="*55)
    print(" 🤖 AI CLI Developer Agent (Groq Edition)")
    print("="*55)
    
    # Otomatis deteksi folder saat CLI pertama kali dijalankan
    print("\n📂 Memindai Struktur Project...")
    print(get_project_structure())
    print("\n" + "="*55)

    # Inisialisasi agent AI
    agent = Agent()
    
    while True:
        try:
            # Ambil input dari terminal pengguna
            user_input = input("\n\n🧑 You: ")
            
            # Cek perintah keluar dari aplikasi
            if user_input.lower() in ['exit', 'quit', 'keluar']:
                print("Sistem dihentikan. 👋")
                break
                
            if not user_input.strip():
                continue
                
            print("\n🤖 AI: ", end="")
            # Jalankan pemrosesan input melalui sistem agent
            agent.process_input(user_input, print_stream)
            
        except KeyboardInterrupt:
            # Mengantisipasi jika user menekan Ctrl+C di terminal
            print("\n\nSistem dihentikan secara paksa. 👋")
            break
