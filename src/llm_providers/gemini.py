from pydantic import BaseModel
from typing import Type
from src.llm_providers.base import OpenAICompatibleClient


class GeminiClient(OpenAICompatibleClient):
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
    api_key_env = "GEMINI_API_KEY"
    model = "gemini-3.5-flash"

    def complete(self, system: str, user: str, response_model: Type[BaseModel]) -> dict:
        client = self._make_client()
        completion = client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format=response_model,
        )
        return completion.choices[0].message.parsed.model_dump()
