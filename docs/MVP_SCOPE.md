# MVP scope and acceptance criteria

## In scope for v0.1
- local file scan: CSV, JSON/JSONL, optional Parquet;
- column profile: type, null %, uniqueness %, samples;
- duplicate-row check;
- ID-like uniqueness check;
- negative-value heuristic;
- configurable freshness check;
- PII signals;
- quality/governance scoring;
- JSON output;
- YAML contract export;
- dbt test export;
- schema/classification baseline and drift;
- synthetic retail demo;
- local and optional AI explanations;
- unit tests and CI.

## Explicitly not claimed in v0.1
- enterprise-scale distributed profiling;
- complete PII discovery or regulatory compliance;
- automatic causal root-cause analysis;
- full semantic data contracts;
- production OpenMetadata/DataHub integration;
- guaranteed anomaly detection.

Those are roadmap items and should not be overstated in public messaging.
