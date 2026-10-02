from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

Severity = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

class Finding(BaseModel):
    code: str
    severity: Severity
    column: str | None = None
    message: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    remediation: str

class ColumnProfile(BaseModel):
    name: str
    dtype: str
    null_pct: float
    unique_pct: float
    sample_values: list[str] = Field(default_factory=list)
    pii_types: list[str] = Field(default_factory=list)

class ScanReport(BaseModel):
    source: str
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    row_count: int
    column_count: int
    duplicate_row_pct: float
    quality_score: int
    governance_score: int
    columns: list[ColumnProfile]
    findings: list[Finding]
    metadata: dict[str, Any] = Field(default_factory=dict)
