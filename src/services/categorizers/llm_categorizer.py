import os
import json
import logging
from huggingface_hub import (
    InferenceClient,
    ChatCompletionInputResponseFormatJSONSchema,
)
from src.schemas.transaction import TransactionCategoryList
from typing import List


class HFTransactionCategorizer:
    def __init__(
        self,
        model_name: str = "meta-llama/Llama-3.3-70B-Instruct",
        providers: List[str] = None,
    ):
        self.providers = providers or ["fireworks-ai", "groq"]
        self.model_name = model_name

        self.response_format = ChatCompletionInputResponseFormatJSONSchema(
            type="json_schema",
            json_schema={
                "name": "TransactionCategoryList",
                "schema": TransactionCategoryList.model_json_schema(),
                "strict": True,
            },
        )

        # Initialize system prompt
        self.system_prompt = ""
        prompt_path = os.path.join(os.path.dirname(__file__), "prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    def _create_client(self, provider: str) -> InferenceClient:
        return InferenceClient(
            api_key=os.getenv("HF_TOKEN", ""),
            provider=provider,
        )

    def categorize(self, transaction_descriptions: List[str]) -> List[dict]:
        logging.info(
            f"[HF API Call] Request transaction_descriptions: {transaction_descriptions}"
        )

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": "\n".join(transaction_descriptions)},
        ]

        last_error = None
        for i, provider in enumerate(self.providers):
            logging.info(f"[HF API Call] Attempt {i + 1}, using provider: {provider}")
            client = self._create_client(provider)
            try:
                response = client.chat_completion(
                    messages=messages,
                    response_format=self.response_format,
                    model=self.model_name,
                )
                structured_data = response.choices[0].message.content
                logging.info(f"[HF API Call] Response structured_data: {structured_data}")
                return json.loads(structured_data)["trans_category_list"]
            except Exception as e:
                logging.warning(f"[HF API Call] Provider {provider} failed: {e}, trying next...")
                last_error = e

        raise RuntimeError(
            f"All providers failed. Last error: {last_error}"
        )
