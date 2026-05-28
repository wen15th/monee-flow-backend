import os
from openai import OpenAI
from pydantic import BaseModel
from typing import Type


class OpenAICompatibleClient:
    base_url: str
    api_key_env: str
    model: str

    def _make_client(self) -> OpenAI:
        return OpenAI(
            base_url=self.base_url,
            api_key=os.getenv(self.api_key_env, ""),
        )

    def complete(self, system: str, user: str, response_model: Type[BaseModel]) -> dict:
        raise NotImplementedError