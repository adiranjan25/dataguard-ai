from __future__ import annotations

from typing import Any

import yaml

from .models import ScanReport


def build_contract(report: ScanReport) -> dict[str, Any]:
    columns = {}
    for c in report.columns:
        constraints = []
        if c.null_pct == 0:
            constraints.append("not_null")
        if c.unique_pct >= 99.9 and (c.name == "id" or c.name.endswith("_id")):
            constraints.append("unique")
        columns[c.name] = {
            "type": c.dtype,
            "nullable": c.null_pct > 0,
            "constraints": constraints,
            "classification": c.pii_types or ["UNCLASSIFIED"],
        }
    return {
        "version": "0.1",
        "dataset": report.source,
        "owner": report.metadata.get("owner"),
        "quality_score_at_generation": report.quality_score,
        "columns": columns,
    }

def build_dbt_schema(report: ScanReport) -> dict[str, Any]:
    table_name = report.source.rsplit("/", 1)[-1].split(".")[0].replace("-", "_")
    cols = []
    for c in report.columns:
        tests = []
        if c.null_pct == 0:
            tests.append("not_null")
        if c.unique_pct >= 99.9 and (c.name == "id" or c.name.endswith("_id")):
            tests.append("unique")
        entry = {"name": c.name}
        if tests:
            entry["data_tests"] = tests
        if c.pii_types:
            entry["meta"] = {"classification": c.pii_types}
        cols.append(entry)
    return {"version": 2, "models": [{"name": table_name, "columns": cols}]}

def dump_yaml(data: dict) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
