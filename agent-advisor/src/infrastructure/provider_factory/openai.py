from langchain_openai import ChatOpenAI
from src.infrastructure.provider_factory.connection_models import ConnectionModelNaturalLanguage

class ConnectOpenAI(ConnectionModelNaturalLanguage):
    
    def __init__(self, model: str = "gpt-4.1-mini"):
        self.model = model

    def connection(self):
        llm = ChatOpenAI(
            model_name=self.model
        )
        return llm