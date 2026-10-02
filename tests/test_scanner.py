import pandas as pd

from dataguard.config import DEFAULT_CONFIG
from dataguard.scanner import scan_dataframe


def test_scan_finds_duplicate_id_and_pii():
    df = pd.DataFrame({
        "customer_id": [1, 1, 2, 3],
        "email": ["a@example.com", "b@example.com", None, "d@example.com"],
        "amount": [10, -2, 30, 40],
    })
    report = scan_dataframe(df, config=DEFAULT_CONFIG)
    codes = {f.code for f in report.findings}
    assert "ID_UNIQUENESS" in codes
    assert "PII_DETECTED" in codes
    assert "NEGATIVE_VALUE" in codes
    assert report.quality_score < 100

def test_clean_dataset_scores_high():
    df = pd.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})
    report = scan_dataframe(df, config=DEFAULT_CONFIG)
    assert report.quality_score == 100
