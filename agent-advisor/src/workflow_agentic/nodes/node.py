import json
import logging

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.infrastructure.provider_factory.connection_models_factory import ConnectionModelFactory
from src.utils.prompts import PLANNER_PROMPT, SYNTHESIZER_PROMPT
from src.workflow_agentic.agents.agents import Agents
from src.workflow_agentic.state import AdvisorState

logger = logging.getLogger(__name__)


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


def orchestrator_node(state: AdvisorState) -> dict:
    logger.info(
        "[Orchestrator] Mensagem recebida do cliente %s: '%s'",
        state["client_id"],
        state["message_input"],
    )

    agents = Agents()

    messages = state.get("messages", [])
    logger.info("[Orchestrator] Histórico da sessão: %d mensagem(ns)", len(messages))

    chat_history = ""
    for msg in messages:
        role = "Cliente" if isinstance(msg, HumanMessage) else "Assistente"
        raw = msg.content
        if isinstance(raw, str):
            content = raw
        elif isinstance(raw, dict) and "text" in raw:
            content = raw["text"]
        elif isinstance(raw, list):
            parts = []
            for part in raw:
                if isinstance(part, dict) and "text" in part:
                    parts.append(part["text"])
                elif isinstance(part, str):
                    parts.append(part)
            content = " ".join(parts)
        else:
            content = str(raw)
        chat_history += f"{role}: {content}\n"

    if chat_history:
        logger.info("[Orchestrator] Chat history recuperado:\n%s", chat_history[:500])

    logger.info("[Orchestrator] Analisando intenção e contexto da solicitação...")

    result = agents.agent_orquestrador(
        message_input=state["message_input"],
        client_id=state["client_id"],
        session_id=state["session_id"],
        chat_history=chat_history,
    )

    logger.info("[Orchestrator] Intenção classificada com sucesso.")

    return {
        "intent": result,
        "context_summary": result,
        "messages": [HumanMessage(content=state["message_input"])],
    }


def planner_node(state: AdvisorState) -> dict:
    logger.info("[Planner] Iniciando decomposição de tarefas...")

    llm = ConnectionModelFactory.create_connection_model().connection()

    prompt = PLANNER_PROMPT.format(orchestrator_analysis=state["intent"])
    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=state["message_input"]),
    ])

    try:
        content = _extract_content(response)
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        execution_plan = json.loads(content)
    except (json.JSONDecodeError, IndexError, AttributeError):
        logger.warning("[Planner] Falha ao parsear plano do LLM. Usando plano fallback.")
        execution_plan = [
            {"agent": "agente_apoio", "task": state["message_input"], "priority": "alta", "deps": []},
            {"agent": "agente_consulta", "task": state["message_input"], "priority": "alta", "deps": ["agente_apoio"]},
        ]

    agentes_selecionados = [t["agent"] for t in execution_plan]
    logger.info(
        "[Planner] Plano criado com %d tarefa(s). Agentes selecionados: %s",
        len(execution_plan),
        agentes_selecionados,
    )
    for i, task in enumerate(execution_plan, 1):
        logger.info(
            "[Planner]   Tarefa %d: agente=%s | prioridade=%s | deps=%s | desc='%s'",
            i,
            task["agent"],
            task.get("priority", "N/A"),
            task.get("deps", []),
            task["task"][:80],
        )

    return {"execution_plan": execution_plan}


def _build_chat_history(state: AdvisorState) -> str:
    chat_history = ""
    for msg in state.get("messages", []):
        role = "Cliente" if isinstance(msg, HumanMessage) else "Assistente"
        raw = msg.content
        if isinstance(raw, str):
            content = raw
        elif isinstance(raw, dict) and "text" in raw:
            content = raw["text"]
        elif isinstance(raw, list):
            parts = []
            for part in raw:
                if isinstance(part, dict) and "text" in part:
                    parts.append(part["text"])
                elif isinstance(part, str):
                    parts.append(part)
            content = " ".join(parts)
        else:
            content = str(raw)
        chat_history += f"{role}: {content}\n"
    return chat_history


def executor_node(state: AdvisorState) -> dict:
    logger.info("[Executor] Iniciando execução do plano com %d tarefa(s).", len(state.get("execution_plan", [])))

    agents = Agents()
    plan = state.get("execution_plan", [])
    agent_results: dict[str, str] = {}
    chat_history = _build_chat_history(state)

    executed: set[str] = set()
    remaining = list(plan)
    max_iterations = len(remaining) * 2 + 1

    for _ in range(max_iterations):
        if not remaining:
            break

        progressed = False
        for task in list(remaining):
            deps = task.get("deps", [])
            if not all(dep in executed for dep in deps):
                continue

            agent_name = task["agent"]
            task_desc = task["task"]

            logger.info("[Executor] Executando agente '%s'...", agent_name)

            try:
                if agent_name == "agente_consulta":
                    result = agents.agent_consulta(
                        client_id=state["client_id"],
                        task_description=task_desc,
                        chat_history=chat_history,
                    )
                elif agent_name == "agente_analise":
                    dados = agent_results.get("agente_consulta", "No data available")
                    result = agents.agent_analise(
                        client_id=state["client_id"],
                        task_description=task_desc,
                        dados_financeiros=dados,
                        chat_history=chat_history,
                    )
                elif agent_name == "agente_apoio":
                    result = agents.agent_apoio(
                        task_description=task_desc,
                        chat_history=chat_history,
                    )
                else:
                    result = f"Unknown agent: {agent_name}"
            except Exception as e:
                logger.error("[Executor] Agente '%s' falhou: %s", agent_name, e)
                result = f"Error executing {agent_name}: {e}"

            logger.info("[Executor] Agente '%s' concluído com sucesso.", agent_name)
            agent_results[agent_name] = result
            executed.add(agent_name)
            remaining.remove(task)
            progressed = True

        if not progressed:
            logger.warning("[Executor] Nenhum progresso na iteração. Dependências não resolvidas: %s",
                           [t["agent"] for t in remaining])
            break

    logger.info("[Executor] Execução finalizada. Agentes executados: %s", list(executed))

    return {"agent_results": agent_results}


def synthesizer_node(state: AdvisorState) -> dict:
    logger.info("[Synthesizer] Consolidando resultados de %d agente(s)...", len(state.get("agent_results", {})))

    llm = ConnectionModelFactory.create_connection_model().connection()
    agent_results = state.get("agent_results", {})

    prompt = SYNTHESIZER_PROMPT.format(
        message_input=state["message_input"],
        agent_results=json.dumps(agent_results, ensure_ascii=False, indent=2),
    )
    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=state["message_input"]),
    ])

    final_text = _extract_content(response)
    logger.info("[Synthesizer] Resposta final gerada para o cliente %s.", state["client_id"])

    return {
        "final_response": final_text,
        "messages": [AIMessage(content=final_text)],
    }
