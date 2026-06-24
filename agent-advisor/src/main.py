import logging

from fastapi import FastAPI

from src.adapters.routes.conversation_route import router
from src.infrastructure.langfuse.callback import verify_langfuse_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(router, prefix="/ms_agent_server", tags=["conversation analysis"])


@app.on_event("startup")
async def startup_event():
    logger.info("[App] Iniciando Agent Account Advisor...")
    if verify_langfuse_connection():
        logger.info("[App] Langfuse conectado - tracing habilitado.")
    else:
        logger.warning("[App] Langfuse indisponível - tracing desabilitado.")
    logger.info("[App] Aplicação pronta para receber requisições.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
