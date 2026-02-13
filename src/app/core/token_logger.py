import time
import uuid
import structlog
import tiktoken

logger = structlog.get_logger()

class TokenEstimator:
    """
    Estimador de tokens baseado em TikToken.
    Usa prompt_tokens estimados antes da chamada real ao LLM.
    completion_tokens é sempre 0 (estimado).
    """

    def __init__(self, agent_name: str, model_name: str = "gpt-4o-mini"):
        self.agent_name = agent_name
        self.trace_id = str(uuid.uuid4())
        self.encoding = tiktoken.encoding_for_model(model_name)

    def count_tokens(self, messages) -> int:
        """
        Conta tokens do prompt inteiro baseado no formato ChatML.
        """
        total_tokens = 0
        for msg in messages:
            total_tokens += len(self.encoding.encode(msg["content"]))
            # role também conta tokens
            total_tokens += len(self.encoding.encode(msg["role"]))
        return total_tokens

    def log_estimated(self, messages):
        """
        Calcula tokens estimados e loga antes da chamada real ao modelo.
        """
        prompt_tokens = self.count_tokens(messages)

        logger.info(
            "agent_llm_call_estimated",
            trace_id=self.trace_id,
            agent=self.agent_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=0,
            total_tokens=prompt_tokens,
        )

        return prompt_tokens

    def log_text_estimated(self, text: str):
        """
        Estima tokens de um texto simples (compatível com agent calls).
        """
        prompt_tokens = len(self.encoding.encode(text))

        logger.info(
            "agent_llm_call_estimated",
            trace_id=self.trace_id,
            agent=self.agent_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=0,
            total_tokens=prompt_tokens,
        )

        return prompt_tokens
