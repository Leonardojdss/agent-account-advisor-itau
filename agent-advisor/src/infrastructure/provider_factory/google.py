from langchain_google_genai import ChatGoogleGenerativeAI

from src.config.settings import settings
from src.infrastructure.provider_factory.connection_models import ConnectionModelNaturalLanguage


class ConnectGoogleGenAI(ConnectionModelNaturalLanguage):

    def __init__(self, model: str = "gemini-3.1-flash-lite"):
        self.model = model

    def connection(self):
        llm = ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        return llm
