import pandas as pd
from dataguard.scanner import scan_dataframe
from dataguard.exporters import build_dbt_schema
from dataguard.config import DEFAULT_CONFIG

def test_dbt_export_has_unique_id_test():
    report = scan_dataframe(pd.DataFrame({"customer_id": [1,2,3]}), source="customers.csv", config=DEFAULT_CONFIG)
    doc = build_dbt_schema(report)
    tests = doc["models"][0]["columns"][0]["data_tests"]
    assert "unique" in tests
    assert "not_null" in tests
