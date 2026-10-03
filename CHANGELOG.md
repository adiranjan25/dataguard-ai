# Changelog

## 0.2.1
- Fixed built-in identifier uniqueness detection so `_id` columns such as `customer_id` and `store_id` are not automatically treated as primary-key-like identifiers.
- Kept automatic uniqueness heuristics for generic `id` columns while allowing explicit uniqueness requirements through YAML rules.
- Added regression tests for repeated foreign-key-like identifier columns and explicit uniqueness rules.
- Updated package and generated report version metadata to 0.2.1.
- Updated installation documentation for the public PyPI package.
- Published DataGuard AI 0.2.1 to PyPI.

## 0.2.0
- configurable YAML rule engine: not-null, unique, accepted-values, ranges, regex, max-null %, row-count range
- DuckDB table adapter
- PostgreSQL table adapter via SQLAlchemy/psycopg
- standalone responsive HTML quality/governance report
- Great Expectations portable expectation export
- ready-to-copy GitHub Actions data-quality workflow
- additional integration/unit tests
- sample CI dataset/config

## 0.1.0
- initial scanner, PII detection, scores, drift, contracts, dbt export, demo, JSON, optional AI explanation
