from pathlib import Path
from app.config.settings import settings
from app.core.logging import logger
from app.core.utils import ensure_dir

from app.ingestion.pdf_to_md import PdfToMarkdownConverter
from app.ingestion.metadata import MetadataExtractor
from app.ingestion.chunking import AdaptiveMarkdownChunker

from app.storage.embeddings import build_embeddings
from app.storage.chroma_store import ChromaHnswStore

class IngestionPipeline:
    def __init__(self):
        ensure_dir(settings.staged_dir)
        ensure_dir(settings.chroma_dir)

        self.converter = PdfToMarkdownConverter(out_dir=settings.staged_dir / "markdown")
        self.meta_extractor = MetadataExtractor()
        self.chunker = AdaptiveMarkdownChunker()
        self.emb = build_embeddings()
        self.store = ChromaHnswStore()

    def ingest_pdf(self, pdf_path: Path) -> None:
        logger.info("ingest.start", pdf=str(pdf_path))

        md_path = self.converter.convert(pdf_path)
        md_text = md_path.read_text(encoding="utf-8")

        meta = self.meta_extractor.extract(pdf_path, md_text)
        chunks = self.chunker.chunk(md_text, meta=meta)

        vectors = self.emb.embed([c.text for c in chunks])
        self.store.upsert(chunks, vectors)

        logger.info("ingest.done", pdf=str(pdf_path), doc_id=meta.doc_id, n_chunks=len(chunks))
