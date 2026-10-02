import pandas as pd
from dataguard.scanner import scan_dataframe
from dataguard.drift import snapshot, compare
from dataguard.config import DEFAULT_CONFIG

def test_added_column_drift():
    old = scan_dataframe(pd.DataFrame({"id": [1, 2]}), config=DEFAULT_CONFIG)
    new = scan_dataframe(pd.DataFrame({"id": [1, 2], "new_col": ["a", "b"]}), config=DEFAULT_CONFIG)
    changes = compare(new, snapshot(old))
    assert any(c["type"] == "COLUMN_ADDED" for c in changes)
