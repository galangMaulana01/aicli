import os

def edit_file(filepath, content):
    """Membuat atau mengedit file (overwrite)."""
    try:
        # FIX: Mencegah AI menggunakan path absolut (menghapus '/' atau '\' di awal)
        filepath = filepath.lstrip("\\/")
        
        # Buat folder jika belum ada
        folder_path = os.path.dirname(filepath)
        if folder_path:
            os.makedirs(folder_path, exist_ok=True)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Berhasil menyimpan/mengupdate file: {filepath}"
    except Exception as e:
        return f"Error menulis file {filepath}: {e}"
