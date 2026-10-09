# DataGuard AI

[![CI](https://github.com/adiranjan25/dataguard-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/adiranjan25/dataguard-ai/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/dataguard-ai.svg)](https://pypi.org/project/dataguard-ai/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Status: Public Beta](https://img.shields.io/badge/status-public%20beta-orange.svg)](#project-status)

**Open-source, AI-assisted data quality and governance for modern data platforms.**

> **Scan your data. Find quality and governance risks. Understand why they matter. Generate the fix.**

DataGuard AI is a developer-first toolkit for **data quality, data governance, PII discovery, schema drift, data contracts, and CI/CD-friendly validation**. Detection is deterministic and does **not** require an LLM. Optional AI assistance can explain structured findings and suggest remediation without making quality detection dependent on a model.

**Current version: v0.2.1 public beta.**

**Links:** [PyPI](https://pypi.org/project/dataguard-ai/) · [Releases](https://github.com/adiranjan25/dataguard-ai/releases) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)

## Why DataGuard AI?

Data teams often manage quality rules, contracts, PII checks, schema drift, metadata, and AI assistants in separate workflows. DataGuard AI provides a lightweight layer developers can run locally or in CI to surface these risks through one interface.


## See DataGuard AI in Action

Try the demo:

```bash
pip install dataguard-ai==0.2.1
dataguard demo --rows 100
```

### Example Quality Report

![DataGuard AI Quality Report](dataguard-ai-report-screenshot.png)

See how DataGuard AI identifies data quality
and governance risks using synthetic sample data.
  

## 30-second example

Install and run the demo:

```bash
pip install dataguard-ai
dataguard demo --rows 100
```

Example findings:

```text
DataGuard AI — customers.csv
Quality score: 95/100
Governance score: 61/100

HIGH    first_name   Likely sensitive data: PERSON_NAME
MEDIUM  email        8.0% null values
HIGH    email        Likely sensitive data: EMAIL
HIGH    ssn          Likely sensitive data: SSN

DataGuard AI — orders.csv
MEDIUM  amount       Negative values detected in a non-negative business measure

DataGuard AI — inventory.csv
MEDIUM  inventory    Negative values detected in a non-negative business measure
```

The demo uses synthetic retail data, so you can explore the project without providing proprietary datasets.


### What v0.2 can do

- Profile CSV and JSON data, with optional Parquet support
- Scan **DuckDB** and **PostgreSQL** tables
- Run reusable **YAML data-quality rules**
- Detect nulls, duplicate rows, uniqueness issues, range violations, and freshness risks
- Identify likely PII using value and column-name signals
- Compute transparent quality and governance scores
- Generate standalone **HTML** and machine-readable **JSON** reports
- Snapshot schemas and detect schema drift
- Generate starter **dbt tests** and YAML data contracts
- Export portable **Great Expectations** expectation configuration
- Run in **GitHub Actions**
- Explain findings locally, with optional AI-assisted remediation guidance

## Quick start

### Install from PyPI

```bash
pip install dataguard-ai
```

Run the synthetic retail demo:

```bash
dataguard demo --rows 100
```

Or scan your own dataset:

```bash
dataguard scan data/customers.csv
```

Generate JSON and HTML reports:

```bash
dataguard scan data/customers.csv --json-out report.json --html-out report.html
```

### Install from source

For development or contributing:

```bash
git clone https://github.com/adiranjan25/dataguard-ai.git
cd dataguard-ai
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Detection philosophy

> **AI assists; deterministic and statistical checks detect and verify.**

The default scanning path does not require an LLM. This keeps findings reproducible and allows teams to use DataGuard AI without sending raw production datasets to an external model.

## YAML rule engine

Supported v0.2 custom rule types:

- `not_null`
- `unique`
- `accepted_values`
- `between`
- `regex`
- `max_null_pct`
- `row_count_between`

Example:

```yaml
quality:
  max_null_pct: 5
governance:
  owner: data-platform@example.com
rules:
  - type: not_null
    column: customer_id
    severity: CRITICAL
  - type: unique
    column: customer_id
  - type: accepted_values
    column: state
    values: [TX, CA, NY]
  - type: between
    column: amount
    min: 0
    max: 100000
```

```bash
dataguard scan customers.csv --config dataguard.yml --html-out report.html
```

### Explicit uniqueness rules

DataGuard does not assume that every column ending in `_id` is a primary key. Columns such as `customer_id` or `store_id` often represent foreign keys and may legitimately contain repeated values.

When uniqueness is part of the dataset contract, declare it explicitly:

```yaml
rules:
  - type: unique
    column: customer_id
    severity: HIGH
```

A generic column named `id` is still treated as a primary-key-like identifier by the built-in heuristic.

## Database scanning


### DuckDB

```bash
pip install "dataguard-ai[duckdb]"
dataguard scan-duckdb analytics.duckdb --table customers --html-out report.html
```

### PostgreSQL

```bash
pip install "dataguard-ai[postgres]"
export DATAGUARD_POSTGRES_URL='postgresql+psycopg://user:password@host/database'
dataguard scan-postgres --table public.customers --html-out report.html
```

> **Current limitation:** database scans load the selected table/result into memory. Warehouse-scale pushdown profiling is a roadmap item.

## Reports

```bash
dataguard scan customers.csv --html-out report.html
dataguard scan customers.csv --json-out report.json
```

The HTML report includes quality/governance scores, findings, severity, affected columns, suggested remediation, column profiles, and detected PII.

## Data contracts and dbt

```bash
dataguard contract data/customers.csv --out contract.yml
dataguard generate-dbt data/customers.csv --out schema.yml
```

These outputs are intended as reviewable starting points rather than replacements for domain-specific contract design.

## Great Expectations

```bash
dataguard generate-gx data/customers.csv --out gx-expectations.json
```

The exporter deliberately produces reviewable configuration rather than modifying an existing Great Expectations project.

## Schema drift

```bash
dataguard snapshot data/customers.csv --out baseline.json
dataguard drift data/customers_v2.csv --baseline baseline.json
```

## GitHub Actions

The repository includes an example workflow at `.github/workflows/dataguard.yml` that demonstrates scanning sample data and uploading JSON/HTML reports as workflow artifacts.

Project CI separately runs linting and automated tests against **Python 3.10, 3.11, and 3.12**.

## Optional AI explanations

Local deterministic explanations are available without an external model.

```bash
pip install "dataguard-ai[ai]"
export OPENAI_API_KEY=...
dataguard explain report.json --provider openai
```

The included provider sends structured findings rather than raw dataset rows. Always review your organization's security, privacy, and data-handling requirements before enabling an external provider.

## Architecture

```text
                    Data sources
                         |
       +-----------------+-----------------+
       |                 |                 |
   CSV / JSON         DuckDB          PostgreSQL
   / Parquet             |                 |
       +-----------------+-----------------+
                         |
                         v
                  DataGuard scanner
                         |
        +----------------+----------------+
        |                |                |
     Profiling       Rule engine     PII detection
        |                |                |
        +----------------+----------------+
                         |
                         v
              Quality + governance
                         |
       +-----------+-----+------+-----------+
       |           |            |           |
       v           v            v           v
      CLI         JSON         HTML    Contracts / dbt / GX
```

Detection and optional AI explanation are intentionally separated.

## Commands

| Command | Purpose |
|---|---|
| `dataguard scan PATH` | Profile file data and report quality/governance findings |
| `dataguard demo` | Generate and scan synthetic retail datasets |
| `dataguard scan-duckdb DATABASE --table TABLE` | Scan a DuckDB table |
| `dataguard scan-postgres --table TABLE` | Scan a PostgreSQL table |
| `dataguard contract PATH` | Generate a starter data contract |
| `dataguard generate-dbt PATH` | Generate starter dbt tests |
| `dataguard generate-gx PATH` | Generate portable GX expectation configuration |
| `dataguard snapshot PATH` | Save a schema/profile baseline |
| `dataguard drift PATH --baseline FILE` | Compare current schema with a baseline |
| `dataguard explain REPORT.json` | Explain findings locally or with optional AI |

Run `dataguard --help` for current CLI options.

## Python API

```python
from dataguard.scanner import scan_path

report = scan_path("customers.csv")
print(report.quality_score)

for finding in report.findings:
    print(finding.severity, finding.column, finding.message)
```

## Retail demo

The bundled synthetic retail demo creates customer, order, and inventory datasets with intentionally injected quality/governance problems so developers can explore DataGuard AI without providing proprietary data.

```bash
dataguard demo --rows 5000
```

## Project status

DataGuard AI is currently a **public beta (v0.2.1)**. The API, configuration schema, scoring model, and command behavior may evolve before v1.0.

The project is suitable for experimentation, development workflows, demos, and community feedback. Evaluate it against your own requirements before using it as a production control.

## Roadmap

### v0.3 — Metadata and context

- OpenMetadata integration
- DataHub integration
- dbt artifact ingestion
- Dataset-to-dataset referential checks
- Richer statistical drift and anomaly detection

### v0.4 — Agent access

- MCP server
- Agent-accessible quality, contract, and governance tools
- Ollama/local-model provider
- Governance context for AI agents
- Assisted remediation workflows

### Toward v1.0

- Warehouse-scale profiling/pushdown
- Broader integration tests
- Benchmark datasets and reproducible evaluation
- Stable configuration and CLI contracts

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidance.

Useful first contributions include additional PII detectors, report/export formats, documentation improvements, tests, database adapters, and integration examples.

## Security and privacy

- Never submit secrets, credentials, or proprietary production datasets in GitHub issues.
- Use environment variables or an appropriate secrets manager for database and model credentials.
- Treat detected PII findings as sensitive operational metadata.
- Review organizational security/privacy requirements before using an external AI provider.
- See [SECURITY.md](SECURITY.md) for vulnerability-reporting guidance.

## License

DataGuard AI is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE).
