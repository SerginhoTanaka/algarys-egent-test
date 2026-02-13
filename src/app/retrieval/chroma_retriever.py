from typing import List, Dict, Any
from src.app.core.logging import get_logger

from src.app.retrieval.retriever import Retriever
from src.app.storage.chroma_store import ChromaHnswStore
from src.app.core.utils import sanitize_filters

logger = get_logger(__name__)


class ChromaRetriever(Retriever):
    """
    Retriever baseado em Chroma + embeddings.
    """
    def __init__(self, store: ChromaHnswStore, embeddings):
        super().__init__(store, embeddings)

    def retrieve(
        self,
        query: str,
        metadata_filters: Dict[str, Any] | None = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:

        logger.info("retriever.start", query=query, top_k=top_k)

        # 1) Embedding da query
        query_vec = self.embeddings.embed([query])[0]

        # 2) Sanitizar filtros para formato aceito pelo Chroma
        where = sanitize_filters(metadata_filters or {})

        # 3) Executar consulta
        raw = self.store.collection.query(
            query_embeddings=[query_vec],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        docs = raw.get("documents", [[]])[0]
        metas = raw.get("metadatas", [[]])[0]
        dists = raw.get("distances", [[]])[0]

        results = []
        for text, meta, dist in zip(docs, metas, dists):
            results.append({
                "text": text,
                "metadata": meta,
                "distance": dist,
            })

        logger.info("retriever.done", n_results=len(results))
        return results
