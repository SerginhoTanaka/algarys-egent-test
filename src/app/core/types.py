from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict

class DocumentMeta(BaseModel):
    doc_id: str
    source_path: str
    company: Optional[str] = None
    doc_type: Optional[str] = None
    doc_date: Optional[str] = None  # ISO string quando possível
    extra: Dict[str, str] = Field(default_factory=dict)

class Chunk(BaseModel):
    chunk_id: str
    doc_id: str
    text: str
    chunk_kind: Literal["text", "table"] = "text"
    section_path: List[str] = Field(default_factory=list)
    order: int = 0
    metadata: Dict[str, str] = Field(default_factory=dict)
