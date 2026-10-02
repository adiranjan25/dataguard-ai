import pandas as pd

from dataguard.config import DEFAULT_CONFIG
from dataguard.scanner import scan_dataframe


def test_scan_finds_duplicate_id_and_pii():
    df = pd.DataFrame(
        {
            "id": [1, 1, 2, 3],
            "email": ["a@example.com", "b@example.com", None, "d@example.com"],
            "amount": [10, -2, 30, 40],
        }
    )

    report = scan_dataframe(df, config=DEFAULT_CONFIG)
    codes = {f.code for f in report.findings}

    assert "ID_UNIQUENESS" in codes
    assert "PII_DETECTED" in codes
    assert "NEGATIVE_VALUE" in codes


def test_repeated_foreign_key_does_not_imply_uniqueness():
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3, 4],
            "customer_id": [101, 101, 102, 102],
            "amount": [10, 20, 30, 40],
        }
    )

    report = scan_dataframe(df, config=DEFAULT_CONFIG)

    inferred_id_findings = [
        f
        for f in report.findings
        if f.code == "ID_UNIQUENESS" and f.column == "customer_id"
    ]

    assert inferred_id_findings == []


def test_explicit_unique_rule_still_enforces_foreign_key_uniqueness():
    df = pd.DataFrame(
        {
            "customer_id": [101, 101, 102, 103],
        }
    )

    config = {
        **DEFAULT_CONFIG,
        "rules": [
            {
                "type": "unique",
                "column": "customer_id",
                "severity": "HIGH",
            }
        ],
    }

    report = scan_dataframe(df, config=config)

    assert any(
        f.code == "RULE_UNIQUE" and f.column == "customer_id"
        for f in report.findings
    )


def test_clean_dataset_scores_high():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "value": [10, 20, 30, 40],
        }
    )

    report = scan_dataframe(df, config=DEFAULT_CONFIG)

    assert report.quality_score >= 90
