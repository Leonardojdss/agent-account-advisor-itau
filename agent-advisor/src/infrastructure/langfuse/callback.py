import logging
import os

from langfuse import get_client, propagate_attributes
from langfuse.langchain import CallbackHandler

from src.config.settings import settings

logger = logging.getLogger(__name__)


def _ensure_langfuse_env():
    os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
    os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
    os.environ["LANGFUSE_HOST"] = settings.LANGFUSE_HOST


def get_langfuse_handler() -> CallbackHandler | None:
    if not settings.LANGFUSE_PUBLIC_KEY or not settings.LANGFUSE_SECRET_KEY:
        return None

    _ensure_langfuse_env()

    try:
        handler = CallbackHandler()
        return handler
    except Exception as e:
        logger.warning("[Langfuse] Erro ao criar handler: %s", e)
        return None


def get_langfuse_client():
    if not settings.LANGFUSE_PUBLIC_KEY or not settings.LANGFUSE_SECRET_KEY:
        return None

    _ensure_langfuse_env()

    try:
        return get_client()
    except Exception as e:
        logger.warning("[Langfuse] Erro ao obter client: %s", e)
        return None


def verify_langfuse_connection() -> bool:
    if not settings.LANGFUSE_PUBLIC_KEY or not settings.LANGFUSE_SECRET_KEY:
        logger.warning("[Langfuse] Credenciais não configuradas (LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY).")
        return False

    _ensure_langfuse_env()

    try:
        langfuse = get_client()
        if langfuse.auth_check():
            logger.info("[Langfuse] Conexão verificada com sucesso em %s", settings.LANGFUSE_HOST)
            return True
        else:
            logger.warning("[Langfuse] Falha na autenticação. Verifique credenciais e host: %s", settings.LANGFUSE_HOST)
            return False
    except Exception as e:
        logger.warning("[Langfuse] Erro ao verificar conexão com %s: %s", settings.LANGFUSE_HOST, e)
        return False
