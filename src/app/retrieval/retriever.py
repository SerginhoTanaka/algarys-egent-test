from typing import List, Dict, Any
from src.app.core.logging import get_logger

logger = get_logger(__name__)


class Retriever:
    """
    Classe base responsável por definir a interface de retrieval.
    Implementações concretas (ex: ChromaRetriever) devem sobrescrever retrieve().
    """

    def __init__(self, store=None, embeddings=None):
        self.store = store
        self.embeddings = embeddings

    def retrieve(
        self,
        query: str,
        metadata_filters: Dict[str, Any] | None = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        logger.info("retriever.base_called")
        raise NotImplementedError("Implement retrieve() in subclasses.")
