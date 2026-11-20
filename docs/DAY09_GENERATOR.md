# Day 09 — Customer and Catalog Generator

**Status:** Python source and unit tests published. Local prototype tested (10/10); the exact published revision has not been executed in a GitHub CI runner. PostgreSQL import remains unverified.

## Run (Python 3.10+, standard library only)

From the repository root:

```bash
python -m unittest discover -s tests -v
python -m src.generator --validate-only
python -m src.generator --config config/synthetic_data.json --output data/generated
```

Expected CSV outputs: `categories.csv` (12 rows), `products.csv` (240 rows), `customers.csv` (10,000 rows), plus `manifest.json` with actual row counts, SHA-256 file hashes, seed, configuration hash and validation scope.

## Design and constraints

- Each entity has an independent deterministic RNG stream; IDs are sequential BIGINT-compatible values.
- Product category IDs resolve to existing categories; products have bounded nonnegative two-decimal prices and active flags.
- Customer region and acquisition source follow configuration weights; created_at lies within the observation window.
- CSV output is UTF-8, LF, with canonical headers, sorted IDs, and ISO-8601 UTC timestamps.
- The `--validate-only` mode checks generated records without writing files.
- All data is synthetic and contains no real names, contact details or customer PII.

## Test coverage

10 unit tests: counts, validation, deterministic output, seed variation, unique IDs, FK/price checks, identical CSV/manifest hashes, invalid probabilities, unknown config keys and duplicate IDs.

**Scope boundary:** Day 09 implements only customers and catalog. Campaigns, sessions, orders, payments, refunds and events are future days. The generated CSVs are not committed to the repository; they can be regenerated locally. Day 07 PostgreSQL migration acceptance remains pending independently.

## Evidence and limitations

A local development prototype passed 10 unit tests and generated 12/240/10,000 rows with repeatable SHA-256 hashes. The GitHub-published implementation follows the same approach but must still be executed in CI or on a checkout to establish evidence for its exact commit. No claim of successful PostgreSQL import is made.
