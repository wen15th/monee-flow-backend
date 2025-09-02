import asyncio
import os
import json
import logging
from huggingface_hub import InferenceClient
from src.schemas.transaction import TransactionCategoryList
from typing import List


class HFTransactionCategorizer:
    def __init__(self, model_name: str = "meta-llama/Llama-3.3-70B-Instruct"):
        self.client = InferenceClient(
            api_key=os.getenv("HF_TOKEN", ""),
            provider="cerebras"
        )
        self.model_name = model_name

        # Convert Pydantic to JSON schema
        self.response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "TransactionCategoryList",
                "schema": TransactionCategoryList.model_json_schema(),
                "strict": True,
            },
        }

        # Initialize system prompt
        self.system_prompt = ""
        prompt_path = os.path.join(os.path.dirname(__file__), "prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()


    def categorize(self, transaction_descriptions: List[str]) -> List[dict]:
        logging.info(f"[HF API Call] Request transaction_descriptions: {transaction_descriptions}")

        # Build system/user messages
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": "\n".join(transaction_descriptions)}
        ]

        response = self.client.chat_completion(
            messages=messages,
            response_format=self.response_format,
            model=self.model_name,
        )

        structured_data = response.choices[0].message.content
        logging.info(f"[HF API Call] Response structured_data: {structured_data}")

        trans_category_list = json.loads(structured_data)['trans_category_list']

        return trans_category_list


    # async def async_categorize_with_retry(self, transaction_descriptions: List[str], retries: int = 2, delay: int = 60):
    #     for attempt in range(retries + 1):
    #         logging.info(f"[HF API Call] start, attempt {attempt + 1}")
    #         try:
    #             loop = asyncio.get_event_loop()
    #             result = await loop.run_in_executor(None, self.categorize, transaction_descriptions)
    #             return result
    #         except Exception as e:
    #             logging.error(f"[HF API Call] failed at attempt {attempt + 1}: {e}")
    #             if attempt < retries:
    #                 await asyncio.sleep(delay * (attempt + 1))
    #             else:
    #                 # TODO
    #                 # log_failure_to_db(transactions, e)
    #                 return None