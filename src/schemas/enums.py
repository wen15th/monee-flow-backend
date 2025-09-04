# src/schemas/enums.py
from enum import Enum

class BankEnum(str, Enum):
    TD = "TD"
    Rogers = "Rogers"