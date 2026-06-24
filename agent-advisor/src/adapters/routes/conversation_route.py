import logging

from fastapi import APIRouter, HTTPException, status
from langfuse import propagate_attributes

from src.adapters.schemas.conversation_model_request import ConversationModelRequest
from src.adapters.schemas.conversation_model_response import ConversationModelResponse
from src.infrastructure.langfuse.callback import get_langfuse_client, get_langfuse_handler
from src.infrastructure.redis.checkpointer import get_checkpointer
from src.workflow_agentic.graph import get_compiled_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

_checkpointer = get_checkpointer()
_compiled_graph = get_compiled_graph(checkpointer=_checkpointer)


@router.post("/V1/agent_conversation/", response_model=ConversationModelResponse)
async def agent_conversation_endpoint(
    conversation_input: ConversationModelRequest,
) -> ConversationModelResponse:
    try:
        logger.info(
            "[Route] Requisição recebida - client_id=%s | session_id=%s | interaction_id=%s",
            conversation_input.client_id,
            conversation_input.session_id,
            conversation_input.interaction_id,
        )
        logger.info("[Route] Mensagem do cliente: '%s'", conversation_input.message_input)

        config = {"configurable": {"thread_id": conversation_input.session_id}}

        existing_state = _compiled_graph.get_state(config)
        if existing_state and existing_state.values.get("messages"):
            history_count = len(existing_state.values["messages"])
            logger.info("[Route] Histórico recuperado: %d mensagem(ns) na sessão %s",
                        history_count, conversation_input.session_id)
        else:
            logger.info("[Route] Nova sessão: %s (sem histórico)", conversation_input.session_id)

        initial_state = {
            "message_input": conversation_input.message_input,
            "client_id": conversation_input.client_id,
            "session_id": conversation_input.session_id,
            "interaction_id": conversation_input.interaction_id,
        }

        handler = get_langfuse_handler()
        langfuse = get_langfuse_client()

        if handler:
            config["callbacks"] = [handler]

        logger.info("[Route] Invocando grafo com thread_id=%s...", conversation_input.session_id)

        if langfuse:
            with langfuse.start_as_current_observation(
                as_type="span",
                name="agent-advisor-conversation",
            ):
                with propagate_attributes(
                    session_id=conversation_input.session_id,
                    user_id=conversation_input.client_id,
                ):
                    result = _compiled_graph.invoke(initial_state, config=config)
        else:
            result = _compiled_graph.invoke(initial_state, config=config)

        logger.info(
            "[Route] Grafo finalizado com sucesso - client_id=%s | session_id=%s",
            conversation_input.client_id,
            conversation_input.session_id,
        )
        logger.info("[Route] Resposta gerada: '%s'", result["final_response"][:100])

        return ConversationModelResponse(
            message_output=result["final_response"],
            client_id=conversation_input.client_id,
            session_id=conversation_input.session_id,
            interaction_id=conversation_input.interaction_id,
        )

    except Exception as e:
        logger.error(
            "[Route] Erro ao processar requisição - client_id=%s | erro=%s",
            conversation_input.client_id,
            e,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {e}",
        )
