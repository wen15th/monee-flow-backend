import os
import logging
from typing import List

from src.llm_providers.deepseek import DeepSeekClient
from src.llm_providers.gemini import GeminiClient
from src.schemas.transaction import TransactionCategoryList


class LLMTransactionCategorizer:
    def __init__(self):
        self.providers = [DeepSeekClient(), GeminiClient()]
        self.response_model = TransactionCategoryList

        prompt_path = os.path.join(os.path.dirname(__file__), "prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    def categorize(self, transaction_descriptions: List[str]) -> List[dict]:
        logging.info(f"[LLM] Categorizing: {transaction_descriptions}")
        user_content = "\n".join(transaction_descriptions)

        last_error = None
        for provider in self.providers:
            name = provider.__class__.__name__
            logging.info(f"[LLM] Trying provider: {name}")
            try:
                result = provider.complete(
                    system=self.system_prompt,
                    user=user_content,
                    response_model=self.response_model,
                )
                logging.info(f"[LLM] Response: {result}")
                return result["trans_category_list"]
            except Exception as e:
                logging.warning(f"[LLM] Provider {name} failed: {e}, trying next...")
                last_error = e

        raise RuntimeError(f"All providers failed. Last error: {last_error}")
