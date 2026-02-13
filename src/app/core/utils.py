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
    Chroma (v0.5+) só permite um filtro por operação.
    Prioridade:
      1. Se existir 'company', use somente ela.
      2. Se não existir 'company', use o primeiro filtro válido.
      3. Se nada existir, return {}.
    """

    # Remover valores inválidos
    cleaned = {k: v for k, v in filters.items() if v not in (None, "", [], {})}

    # Caso 1: company tem prioridade
    if "company" in cleaned:
        return {"company": {"$eq": cleaned["company"]}}

    # Caso 3: sem filtros
    return {}


def get_unique_companies(store):
    """
    Percorre toda a coleção e retorna uma lista de companies únicos.
    """
    results = store.collection.get(include=["metadatas"])
    companies = set()

    for meta in results["metadatas"]:
        if "company" in meta and meta["company"]:
            companies.add(meta["company"])

    return sorted(list(companies))

def get_metadata_fields(store):
    """
    Coleta todas as chaves de metadados encontrados na coleção.
    """
    results = store.collection.get(include=["metadatas"])
    keys = set()

    for meta in results["metadatas"]:
        keys |= set(meta.keys())

    return sorted(list(keys))

