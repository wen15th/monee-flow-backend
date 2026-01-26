from datetime import datetime, date
import re
from typing import Optional


def normalize_description(desc: str) -> str:
    """
    Clean transaction description noise:
    """
    text = (desc or "").strip()

    for pattern in ["TFR-TO C/C", "SEND E-TFR"]:
        if pattern in text:
            return pattern

    # 0) Normalize spaces
    text = re.sub(r"\s+", " ", text)

    # 1) Remove ' #1234' anywhere
    text = re.sub(r"\s*#\d+\b", "", text)

    # 2) Remove '/suffix' with letters+digits, e.g. '/G3ZGWU'
    text = re.sub(r"/(?=[A-Za-z0-9]*[A-Za-z])(?=[A-Za-z0-9]*\d)[A-Za-z0-9]+$", "", text)

    # 3) Remove '*suffix' with letters+digits, e.g. '*NI3HV3DJ1'
    text = re.sub(
        r"\*(?=[A-Za-z0-9]*[A-Za-z])(?=[A-Za-z0-9]*\d)[A-Za-z0-9]+$", "", text
    )

    # 4) Remove '******1234' (card numbers)
    text = re.sub(r"\*{2,}\d+$", "", text)
    text = re.sub(r"\*{2,}", "", text)

    # 5) Remove '*digits', e.g. 'UPS*123456...'
    text = re.sub(r"\*\d+$", "", text)

    # 6) Remove trailing pure digits
    text = re.sub(r"\s+\d+$", "", text)

    # 7) Remove common transaction network / suffix identifiers
    text = re.sub(
        r"\s*_(V|M|MC|AX|AMEX|DS|DISC|P|I|WD|DEP|TFR|BP|INT)$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # 8)
    text = re.sub(
        r"\b(?:[A-Za-z]\d){3,}[A-Za-z]?\b|\b(?:\d[A-Za-z]){3,}\d?\b", "", text
    )

    # Convert to uppercase
    return text.strip().upper()


def parse_date(date_str: str) -> Optional[date]:
    formats = ["%m/%d/%Y", "%Y-%m-%d"]  # Possible date format
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def first_non_empty(item: dict, *keys: str) -> str:
    for k in keys:
        v = item.get(k)
        if v not in (None, ""):
            return str(v).strip()
    return ""
