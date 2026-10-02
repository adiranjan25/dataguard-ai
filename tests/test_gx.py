import pandas as pd
from dataguard.scanner import scan_dataframe
from dataguard.gx_exporter import build_gx_expectations
def test_gx_export():
    r=scan_dataframe(pd.DataFrame({"customer_id":[1,2,3]}), source="customers.csv")
    x=build_gx_expectations(r)
    types={e["type"] for e in x["expectations"]}
    assert "expect_column_values_to_be_unique" in types
    assert "expect_column_values_to_not_be_null" in types
