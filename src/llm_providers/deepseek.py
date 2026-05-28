import json
from pydantic import BaseModel
from typing import Type
from src.llm_providers.base import OpenAICompatibleClient


class DeepSeekClient(OpenAICompatibleClient):
    base_url = "https://api.deepseek.com"
    api_key_env = "DEEPSEEK_API_KEY"
    model = "deepseek-v4-flash"

    def complete(self, system: str, user: str, response_model: Type[BaseModel]) -> dict:
        client = self._make_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)