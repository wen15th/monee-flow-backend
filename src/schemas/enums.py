# src/schemas/enums.py
from enum import IntEnum, Enum


class BankEnum(str, Enum):
    TD = "TD"
    Rogers = "Rogers"
    CMB = "CMB"


class StatementStatus(IntEnum):
    COMPLETED = 1
    DELETED = 2
    PROCESSING = 3
    FAILED = 4
