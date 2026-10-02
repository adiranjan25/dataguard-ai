from __future__ import annotations
import re
import pandas as pd

PATTERNS = {
    "EMAIL": re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.I),
    "SSN": re.compile(r"^\d{3}-\d{2}-\d{4}$"),
    "PHONE": re.compile(r"^\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$"),
    "IP_ADDRESS": re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$"),
}

NAME_HINTS = {
    "email": "EMAIL",
    "e_mail": "EMAIL",
    "ssn": "SSN",
    "social_security": "SSN",
    "phone": "PHONE",
    "mobile": "PHONE",
    "first_name": "PERSON_NAME",
    "last_name": "PERSON_NAME",
    "full_name": "PERSON_NAME",
    "address": "ADDRESS",
    "street": "ADDRESS",
    "zip": "POSTAL_CODE",
    "postal": "POSTAL_CODE",
    "dob": "DATE_OF_BIRTH",
    "birth_date": "DATE_OF_BIRTH",
}

def detect_pii(series: pd.Series, column_name: str, sample_size: int = 200) -> list[str]:
    detected = set()
    low = column_name.lower()
    for hint, pii_type in NAME_HINTS.items():
        if hint in low:
            detected.add(pii_type)

    values = series.dropna().astype(str).head(sample_size)
    if values.empty:
        return sorted(detected)

    for pii_type, pattern in PATTERNS.items():
        hits = sum(bool(pattern.match(v.strip())) for v in values)
        if hits / len(values) >= 0.6:
            detected.add(pii_type)
    return sorted(detected)
