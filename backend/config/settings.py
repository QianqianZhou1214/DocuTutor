from pydantic import BaseSettings
from typing import Dict, Any
import yaml


class Settings(BaseSettings):
    raw_config: Dict[str, Any]
    groq_api_key: str = ""
    openai_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def load(cls, path: str):
        with open(path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        return cls(raw_config=cfg)


config = Settings.load("backend/config/config.yaml")
