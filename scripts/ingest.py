from pathlib import Path
import sys
from pathlib import Path as _Path

REPO_ROOT = _Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from app.core.logging import setup_logging, logger
from app.config.settings import settings
from app.ingestion.pipeline import IngestionPipeline

def main():
    setup_logging()
    pipeline = IngestionPipeline()

    settings.raw_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(settings.raw_dir.glob("*.pdf"))
    if not pdfs:
        logger.info("ingest.no_pdfs", raw_dir=str(settings.raw_dir))
        return

    for pdf in pdfs:
        pipeline.ingest_pdf(pdf)

if __name__ == "__main__":
    main()
