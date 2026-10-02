# Examples

Run `dataguard demo` to generate synthetic retail datasets locally. No employer or proprietary data is included.

Try:

```bash
dataguard demo --rows 5000
dataguard scan .dataguard-demo/customers.csv --json-out customers-report.json
dataguard contract .dataguard-demo/customers.csv --out customers-contract.yml
dataguard generate-dbt .dataguard-demo/customers.csv --out customers-schema.yml
```
