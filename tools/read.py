import os

def get_project_structure(root_dir="."):
    """Membaca dan menampilkan struktur folder dan file."""
    structure = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Abaikan hidden folder dan cache
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
        
        level = dirpath.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * level
        folder = os.path.basename(dirpath) or os.path.abspath(root_dir).split(os.sep)[-1]
        structure.append(f"{indent}📁 {folder}/")
        
        subindent = ' ' * 4 * (level + 1)
        for f in filenames:
            if not f.startswith('.'):
                structure.append(f"{subindent}📄 {f}")
    return "\n".join(structure)

def read_file(filepath):
    """Membaca isi file yang diminta AI."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error membaca file {filepath}: {e}"
