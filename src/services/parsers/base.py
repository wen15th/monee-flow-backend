from abc import ABC, abstractmethod
from src.core.app_context import AppContext
import uuid

class BaseBankParser(ABC):
    @abstractmethod
    def parse(self, user_id: uuid.UUID, raw_data: list[dict]):
        """
        Parse the bank statement, return transaction list。
        Each dict includes:
        - date: transaction date
        - description: original transaction description or merchant info
        - norm_desc: normalized description
        - amount: amount of payment
        """
        pass