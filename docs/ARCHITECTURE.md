# Architecture

DataGuard AI separates **detection** from **explanation**.

1. `io.py` loads supported local data.
2. `scanner.py` computes profiles and deterministic findings.
3. `pii.py` applies transparent PII signals.
4. `models.py` defines the stable report contract.
5. `exporters.py` turns the report into contracts/dbt tests.
6. `drift.py` creates and compares baselines.
7. `explain.py` explains structured findings locally or through an optional provider.
8. `cli.py` exposes the workflow to developers.

This makes the report useful in CI/CD even when no AI provider is configured.

## Extension points

Future adapters should convert a source into either:
- a pandas DataFrame for bounded datasets; or
- a source-profile object for warehouse-scale pushdown profiling.

Future rule plugins should emit the same `Finding` model, allowing the CLI, exporters, HTML UI, and MCP server to remain decoupled from individual checks.
