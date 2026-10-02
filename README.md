# DataGuard AI

**Scan your data. Find quality and governance risks. Understand why they matter. Generate the fix.**

DataGuard AI is an open-source developer tool for **data quality, data governance, PII discovery, schema drift, and data-contract generation**. The core scanner is deterministic and works without an LLM. An optional AI provider can explain findings and recommend remediation without making detection dependent on AI.

> **MVP v0.2.0** — designed to be useful in minutes, extensible in days.

## Why DataGuard AI?

Modern teams often have quality checks, catalogs, contracts, and AI assistants in separate places. DataGuard AI provides a thin developer-friendly layer that can:

- profile CSV/Parquet data;
- detect null, uniqueness, duplicate, numeric-range, and freshness risks;
- detect likely PII with value- and name-based signals;
- compute transparent quality and governance scores;
- snapshot schemas and detect schema drift;
- generate starter dbt tests and a portable YAML data contract;
- export machine-readable JSON for CI/CD;
- explain findings locally, with an optional LLM explanation mode;
- run a complete synthetic retail demo with one command.

## 60-second demo

```bash
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -e .
dataguard demo
```

Or scan your own CSV:

```bash
dataguard scan data/customers.csv
```

JSON for automation:

```bash
dataguard scan data/customers.csv --json-out report.json
```

Generate a data contract and dbt tests:

```bash
dataguard contract data/customers.csv --out contract.yml
dataguard generate-dbt data/customers.csv --out schema.yml
```

Create and compare schema snapshots:

```bash
dataguard snapshot data/customers.csv --out baseline.json
dataguard drift data/customers_v2.csv --baseline baseline.json
```

## Example output

```text
DataGuard AI — customers.csv

Quality score:    84/100
Governance score: 68/100

HIGH     email        7.4% null values
HIGH     ssn          likely sensitive data (SSN)
MEDIUM   customer_id  uniqueness 96.8%
MEDIUM   updated_at   stale relative to configured freshness threshold

Suggested actions
- Add not_null and unique checks for customer_id.
- Classify and protect email and ssn.
- Add a freshness expectation for updated_at.
```

## Detection philosophy

**AI assists; deterministic/statistical checks detect and verify.**

That separation makes results reproducible and lets teams use DataGuard AI without sending production data to an external model.

## MVP architecture

```text
                 ┌──────────────────────┐
                 │      Data source     │
                 │ CSV / Parquet / DB*  │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │       Profiler       │
                 │ schema / stats / PII │
                 └──────────┬───────────┘
                            │
          ┌─────────────────┼──────────────────┐
          │                 │                  │
  ┌───────▼───────┐ ┌──────▼────────┐ ┌──────▼────────┐
  │ Quality rules │ │ Governance     │ │ Schema drift  │
  │ null/unique   │ │ PII/ownership  │ │ snapshots     │
  └───────┬───────┘ └──────┬────────┘ └──────┬────────┘
          └─────────────────┼──────────────────┘
                            │
                 ┌──────────▼───────────┐
                 │ Report + score + fix │
                 └─────┬──────────┬─────┘
                       │          │
                    JSON/YAML   dbt tests
```

`*` DuckDB/PostgreSQL adapters are scaffolded as optional extras in the MVP roadmap; file scanning is production-usable in v0.1.

## v0.2 highlights

- YAML rule engine for reusable data contracts and CI checks
- DuckDB and PostgreSQL table scanning
- standalone HTML quality/governance reports
- Great Expectations expectation export
- GitHub Actions workflow example

```bash
dataguard scan customers.csv --config dataguard.example.yml --html-out report.html
dataguard generate-gx customers.csv --out gx-expectations.json
dataguard scan-duckdb analytics.duckdb --table customers
dataguard scan-postgres --table public.customers
```

See `docs/V0.2.md` for details.

## Commands

| Command | Purpose |
|---|---|
| `dataguard scan PATH` | Profile data and report quality/governance findings |
| `dataguard demo` | Generate and scan a synthetic retail dataset |
| `dataguard contract PATH` | Generate a starter data contract |
| `dataguard generate-dbt PATH` | Generate dbt `schema.yml` tests |
| `dataguard snapshot PATH` | Save a schema/profile baseline |
| `dataguard drift PATH --baseline FILE` | Compare current schema with baseline |
| `dataguard explain REPORT.json` | Explain findings locally or with optional AI |

Run `dataguard --help` for options.

## Configuration

Create `dataguard.yml`:

```yaml
quality:
  max_null_pct: 5
  min_unique_pct_for_id: 99
  duplicate_row_pct: 1

governance:
  require_owner: true
  owner: data-platform@example.com
  freshness_column: updated_at
  max_freshness_hours: 24

pii:
  enabled: true
```

Then:

```bash
dataguard scan customers.csv --config dataguard.yml
```

## Optional AI explanations

The default `explain` command is local and deterministic. To use an OpenAI-compatible explanation provider:

```bash
pip install -e ".[ai]"
export OPENAI_API_KEY=...
dataguard explain report.json --provider openai
```

Only the structured findings are sent by the included provider implementation—not the raw dataset. Review your organization's data-handling policies before enabling any external provider.

## Retail demo

The bundled demo generates synthetic:

- customers;
- orders;
- inventory.

It intentionally injects duplicate IDs, missing values, PII, invalid amounts, orphan-like identifiers, stale timestamps, and other realistic defects.

```bash
dataguard demo --rows 5000
```

## Python API

```python
from dataguard.scanner import scan_path

report = scan_path("customers.csv")
print(report.quality_score)
for finding in report.findings:
    print(finding.severity, finding.column, finding.message)
```

## Roadmap

### v0.2
- DuckDB and PostgreSQL first-class scanning
- user-defined YAML rules
- Great Expectations export
- HTML report
- GitHub Action

### v0.3
- OpenMetadata/DataHub integrations
- dbt artifacts ingestion
- dataset-to-dataset referential checks
- richer statistical drift

### v0.4
- MCP server
- agent tools: `get_table_quality`, `find_pii`, `check_contract`, `explain_failure`
- Ollama/local-model provider

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). Good first contributions include new PII detectors, new exporters, sample datasets, documentation, and database adapters.

## Security

Do not submit real secrets, credentials, or production datasets in issues. See [SECURITY.md](SECURITY.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).
