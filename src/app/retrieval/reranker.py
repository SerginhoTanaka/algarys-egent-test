from typing import List, Dict, Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class Reranker:
    def rank(self, query: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info("rerank called with %d candidates", len(candidates))
        return candidates
