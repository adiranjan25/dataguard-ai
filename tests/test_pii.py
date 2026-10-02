import pandas as pd
from dataguard.pii import detect_pii

def test_email_detection():
    s = pd.Series(["a@example.com", "b@example.org", "c@example.net"])
    assert "EMAIL" in detect_pii(s, "contact")

def test_ssn_name_hint():
    s = pd.Series(["123-45-6789"])
    assert "SSN" in detect_pii(s, "ssn")
