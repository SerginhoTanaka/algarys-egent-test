from app.core.logging import get_logger

logger = get_logger(__name__)


class ExtractorAgent:
    def extract(self, chunks):
        logger.info("extractor called")
        raise NotImplementedError()
