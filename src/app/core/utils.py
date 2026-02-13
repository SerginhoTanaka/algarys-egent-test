import hashlib
from pathlib import Path
from typing import Dict, Any

def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

def stable_doc_id(path: Path) -> str:
    # doc_id estável baseado no caminho + tamanho + mtime (barato e suficiente)
    stat = path.stat()
    payload = f"{path.name}|{stat.st_size}|{int(stat.st_mtime)}"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def sanitize_filters(filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforma filtros em formato aceito pelo Chroma.
    
    Input:
        {"company": "Apple", "doc_type": None}

    Output:
        {"company": {"$eq": "Apple"}}

    Campos None, "" ou [] são removidos.
    """
    out = {}

    for key, value in filters.items():
        if value is None or value == "" or value == []:
            continue

        # Chroma exige {"field": {"$eq": value}}
        out[key] = {"$eq": value}

    return out