from app.core.logging import get_logger

logger = get_logger(__name__)


class QAAgent:
    def answer(self, question: str):
        logger.info("qa agent called")
        raise NotImplementedError()
