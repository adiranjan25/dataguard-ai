from __future__ import annotations

from .models import ScanReport


def build_gx_expectations(report: ScanReport) -> dict:
    """Portable GX expectation configuration. It can be translated into GX Core objects by the user's GX project."""
    expectations=[]
    for c in report.columns:
        if c.null_pct == 0:
            expectations.append({"type":"expect_column_values_to_not_be_null","kwargs":{"column":c.name}})
        if c.unique_pct >= 99.9 and (c.name=="id" or c.name.endswith("_id")):
            expectations.append({"type":"expect_column_values_to_be_unique","kwargs":{"column":c.name}})
    return {"suite_name":"dataguard_generated","meta":{"generated_by":"dataguard-ai","source":report.source},
            "expectations":expectations}
