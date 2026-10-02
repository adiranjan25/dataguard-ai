from __future__ import annotations
from pathlib import Path
import pandas as pd

def load_dataframe(path: str) -> pd.DataFrame:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(p)
    if suffix in {".parquet", ".pq"}:
        try:
            return pd.read_parquet(p)
        except ImportError as e:
            raise RuntimeError('Parquet support requires: pip install "dataguard-ai[parquet]"') from e
    if suffix in {".jsonl", ".ndjson"}:
        return pd.read_json(p, lines=True)
    if suffix == ".json":
        return pd.read_json(p)
    raise ValueError(f"Unsupported file type: {suffix}. Use CSV, JSON/JSONL, or Parquet.")
