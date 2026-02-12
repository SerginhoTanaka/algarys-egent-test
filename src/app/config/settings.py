from pydantic import BaseModel
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
class Settings(BaseModel):
    project_name: str = "financial-docs-rag"
    data_dir: Path = Path(os.getenv("DATA_DIR", "data"))
    raw_dir: Path = data_dir / "raw"
    staged_dir: Path = data_dir / "staged"
    chroma_dir: Path = data_dir / "chroma"

    # embeddings
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "openai") 
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    local_embedding_model: str = os.getenv("LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # chroma/hnsw
    chroma_collection: str = os.getenv("CHROMA_COLLECTION", "documents")

    hnsw_space: str = os.getenv("HNSW_SPACE", "cosine")
    hnsw_ef_construction: int = int(os.getenv("HNSW_EF_CONSTRUCTION", "100"))
    hnsw_ef_search: int = int(os.getenv("HNSW_EF_SEARCH", "64"))
    hnsw_max_neighbors: int = int(os.getenv("HNSW_MAX_NEIGHBORS", "16"))
    hnsw_num_threads: int = int(os.getenv("HNSW_NUM_THREADS", "4"))

settings = Settings()
