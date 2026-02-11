from app.core.logging import get_logger

logger = get_logger(__name__)


class Orchestrator:
    def __init__(self, retriever=None, agents=None):
        self.retriever = retriever
        self.agents = agents or []

    def run(self, query: str):
        logger.info("orchestrator received query")
        raise NotImplementedError()
