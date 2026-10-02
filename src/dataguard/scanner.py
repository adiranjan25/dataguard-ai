from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

from .config import load_config
from .io import load_dataframe
from .models import ColumnProfile, Finding, ScanReport
from .pii import detect_pii
from .rules import evaluate_custom_rules

def _sev_for_null(null_pct: float, threshold: float) -> str:
    if null_pct >= max(25.0, threshold * 4):
        return "HIGH"
    return "MEDIUM"

def _looks_like_id(name: str) -> bool:
    low = name.lower()
    return low == "id" or low.endswith("_id") or low.startswith("id_")

def _quality_score(findings: list[Finding]) -> int:
    weights = {"LOW": 2, "MEDIUM": 5, "HIGH": 10, "CRITICAL": 20}
    quality_codes = {"NULL_RATE", "ID_UNIQUENESS", "DUPLICATE_ROWS", "NEGATIVE_VALUE", "FRESHNESS"}
    penalty = sum(weights[f.severity] for f in findings if f.code in quality_codes)
    return max(0, 100 - min(100, penalty))

def _governance_score(findings: list[Finding], has_owner: bool) -> int:
    score = 100
    if not has_owner:
        score -= 15
    pii_findings = [f for f in findings if f.code == "PII_DETECTED"]
    score -= min(40, len(pii_findings) * 8)
    if any(f.code == "FRESHNESS" for f in findings):
        score -= 10
    return max(0, score)

def scan_dataframe(df: pd.DataFrame, source: str = "<dataframe>", config: dict | None = None) -> ScanReport:
    cfg = config or load_config()
    qcfg = cfg["quality"]
    gcfg = cfg["governance"]
    pii_enabled = cfg.get("pii", {}).get("enabled", True)

    findings: list[Finding] = []
    profiles: list[ColumnProfile] = []
    n = len(df)

    dup_pct = 0.0 if n == 0 else round(float(df.duplicated().mean() * 100), 2)
    if dup_pct > float(qcfg["duplicate_row_pct"]):
        findings.append(Finding(
            code="DUPLICATE_ROWS", severity="HIGH", message=f"{dup_pct}% duplicate rows detected",
            evidence={"duplicate_row_pct": dup_pct},
            remediation="Identify the natural/business key and deduplicate upstream or enforce a uniqueness constraint."
        ))

    negative_hints = [x.lower() for x in qcfg.get("negative_value_columns", [])]

    for col in df.columns:
        s = df[col]
        null_pct = 0.0 if n == 0 else round(float(s.isna().mean() * 100), 2)
        unique_pct = 0.0 if n == 0 else round(float(s.nunique(dropna=True) / n * 100), 2)
        pii_types = detect_pii(s, str(col)) if pii_enabled else []

        samples = [str(x)[:80] for x in s.dropna().head(3).tolist()]
        profiles.append(ColumnProfile(
            name=str(col), dtype=str(s.dtype), null_pct=null_pct,
            unique_pct=unique_pct, sample_values=samples, pii_types=pii_types
        ))

        if null_pct > float(qcfg["max_null_pct"]):
            findings.append(Finding(
                code="NULL_RATE", severity=_sev_for_null(null_pct, float(qcfg["max_null_pct"])),
                column=str(col), message=f"{null_pct}% null values",
                evidence={"null_pct": null_pct, "threshold_pct": qcfg["max_null_pct"]},
                remediation=f"Investigate missing {col} values; add a not-null rule if the field is required."
            ))

        if _looks_like_id(str(col)) and unique_pct < float(qcfg["min_unique_pct_for_id"]):
            findings.append(Finding(
                code="ID_UNIQUENESS", severity="HIGH", column=str(col),
                message=f"ID-like column is only {unique_pct}% unique",
                evidence={"unique_pct": unique_pct, "threshold_pct": qcfg["min_unique_pct_for_id"]},
                remediation=f"Check duplicate {col} generation, replayed ingestion, joins, or missing deduplication."
            ))

        if pd.api.types.is_numeric_dtype(s) and any(h in str(col).lower() for h in negative_hints):
            neg_count = int((s.dropna() < 0).sum())
            if neg_count:
                findings.append(Finding(
                    code="NEGATIVE_VALUE", severity="MEDIUM", column=str(col),
                    message=f"{neg_count} negative values in a non-negative business measure",
                    evidence={"negative_count": neg_count},
                    remediation=f"Validate source semantics and add a >= 0 expectation for {col} when appropriate."
                ))

        if pii_types:
            findings.append(Finding(
                code="PII_DETECTED", severity="HIGH", column=str(col),
                message=f"Likely sensitive data: {', '.join(pii_types)}",
                evidence={"pii_types": pii_types},
                remediation="Classify the field, verify access controls, masking, retention, and downstream usage."
            ))

    freshness_col = gcfg.get("freshness_column")
    if freshness_col and freshness_col in df.columns and n:
        parsed = pd.to_datetime(df[freshness_col], errors="coerce", utc=True)
        latest = parsed.max()
        if pd.notna(latest):
            age_hours = (pd.Timestamp.now(tz="UTC") - latest).total_seconds() / 3600
            threshold = float(gcfg.get("max_freshness_hours", 24))
            if age_hours > threshold:
                findings.append(Finding(
                    code="FRESHNESS", severity="HIGH", column=freshness_col,
                    message=f"Latest record is {age_hours:.1f} hours old (threshold {threshold:g}h)",
                    evidence={"age_hours": round(age_hours, 2), "threshold_hours": threshold},
                    remediation="Check upstream ingestion/CDC health and define an explicit freshness SLA."
                ))

    findings.extend(evaluate_custom_rules(df, cfg.get("rules", [])))

    owner = gcfg.get("owner")
    if gcfg.get("require_owner") and not owner:
        findings.append(Finding(
            code="MISSING_OWNER", severity="MEDIUM", message="Dataset owner is not configured",
            remediation="Assign a technical or business owner in dataguard.yml or your catalog."
        ))

    return ScanReport(
        source=source, row_count=n, column_count=len(df.columns), duplicate_row_pct=dup_pct,
        quality_score=_quality_score(findings),
        governance_score=_governance_score(findings, bool(owner)),
        columns=profiles, findings=findings,
        metadata={"owner": owner}
    )

def scan_path(path: str, config_path: str | None = None) -> ScanReport:
    cfg = load_config(config_path)
    df = load_dataframe(path)
    return scan_dataframe(df, source=str(Path(path)), config=cfg)
