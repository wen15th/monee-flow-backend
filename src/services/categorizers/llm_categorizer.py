import os
import json
import logging
import random
from huggingface_hub import (
    InferenceClient,
    ChatCompletionInputResponseFormatJSONSchema,
)
from huggingface_hub.utils import HfHubHTTPError
from src.schemas.transaction import TransactionCategoryList
from typing import List


class HFTransactionCategorizer:
    def __init__(
        self,
        model_name: str = "meta-llama/Llama-3.3-70B-Instruct",
        providers: List[str] = None,
    ):
        self.providers = providers or ["cerebras"]
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

        # Build system/user messages
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": "\n".join(transaction_descriptions)},
        ]

        max_attempts = 3
        tried_providers = []

        for attempt in range(max_attempts):
            available_providers = [
                p for p in self.providers if p not in tried_providers
            ]
            if not available_providers:
                logging.warning(
                    "All providers exhausted, retrying previously tried providers"
                )
                available_providers = self.providers.copy()

            provider = random.choice(available_providers)
            tried_providers.append(provider)
            logging.info(
                f"[HF API Call] Attempt {attempt + 1}, using provider: {provider}"
            )

            client = self._create_client(provider)

            try:
                response = client.chat_completion(
                    messages=messages,
                    response_format=self.response_format,
                    model=self.model_name,
                )

                structured_data = response.choices[0].message.content
                logging.info(
                    f"[HF API Call] Response structured_data: {structured_data}"
                )
                trans_category_list = json.loads(structured_data)["trans_category_list"]

                return trans_category_list

            except HfHubHTTPError as e:
                if 500 <= e.status_code < 600:
                    logging.warning(
                        f"Provider {provider} failed with {e.status_code}, retrying..."
                    )
                    continue
                else:
                    logging.error(
                        f"Provider {provider} failed with {e.status_code}: {e}"
                    )
                    raise

        raise RuntimeError(
            f"Failed to categorize transactions after {max_attempts} attempts."
        )
