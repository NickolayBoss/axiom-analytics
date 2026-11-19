# Day 08 — Synthetic Data Generation Specification v1.0

**Roadmap date:** 2026-11-20 · **Authored:** 2026-11-19  
**Status:** Specification complete. Generators and generated datasets are scheduled for Days 09–11; **not yet implemented**.

## 1. Objective and reproducibility

Create a deterministic, entirely fictional e-commerce dataset matching [Data Dictionary](DATA_DICTIONARY.md) and [migration 001](../database/migrations/001_initial_schema.sql). The dataset supports sales, refunds, cohort, funnel, campaign and data-quality exercises without real personal data.

**Default configuration:** seed `20261120`, observation period `2025-01-01T00:00:00Z` to `2025-12-31T23:59:59Z`, report timezone UTC, currency CU, canonical UTF-8 CSV with LF newlines and ISO-8601 UTC timestamps. Record output is sorted by primary key; RNG streams are isolated per entity to prevent an unrelated entity-count change from reshuffling all downstream data. Same code version, config and seed must yield byte-identical files.

## 2. Baseline scale and relationships

| Entity | Baseline target | ID range (inclusive) | Grain / dependency |
|---|---:|---|---|
| categories | 12 | 1–12 | one category |
| products | 240 | 1–240 | 20 per category |
| customers | 10,000 | 1–10,000 | one customer |
| campaigns | 24 | 1–24 | two per month |
| orders | 40,000 | 1–40,000 | one checkout; customer FK |
| order_items | 80,000 approx. | 1 onward | 1–4 lines per order; product FK |
| payments | 45,000 approx. | 1 onward | 1–3 attempts per order |
| refunds | 2,000 approx. | 1 onward | zero or multiple per captured payment |
| sessions | 100,000 | 1–100,000 | anonymous or customer-linked |
| events | 250,000 approx. | 1 onward | ordered events within session |

Approximate counts are **targets, not observed outputs**. The generator must report actual counts in a manifest. No guarantee of exact 80k items/45k payments/250k events is made.

## 3. Proposed distributions

| Feature | Proposed rule | Purpose |
|---|---|---|
| Customer region | 50% North, 25% Central, 15% South, 10% West | Segmentation |
| Acquisition source | 30% organic, 25% paid_search, 20% social, 15% referral, 10% direct | Channel comparison |
| Product list price | Lognormal-like distribution clipped to [5, 1500] CU; rounded to 2 decimals | Long-tailed basket values |
| Order line count | 1: 40%, 2: 35%, 3: 20%, 4: 5% | Join multiplicity |
| Order status | completed: 78%, cancelled: 12%, expired: 6%, placed: 4% | Eligibility/cancellation |
| Discount | 70% zero; otherwise 5–25% of line gross, rounded down to cents | Promotion effect |
| Payment attempts | completed orders: one capture, optionally preceding 1–2 failed attempts; others: no capture | Reconciliation |
| Refund incidence | 5% of captured orders, with 1–2 partial settlements; capped at captured amount | Refund analytics |
| Anonymous sessions | 20% | Funnel denominator and attribution caveats |
| Campaign-linked sessions | 30%; only link sessions within campaign active dates | Campaign analysis |
| Session length | 1–90 minutes | Event bounds |
| Funnel stages | Conditional stage advancement; see funnel contract below | Drop-off analysis |
| Purchase events | Only for completed eligible orders linked to a session | Purchase reconciliation |

Percentages are modeling choices, **not empirical business statistics**. Sampling should use deterministic weighted choices and explicit rounding rules. Dates are UTC; no future events outside the observation window.

## 4. Temporal and financial contracts

- `customers.created_at <= orders.placed_at` for known buyers.
- `orders.placed_at <= payments.attempted_at`; captured payment amount equals sum of order-line `quantity * unit_price - discount_amount`.
- `refunds.requested_at >= payments.attempted_at`; settled refunds require `refunded_at >= requested_at`; total settled refunds per captured payment <= captured amount.
- `sessions.started_at < sessions.ended_at`; every event lies within inclusive session bounds.
- Session-based purchase events must reference an eligible completed order and a matching customer if the session is identified.
- Completed orders **without** a linked purchase event remain eligible for financial KPIs but are not counted as session funnel purchases; the generator should make this rate explicit in the manifest.
- Whole-campaign `spend` is generated once per campaign, nonnegative; do not invent daily spend from it.
- No customer names, addresses, emails, telephone numbers, or real identifiers are generated.

## 5. Funnel and campaign policy

Stage order: `session_start → product_view → add_to_cart → checkout_start → purchase`. Strictly increasing timestamps for valid advancement; duplicates of view/cart are permitted and should not inflate distinct session counts. Session `campaign_id` is the attribution candidate; an eligible purchase linked to a session is attributed only if the campaign is active on purchase date. Unattributed orders are valid.

**Modeling dependency:** A session may contain at most one purchase event in the baseline generator to simplify deterministic linkage. Multiple sessions may exist for a customer. No multi-touch or cross-device stitching.

## 6. Generation order

1. Read and validate config, initialize independent RNG streams.
2. Generate categories, products, customers, campaigns.
3. Generate sessions and assign eligible customer/campaign references.
4. Generate orders and items, with realistic placement times; assign optional purchase sessions with matching customer.
5. Generate payment attempts and captured payments for completed orders.
6. Generate refunds for captured payments.
7. Generate session events with strictly ordered funnel steps and valid order linkage.
8. Write CSVs in database dependency order and emit a manifest with SHA-256, counts, seed, config hash, generator version and validation summary.

**Implementation caveat:** Orders may be generated before sessions if the implementation first reserves session IDs and purchase linkage; the output must still satisfy every contract.

## 7. Acceptance criteria

- [ ] Same seed/config/code produces byte-identical CSV files.
- [ ] All ten tables have correct headers, types, unique primary keys and valid foreign keys.
- [ ] Every completed order has >=1 item and exactly one full captured payment; non-completed orders have no captured payment.
- [ ] Refund lifecycle and cumulative limits hold.
- [ ] Event ordering, session boundaries and purchase linkage hold.
- [ ] Counts and file hashes are recorded in a manifest.
- [ ] Intentional **invalid** fixtures are kept outside the canonical clean dataset.
- [ ] A clean PostgreSQL import and quality gate pass before claiming a working dataset.

These are future implementation gates; this document alone does not satisfy them.
