import logging

from langgraph.checkpoint.memory import MemorySaver

from src.config.settings import settings

logger = logging.getLogger(__name__)


def get_checkpointer():
    try:
        from langgraph.checkpoint.redis import RedisSaver
    except ImportError:
        logger.warning(
            "[Checkpointer] Pacote 'langgraph-checkpoint-redis' não instalado. "
            "Usando MemorySaver (in-memory). Instale com: pip install langgraph-checkpoint-redis"
        )
        return MemorySaver()

    try:
        saver = RedisSaver(redis_url=settings.REDIS_URL)
        saver.setup()
        logger.info("[Checkpointer] Conectado ao Redis com sucesso: %s", settings.REDIS_URL)
        return saver
    except Exception as e:
        logger.warning(
            "[Checkpointer] Falha ao conectar no Redis (%s). Usando MemorySaver (in-memory) como fallback.",
            e,
        )
        return MemorySaver()
