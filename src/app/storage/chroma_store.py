from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config.settings import settings

class ChromaHnswStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=str(settings.chroma_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        collection_config = {
            "hnsw": {
                "space": settings.hnsw_space,                     
                "ef_construction": int(settings.hnsw_ef_construction),
                "ef_search": int(settings.hnsw_ef_search),
                "max_neighbors": int(settings.hnsw_max_neighbors),
                "num_threads": int(settings.hnsw_num_threads),
            }
        }

        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection,
            configuration=collection_config,
        )

    def upsert(self, chunks, embeddings) -> None:
        ids = [c.chunk_id for c in chunks]
        docs = [c.text for c in chunks]

        metas: List[Dict[str, Any]] = []
        for c in chunks:
            metas.append({
                "doc_id": c.doc_id,
                "chunk_kind": c.chunk_kind,
                "order": c.order,
                "section_path": " > ".join(c.section_path),
                **c.metadata,
            })

        self.collection.upsert(
            ids=ids,
            documents=docs,
            metadatas=metas,
            embeddings=embeddings,
        )
