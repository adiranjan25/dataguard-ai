from __future__ import annotations

import re

import pandas as pd

from .models import Finding


def _finding(code, severity, column, message, evidence, remediation):
    return Finding(code=code, severity=severity, column=column, message=message,
                   evidence=evidence, remediation=remediation)

def evaluate_custom_rules(df: pd.DataFrame, rules: list[dict] | None) -> list[Finding]:
    """Evaluate portable YAML rules. Unknown rule types fail fast instead of being silently ignored."""
    findings: list[Finding] = []
    for i, rule in enumerate(rules or []):
        kind = rule.get("type")
        col = rule.get("column")
        severity = str(rule.get("severity", "HIGH")).upper()
        if col and col not in df.columns:
            findings.append(_finding("RULE_COLUMN_MISSING", severity, col,
                f"Configured rule references missing column '{col}'", {"rule": rule},
                "Fix the rule or restore the expected column."))
            continue
        s = df[col] if col else None

        if kind == "not_null":
            count = int(s.isna().sum())
            if count:
                findings.append(_finding("RULE_NOT_NULL", severity, col, f"{count} null values violate not_null",
                    {"unexpected_count": count}, f"Populate {col} or revise the contract if nulls are valid."))

        elif kind == "unique":
            dup = int(s.dropna().duplicated().sum())
            if dup:
                findings.append(_finding("RULE_UNIQUE", severity, col, f"{dup} duplicate values violate unique",
                    {"duplicate_count": dup}, f"Deduplicate {col} or correct key-generation logic."))

        elif kind == "accepted_values":
            allowed = set(rule.get("values", []))
            bad = s.dropna()[~s.dropna().isin(allowed)]
            if len(bad):
                findings.append(_finding("RULE_ACCEPTED_VALUES", severity, col,
                    f"{len(bad)} values are outside the accepted set", {"unexpected_count": len(bad), "allowed": list(allowed)},
                    f"Correct invalid {col} values or update the approved domain."))

        elif kind == "between":
            lo, hi = rule.get("min"), rule.get("max")
            numeric = pd.to_numeric(s, errors="coerce")
            mask = pd.Series(False, index=s.index)
            if lo is not None: mask |= numeric < lo
            if hi is not None: mask |= numeric > hi
            count = int(mask.fillna(False).sum())
            if count:
                findings.append(_finding("RULE_BETWEEN", severity, col, f"{count} values violate configured range",
                    {"unexpected_count": count, "min": lo, "max": hi}, f"Validate {col} against its business range."))

        elif kind == "regex":
            pattern = re.compile(rule["pattern"])
            vals = s.dropna().astype(str)
            count = int((~vals.map(pattern.fullmatch).map(bool)).sum())
            if count:
                findings.append(_finding("RULE_REGEX", severity, col, f"{count} values violate regex",
                    {"unexpected_count": count, "pattern": rule["pattern"]}, f"Normalize or reject malformed {col} values."))

        elif kind == "max_null_pct":
            pct = float(s.isna().mean() * 100) if len(df) else 0.0
            limit = float(rule["value"])
            if pct > limit:
                findings.append(_finding("RULE_MAX_NULL_PCT", severity, col, f"{pct:.2f}% null exceeds {limit:g}%",
                    {"observed_pct": round(pct,2), "max_pct": limit}, f"Reduce missing {col} values or revise the threshold."))

        elif kind == "row_count_between":
            lo, hi = rule.get("min"), rule.get("max")
            bad = (lo is not None and len(df) < lo) or (hi is not None and len(df) > hi)
            if bad:
                findings.append(_finding("RULE_ROW_COUNT", severity, None, f"Row count {len(df)} violates expected range",
                    {"row_count": len(df), "min": lo, "max": hi}, "Investigate ingestion completeness or unexpected volume."))

        else:
            raise ValueError(f"Unsupported custom rule type at index {i}: {kind}")
    return findings
