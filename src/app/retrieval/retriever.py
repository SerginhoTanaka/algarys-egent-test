from typing import List, Dict, Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class Retriever:
    def __init__(self, store=None, embeddings=None):
        self.store = store
        self.embeddings = embeddings

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        logger.info("retrieve called")
        raise NotImplementedError()
