from src.config.settings import settings
from src.infrastructure.provider_factory.connection_models import ConnectionModelNaturalLanguage
from src.infrastructure.provider_factory.openai import ConnectOpenAI
from src.infrastructure.provider_factory.ollama import ConnectOllama
from src.infrastructure.provider_factory.aws_bedrock import ConnectAWSBedrock
from src.infrastructure.provider_factory.google import ConnectGoogleGenAI


class ConnectionModelFactory:
    _registry: dict[str, type[ConnectionModelNaturalLanguage]] = {
        "openai": ConnectOpenAI,
        "ollama": ConnectOllama,
        "aws_bedrock": ConnectAWSBedrock,
        "google_gemini": ConnectGoogleGenAI
    }

    @staticmethod
    def create_connection_model(provider: str | None = None, **kwargs) -> ConnectionModelNaturalLanguage:
        if provider is None:
            provider = settings.PROVIDER_LLM
        cls = ConnectionModelFactory._registry.get(provider)
        if cls is None:
            raise ValueError(f"type of provider '{provider}' not supported")
        return cls(**kwargs)