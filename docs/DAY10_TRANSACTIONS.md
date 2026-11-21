# Day 10 — Order, Item and Payment Generator

**Status:** Implementation published; GitHub Actions execution outcome not yet independently confirmed.

## Scope

The generator now emits six deterministic CSV tables: `categories`, `products`, `customers`, `orders`, `order_items`, `payments`. Default configuration creates 40,000 orders, 1–4 order items per order, and one fully captured payment per completed order. Failed attempts can precede a successful capture; cancelled, expired and placed orders never receive captured payments.

### Financial conventions

- `line_gross = quantity * unit_price`.
- `line_net = line_gross - discount_amount`.
- `order_total = SUM(line_net)`, using `Decimal` and two fractional digits.
- Every completed order has exactly one captured payment equal to its order total.
- A non-completed order cannot have a captured payment.
- Payment attempts occur after order placement; orders occur no earlier than customer creation.
- All IDs are stable, sequential and foreign-key compatible.
- Source data is entirely fictional. Refunds, campaigns, sessions and events are scheduled for later days.

## Run

```bash
python -m unittest discover -s tests -v
python -m src.generator --validate-only
python -m src.generator --output data/generated
```

The output directory contains six CSV files plus `manifest.json` with actual counts and SHA-256 hashes. Two runs with the same configuration should produce identical outputs.

## Verification and limitations

The repository includes unit tests for captured-payment reconciliation, invalid foreign keys, status violations, deterministic generation and CSV hashes. GitHub Actions runs these tests across Python 3.10–3.12.

**Do not claim a passing CI run without inspecting its result.** PostgreSQL import of all six generated CSVs is not yet implemented in this stage. Approximate item/payment targets are not fixed row-count promises.

## Next

Day 11 adds campaigns, sessions and funnel events. Day 12 adds comprehensive data-quality tests and PostgreSQL import validation.
