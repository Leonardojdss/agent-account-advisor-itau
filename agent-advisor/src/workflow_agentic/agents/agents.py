import logging
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from src.infrastructure.provider_factory.connection_models_factory import ConnectionModelFactory
from src.utils.prompts import (
    AGENTE_ANALISE_PROMPT,
    AGENTE_APOIO_PROMPT,
    AGENTE_CONSULTA_PROMPT,
    ORCHESTRATOR_PROMPT,
)
from src.workflow_agentic.tools.tool_database import search_database_schema, select_database

logger = logging.getLogger(__name__)

TOOLS_CONSULTA = [search_database_schema, select_database]
TOOL_MAP = {t.name: t for t in TOOLS_CONSULTA}


def _extract_content(response) -> str:
    content = response.content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                parts.append(part["text"])
            elif isinstance(part, str):
                parts.append(part)
            else:
                parts.append(str(part))
        return " ".join(parts).strip()
    if isinstance(content, dict) and "text" in content:
        return content["text"].strip()
    return str(content).strip() if content else ""


class Agents:

    def __init__(self):
        logger.info("[Agents] Inicializando agentes com provider LLM...")
        self._llm = ConnectionModelFactory.create_connection_model().connection()
        logger.info("[Agents] LLM conectado: %s", type(self._llm).__name__)

    def agent_orquestrador(
        self,
        message_input: str,
        client_id: str,
        session_id: str,
        chat_history: str,
    ) -> str:
        logger.info("[Agent:Orquestrador] Invocando LLM para classificação de intenção...")
        prompt = ORCHESTRATOR_PROMPT.format(
            client_id=client_id,
            session_id=session_id,
            chat_history=chat_history,
            message_input=message_input,
        )
        response = self._llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=message_input),
        ])
        logger.info("[Agent:Orquestrador] Resposta recebida do LLM.")
        return _extract_content(response)

    def agent_consulta(self, client_id: str, task_description: str, chat_history: str = "") -> str:
        logger.info("[Agent:Consulta] Iniciando consulta bancária para client_id=%s", client_id)
        data_atual = datetime.now().strftime("%d/%m/%Y")
        prompt = AGENTE_CONSULTA_PROMPT.format(
            client_id=client_id,
            data_atual=data_atual,
            task_description=task_description,
        )

        if chat_history:
            prompt += f"\n\n## Histórico da Conversa\n\n{chat_history}"

        llm_with_tools = self._llm.bind_tools(TOOLS_CONSULTA)
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=task_description),
        ]

        for iteration in range(5):
            logger.info("[Agent:Consulta] Iteração %d - invocando LLM...", iteration + 1)
            response = llm_with_tools.invoke(messages)
            messages.append(response)

            if not response.tool_calls:
                logger.info("[Agent:Consulta] Nenhuma tool call. Finalizando.")
                break

            for tool_call in response.tool_calls:
                logger.info(
                    "[Agent:Consulta] Tool call: %s(%s)",
                    tool_call["name"],
                    str(tool_call["args"])[:100],
                )
                tool_fn = TOOL_MAP.get(tool_call["name"])
                if tool_fn is None:
                    result = f"Unknown tool: {tool_call['name']}"
                    logger.warning("[Agent:Consulta] Tool desconhecida: %s", tool_call["name"])
                else:
                    result = tool_fn.invoke(tool_call["args"])
                    logger.info("[Agent:Consulta] Tool '%s' retornou %d caracteres.", tool_call["name"], len(str(result)))
                messages.append(
                    ToolMessage(content=str(result), tool_call_id=tool_call["id"])
                )

        logger.info("[Agent:Consulta] Consulta finalizada.")
        return _extract_content(response)

    def agent_analise(
        self, client_id: str, task_description: str, dados_financeiros: str, chat_history: str = ""
    ) -> str:
        logger.info("[Agent:Analise] Iniciando análise financeira para client_id=%s", client_id)
        data_atual = datetime.now().strftime("%d/%m/%Y")
        prompt = AGENTE_ANALISE_PROMPT.format(
            client_id=client_id,
            data_atual=data_atual,
            dados_financeiros=dados_financeiros,
            task_description=task_description,
        )

        if chat_history:
            prompt += f"\n\n## Histórico da Conversa\n\n{chat_history}"

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=task_description),
        ]
        response = self._llm.invoke(messages)
        logger.info("[Agent:Analise] Análise concluída.")
        return _extract_content(response)

    def agent_apoio(self, task_description: str, chat_history: str = "") -> str:
        logger.info("[Agent:Apoio] Resolvendo informações contextuais/temporais...")
        now = datetime.now()
        dias_semana = {
            "Monday": "Segunda-feira",
            "Tuesday": "Terça-feira",
            "Wednesday": "Quarta-feira",
            "Thursday": "Quinta-feira",
            "Friday": "Sexta-feira",
            "Saturday": "Sábado",
            "Sunday": "Domingo",
        }
        prompt = AGENTE_APOIO_PROMPT.format(
            data_atual=now.strftime("%d/%m/%Y"),
            dia_semana=dias_semana.get(now.strftime("%A"), now.strftime("%A")),
            mes_atual=now.strftime("%m"),
            ano_atual=now.strftime("%Y"),
            task_description=task_description,
        )

        if chat_history:
            prompt += f"\n\n## Histórico da Conversa\n\n{chat_history}"

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=task_description),
        ]
        response = self._llm.invoke(messages)
        logger.info("[Agent:Apoio] Informações contextuais geradas.")
        return _extract_content(response)
