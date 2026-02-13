import logging
import structlog

def setup_logging() -> None:
    """
    Configuração profissional de logging:
    - JSON estruturado (para Cloud Logging, ELK, Datadog)
    - Níveis corretos
    - Timestamp ISO
    - Integração perfeita com structlog
    """

    # Configuração base do logging do Python (fallback)
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )

    # Configuração do structlog
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()

def get_logger(name: str = None):
    """
    Retorna um logger structlog.
    Se name for fornecido, adiciona como contexto.
    """
    return structlog.get_logger(name)
