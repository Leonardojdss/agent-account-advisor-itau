from src.infrastructure.provider_factory.connection_models import ConnectionModelNaturalLanguage
from langchain_ollama import ChatOllama

class ConnectOllama(ConnectionModelNaturalLanguage):
    
    def __init__(self, model: str = "qwen2.5:0.5b"):
        self.model = model
    
    def connection(self):
        llm = ChatOllama(
            model=self.model
            )
        return llm