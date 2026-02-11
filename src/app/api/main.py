try:
    from fastapi import FastAPI
except Exception:  # pragma: no cover - FastAPI optional
    FastAPI = None

from app.core.logging import get_logger

logger = get_logger(__name__)


def create_app():
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed")
    app = FastAPI(title="Document Ingestion API")
    return app


app = None
try:
    app = create_app()
except Exception:
    logger.debug("API app not created (FastAPI missing)")
