from __future__ import annotations

import os

from .models import ScanReport


def local_explanation(report: ScanReport) -> str:
    if not report.findings:
        return "No material findings were detected under the configured MVP rules."
    ordered = sorted(report.findings, key=lambda f: {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}[f.severity], reverse=True)
    lines = [
        f"DataGuard analyzed {report.row_count:,} rows and {report.column_count} columns.",
        f"Quality score: {report.quality_score}/100. Governance score: {report.governance_score}/100.",
        "",
        "Priority remediation:"
    ]
    for f in ordered[:5]:
        target = f" [{f.column}]" if f.column else ""
        lines.append(f"- {f.severity}{target}: {f.message}. {f.remediation}")
    return "\n".join(lines)

def openai_explanation(report: ScanReport) -> str:
    try:
        from openai import OpenAI
    except ImportError as e:
        raise RuntimeError('Install AI support with: pip install "dataguard-ai[ai]"') from e
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")
    client = OpenAI()
    payload = report.model_dump()
    # Avoid transmitting sample values; only structured findings/metrics are needed.
    for col in payload["columns"]:
        col["sample_values"] = []
    response = client.responses.create(
        model=os.getenv("DATAGUARD_OPENAI_MODEL", "gpt-5-mini"),
        input=[
            {"role": "system", "content": "You are a data quality and governance engineer. Explain findings concisely. Do not invent facts. Prioritize remediation."},
            {"role": "user", "content": str(payload)},
        ],
    )
    return response.output_text
