from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AdvisorState(TypedDict):
    message_input: str
    client_id: str
    session_id: str
    interaction_id: str

    messages: Annotated[list[BaseMessage], add_messages]

    intent: str
    context_summary: str

    execution_plan: list[dict]

    agent_results: dict[str, str]

    final_response: str
