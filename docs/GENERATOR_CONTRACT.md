# Day 08 — Generator Interface and Output Contract

**Status:** API design, not implemented. Target implementation: Days 09–11.

## Proposed CLI

```bash
python -m src.generator --config config/synthetic_data.json --output data/generated
python -m src.generator --config config/synthetic_data.json --output data/generated --validate-only
```

These commands describe the **planned** interface; they do not currently run.

## Configuration

See [config/synthetic_data.json](../config/synthetic_data.json) for seed, observation window, row targets, rates and currency. Validate all probabilities in [0,1], positive entity counts, `start < end`, and refund-rate limits. Refuse unknown keys rather than silently ignoring typos.

## Output layout

```text
data/generated/
  categories.csv
  products.csv
  customers.csv
  campaigns.csv
  orders.csv
  order_items.csv
  payments.csv
  refunds.csv
  sessions.csv
  events.csv
  manifest.json
```

Each CSV must have one header row using canonical column names from [DATA_DICTIONARY.md](DATA_DICTIONARY.md), UTF-8 encoding, LF line endings, stable primary-key sorting, ISO-8601 UTC timestamp text, and decimal amounts formatted to two fractional digits. Use an empty field for SQL NULL, not literal `None`.

## Manifest example (illustrative only)

```json
{
  "generator_version": "0.1.0",
  "seed": 20261120,
  "currency": "CU",
  "observation_start": "2025-01-01T00:00:00Z",
  "observation_end": "2025-12-31T23:59:59Z",
  "config_sha256": "<computed at runtime>",
  "files": {
    "customers.csv": {
      "rows": "<actual count>",
      "sha256": "<computed at runtime>"
    }
  },
  "validation": {
    "status": "not_run_in_this_example"
  }
}
```

Placeholders above are not actual file hashes or test results.

## Quality gates

1. Schema: headers, types, nullability, unique PK.
2. Referential integrity: every non-null FK resolves.
3. Business logic: order/payment matching, refunds <= capture, timestamps and attribution.
4. Reproducibility: regenerate in a fresh directory and compare hashes.
5. PostgreSQL: import on a disposable database and run quality-gate SQL.

Do not report a generator as working until all gates have execution evidence. No real PII or secrets are allowed in output.
