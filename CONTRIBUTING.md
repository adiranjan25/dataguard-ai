# Contributing to DataGuard AI

Thank you for contributing.

## Development setup

Python 3.10 or newer is required.

```bash
git clone <your-fork>
cd dataguard-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests
```

## Contribution ideas

- new deterministic data-quality rules;
- PII detectors with tests and documented false-positive tradeoffs;
- database adapters;
- dbt/Great Expectations/OpenMetadata/DataHub integrations;
- synthetic domain demos;
- documentation and reproducible benchmarks.

## Pull requests

1. Open an issue for substantial features.
2. Keep changes focused.
3. Add or update tests.
4. Do not include proprietary datasets, secrets, or employer-confidential material.
5. Explain behavior changes and any privacy/security implications.

By contributing, you agree that your contribution is licensed under Apache-2.0.
