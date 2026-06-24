from langchain_aws import BedrockLLM
from src.infrastructure.provider_factory.connection_models import ConnectionModelNaturalLanguage


class ConnectAWSBedrock(ConnectionModelNaturalLanguage):

    def __init__(self, model: str = "anthropic.claude-haiku-4-5-20251001-v1:0", region: str = "us-east-1"):
        self.model = model
        self.region = region

    def connection(self):
        llm = BedrockLLM(
            model_id=self.model,
            region_name=self.region
        )
        return llm
