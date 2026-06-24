from pydantic import BaseModel

class ConversationModelRequest(BaseModel):
    message_input: str
    client_id: str
    session_id: str
    interaction_id: str