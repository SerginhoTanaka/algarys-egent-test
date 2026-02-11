from app.core.logging import get_logger

logger = get_logger(__name__)


class RiskAgent:
    def assess(self, doc):
        logger.info("risk assessment called")
        raise NotImplementedError()
