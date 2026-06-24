from pydantic import BaseModel

class ConversationModelResponse(BaseModel):
    message_output: str
    client_id: str
    session_id: str
    interaction_id: str