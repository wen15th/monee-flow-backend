from .cmb_parser import CMBBankParser
from .td_parser import TDBankParser
from .rogers_parser import RogersBankParser

BANK_PARSERS = {
    "TD": TDBankParser(),
    "ROGERS": RogersBankParser(),
    "CMB": CMBBankParser(),
}


def get_parser(bank_name: str):
    parser = BANK_PARSERS.get(bank_name.upper())
    if not parser:
        raise ValueError(f"No parser found for bank: {bank_name}")
    return parser
