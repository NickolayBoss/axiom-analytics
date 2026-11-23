# Day 12 — Refunds and data-quality gates

## Scope

The synthetic generator now produces **all ten PostgreSQL entities**, including `refunds`. Each run uses an independent seed stream (`seed:809`) and generates a reproducible subset of captured payments as refunds.

- Only captured payments can be refunded.
- `settled` refunds have `refunded_at >= requested_at`; pending and failed refunds have no settlement timestamp.
- Every refund amount is positive and capped by the captured payment.
- The cumulative settled amount for any payment cannot exceed its captured amount.
- Requests and settlements are inside the observation period.
- Amounts are represented using `Decimal` with two fractional digits.
- Refund count is stochastic and approximate, not a fixed target.

## Commands

```bash
python -m unittest discover -s tests -v
python -m src.generator --validate-only
python -m src.generator --output data/generated
```

Run a programmatic quality report:

```python
from pathlib import Path
from src.generator import parse_config, generate, validate
from src.refund_quality import quality_report

config, _ = parse_config(Path("config/synthetic_data.json"))
rows = generate(config)
validate(rows, config)
print(quality_report(rows, config))
```

The output directory includes ten CSV files and a manifest with exact counts and SHA-256 hashes. The `quality_report` validates transaction reconciliation, funnel references and ordering, refund status, refund caps, and table counts.

## Acceptance status

**Published:** generator source, regression tests and updated manual-only CI. **Not yet independently verified:** a green CI run on this revision, real CSV imports into PostgreSQL, and SQL quality-gate results against the generated dataset. The Day 12 issue remains open until these are verified.

The workflow remains `workflow_dispatch` only, on a single Python 3.12 job, to avoid email spam from every commit. The Python tests and SQL database constraints serve complementary purposes; in-memory validation is not a substitute for a clean PostgreSQL import.

## Next

Day 13: SQL fundamentals, reproducible analytical queries and validation of the ten-table dataset.
