"""
Modul scan direktori untuk Nexus V1.
=====================================
Menyediakan dua cara untuk melihat struktur proyek:
1. `scan_directory` -> string pohon (seperti perintah 'tree').
2. `scan_to_dict`   -> dictionary bersarang (siap di-serialize ke JSON).

Keamanan:
- Symlink tidak diikuti.
- Hanya bekerja di dalam root yang diberikan.
- Daftar pengecualian default mengabaikan direktori yang tidak relevan.
- Batasan kedalaman dan jumlah entri untuk proyek besar.
"""

from pathlib import Path
from typing import Optional, Set, Tuple, List, Dict, Any

# ── Default pengecualian ──────────────────────────────────────────────
# Dapat diganti oleh pemanggil melalui parameter `exclude`.
DEFAULT_EXCLUDE: Set[str] = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    ".vscode",
    ".idea",
}


def scan_directory(
    root: Path,
    exclude: Optional[Set[str]] = None,
    max_depth: Optional[int] = None,
    max_entries: Optional[int] = None,
) -> str:
    """
    Pindai direktori `root` secara rekursif, kembalikan string pohon direktori.

    Args:
        root: Path ke direktori target (biasanya Path.cwd() / Path(".")).
        exclude: Set nama file/direktori yang diabaikan (case-sensitive).
                 None berarti menggunakan DEFAULT_EXCLUDE.
        max_depth: Batas kedalaman rekursi (None = tidak terbatas).
        max_entries: Batas total simpul (file+dir) yang dimasukkan ke hasil.
                     Jika terlampaui, pohon dipotong dan ditambahkan "... (dibatasi)".

    Returns:
        String representasi pohon direktori dengan root ".".
    """
    if not root.is_dir():
        raise ValueError(f"'{root}' bukan direktori.")

    exclude = exclude if exclude is not None else DEFAULT_EXCLUDE
    counter = [0]
    root_node, truncated = _build_tree(
        current_path=root,
        node_name=".",              # tampilkan root sebagai "."
        exclude=exclude,
        max_depth=max_depth,
        current_depth=0,
        max_entries=max_entries,
        counter=counter,
    )

    lines = _format_tree_to_lines(root_node)
    if truncated:
        lines.append("... (dibatasi)")
    return "\n".join(lines)


def scan_to_dict(
    root: Path,
    exclude: Optional[Set[str]] = None,
    max_depth: Optional[int] = None,
    max_entries: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Pindai direktori `root` secara rekursif, kembalikan struktur pohon sebagai dict.

    Struktur yang dihasilkan:
        {
            "name": ".",
            "type": "directory",
            "children": [
                {"name": "file.py", "type": "file", "is_symlink": false},
                {"name": "subdir", "type": "directory", "is_symlink": false, "children": [...]},
                ...
            ],
            "truncated": true   # hanya jika max_entries terlampaui
        }

    Args:
        root: Path ke direktori target.
        exclude: Set nama file/direktori yang diabaikan.
        max_depth: Batas kedalaman rekursi (None = tidak terbatas).
        max_entries: Batas total simpul yang dikumpulkan.
                     Jika terlampaui, dict akan memiliki kunci "truncated": true.

    Returns:
        Dictionary bersarang yang merepresentasikan pohon direktori.
    """
    if not root.is_dir():
        raise ValueError(f"'{root}' bukan direktori.")

    exclude = exclude if exclude is not None else DEFAULT_EXCLUDE
    counter = [0]
    root_node, truncated = _build_tree(
        current_path=root,
        node_name=".",
        exclude=exclude,
        max_depth=max_depth,
        current_depth=0,
        max_entries=max_entries,
        counter=counter,
    )
    if truncated:
        root_node["truncated"] = True
    return root_node


# ── Internal: traversal & formatting ──────────────────────────────────

def _build_tree(
    current_path: Path,
    node_name: str,
    exclude: Set[str],
    max_depth: Optional[int],
    current_depth: int,
    max_entries: Optional[int],
    counter: List[int],
) -> Tuple[Dict[str, Any], bool]:
    """
    Traversal rekursif yang membangun satu simpul pohon.

    Returns:
        Tuple (simpul, truncated):
        - simpul: dictionary representasi simpul.
        - truncated: True jika ada pemotongan karena max_entries.
    """
    simpul = {
        "name": node_name,
        "type": "directory",
        "children": [],
    }
    counter[0] += 1
    truncated = False

    # Jika sudah mencapai batas kedalaman, jangan tambah anak
    if max_depth is not None and current_depth >= max_depth:
        return simpul, truncated

    # Hentikan jika sudah mencapai batas entri
    if max_entries is not None and counter[0] >= max_entries:
        return simpul, True

    # Baca isi direktori
    try:
        entries = sorted(
            [p for p in current_path.iterdir() if p.name not in exclude],
            key=lambda p: (p.is_file(), p.name.lower()),  # direktori dahulu
        )
    except PermissionError:
        simpul["children"].append({"name": "[izin ditolak]", "type": "error"})
        return simpul, truncated
    except OSError as e:
        simpul["children"].append({"name": f"[error: {e}]", "type": "error"})
        return simpul, truncated

    for entry in entries:
        # Periksa batas entri sebelum menambahkan setiap item
        if max_entries is not None and counter[0] >= max_entries:
            truncated = True
            break

        if entry.is_symlink():
            # Symlink tidak diikuti, cukup beri penanda
            child = {
                "name": entry.name,
                "type": "directory" if entry.is_dir() else "file",
                "is_symlink": True,
            }
            simpul["children"].append(child)
            counter[0] += 1
        elif entry.is_dir():
            child, child_truncated = _build_tree(
                current_path=entry,
                node_name=entry.name,
                exclude=exclude,
                max_depth=max_depth,
                current_depth=current_depth + 1,
                max_entries=max_entries,
                counter=counter,
            )
            simpul["children"].append(child)
            if child_truncated:
                truncated = True
        else:
            child = {
                "name": entry.name,
                "type": "file",
                "is_symlink": False,
            }
            simpul["children"].append(child)
            counter[0] += 1

    return simpul, truncated


def _format_tree_to_lines(root_node: Dict[str, Any]) -> List[str]:
    """Ubah struktur pohon (dict) ke daftar string pohon gaya terminal."""
    lines = [root_node["name"]]  # root, yaitu "."

    children = root_node.get("children", [])
    for i, child in enumerate(children):
        is_last = (i == len(children) - 1)
        _format_node(child, prefix="", lines=lines, is_last=is_last)
    return lines


def _format_node(
    node: Dict[str, Any],
    prefix: str,
    lines: List[str],
    is_last: bool,
) -> None:
    """Rekursif mencetak satu simpul ke dalam daftar `lines`."""
    connector = "└── " if is_last else "├── "
    name = node["name"]
    if node.get("is_symlink"):
        name += " [symlink]"
    lines.append(f"{prefix}{connector}{name}")

    # Jika direktori biasa (bukan symlink) dan punya children, proses isinya
    if node["type"] == "directory" and "children" in node and not node.get("is_symlink"):
        children = node["children"]
        for i, child in enumerate(children):
            child_is_last = (i == len(children) - 1)
            new_prefix = prefix + ("    " if is_last else "│   ")
            _format_node(child, new_prefix, lines, child_is_last)
