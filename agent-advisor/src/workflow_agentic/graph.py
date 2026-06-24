import logging

from langgraph.graph import END, START, StateGraph

from src.workflow_agentic.nodes.node import (
    executor_node,
    orchestrator_node,
    planner_node,
    synthesizer_node,
)
from src.workflow_agentic.state import AdvisorState

logger = logging.getLogger(__name__)


def build_advisor_graph() -> StateGraph:
    logger.info("[Graph] Construindo grafo de assessoria...")

    graph = StateGraph(AdvisorState)

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("synthesizer", synthesizer_node)

    graph.add_edge(START, "orchestrator")
    graph.add_edge("orchestrator", "planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "synthesizer")
    graph.add_edge("synthesizer", END)

    logger.info("[Graph] Grafo construído: START -> orchestrator -> planner -> executor -> synthesizer -> END")

    return graph


def get_compiled_graph(checkpointer=None):
    graph = build_advisor_graph()
    compiled = graph.compile(checkpointer=checkpointer)

    if checkpointer:
        logger.info("[Graph] Grafo compilado com checkpointer: %s", type(checkpointer).__name__)
    else:
        logger.info("[Graph] Grafo compilado sem checkpointer (sem persistência de estado).")

    return compiled
