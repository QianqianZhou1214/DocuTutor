from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from backend.config.settings import config


class EmbeddingFactory:

    @staticmethod
    def create() -> any:
        provider = config.raw_config["embedding"]["provider"]

        if provider == "huggingface":
            model_name = config.raw_config["embedding"]["huggingface"]["model_name"]
            return HuggingFaceEmbeddings(model_name=model_name)
        elif provider == "openai":
            model = config.raw_config["embedding"]["openai"]["model"]
            return OpenAIEmbeddings(model=model)
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")
