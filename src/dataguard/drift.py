from __future__ import annotations

from typing import Any

from .models import ScanReport


def snapshot(report: ScanReport) -> dict[str, Any]:
    return {
        "source": report.source,
        "row_count": report.row_count,
        "columns": {c.name: {"dtype": c.dtype, "pii_types": c.pii_types} for c in report.columns},
    }

def compare(current: ScanReport, baseline: dict[str, Any]) -> list[dict[str, Any]]:
    changes = []
    old = baseline.get("columns", {})
    new = {c.name: {"dtype": c.dtype, "pii_types": c.pii_types} for c in current.columns}
    for name in sorted(set(old) - set(new)):
        changes.append({"type": "COLUMN_REMOVED", "column": name, "severity": "HIGH"})
    for name in sorted(set(new) - set(old)):
        changes.append({"type": "COLUMN_ADDED", "column": name, "severity": "LOW"})
    for name in sorted(set(old) & set(new)):
        if old[name].get("dtype") != new[name].get("dtype"):
            changes.append({
                "type": "TYPE_CHANGED", "column": name, "severity": "HIGH",
                "before": old[name].get("dtype"), "after": new[name].get("dtype")
            })
        if old[name].get("pii_types", []) != new[name].get("pii_types", []):
            changes.append({
                "type": "CLASSIFICATION_CHANGED", "column": name, "severity": "MEDIUM",
                "before": old[name].get("pii_types", []), "after": new[name].get("pii_types", [])
            })
    return changes
