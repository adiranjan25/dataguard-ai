from __future__ import annotations
from pathlib import Path
import yaml

DEFAULT_CONFIG = {
    "quality": {"max_null_pct": 5.0, "min_unique_pct_for_id": 99.0, "duplicate_row_pct": 1.0,
                "negative_value_columns": ["amount","price","quantity","inventory","stock"]},
    "governance": {"require_owner": False, "owner": None, "freshness_column": None, "max_freshness_hours": 24},
    "pii": {"enabled": True},
    "rules": [],
}
def deep_merge(base, override):
    out=dict(base)
    for k,v in override.items():
        out[k]=deep_merge(out[k],v) if isinstance(v,dict) and isinstance(out.get(k),dict) else v
    return out
def load_config(path=None):
    if not path: return deep_merge({}, DEFAULT_CONFIG)
    user=yaml.safe_load(Path(path).read_text()) or {}
    return deep_merge(DEFAULT_CONFIG,user)
