# Day 06 — Relational Design Review

**Planned:** 2026-11-18 · **Completed:** 2026-11-16 · **Scope:** ten proposed PostgreSQL tables. **No database has been deployed.**

## Cardinality review

| Parent → child | Parent cardinality per child | Child cardinality per parent | FK nullable? | Enforcement |
|---|---|---|---|---|
| categories → products | exactly 1 | 0..N | no | FK |
| customers → orders | exactly 1 | 0..N | no | FK |
| orders → order_items | exactly 1 | 0..N physically; >=1 for eligible orders | no | FK + quality check |
| products → order_items | exactly 1 | 0..N | no | FK |
| orders → payments | exactly 1 | 0..N | no | FK |
| payments → refunds | exactly 1 | 0..N | no | FK |
| customers → sessions | 0..1 | 0..N | yes | FK |
| campaigns → sessions | 0..1 | 0..N | yes | FK |
| sessions → events | exactly 1 | 0..N physically; start event required for funnel | no | FK + quality check |
| orders → events | 0..1 | 0..N | yes except purchase | FK + CHECK + quality check |
| products → events | 0..1 | 0..N | yes | FK |

**Correction:** An optional FK on the child does not mean a customer/campaign can have at most one session. Each customer or campaign can be referenced by many sessions; a session can be anonymous/unattributed.

## Normalization assessment

- Tables are designed around a single entity grain with atomic attributes (1NF).
- All tables have single-column surrogate primary keys; no partial-key dependencies (2NF).
- Category names live in `categories`, not `products`; customer source lives in `customers`; no intentional transitive dependencies in operational tables (3NF intent).
- `order_items.unit_price` is an intentional **historical transaction snapshot**, not a duplicate of current `products.list_price`.
- `sessions.campaign_id` is the single-touch candidate, not a copy of campaign attributes.
- Aggregated sales and refunds are computed in reporting marts, not stored redundantly in orders.

## Invariants and enforcement boundary

| Invariant | DB-level mechanism | Additional check required |
|---|---|---|
| IDs unique and present | PRIMARY KEY | no |
| Referenced parent exists | FOREIGN KEY | no |
| Valid enum/status | CHECK | no |
| Non-negative price, positive quantity | CHECK | no |
| Discount <= quantity × unit price | CHECK | no |
| Settled refund requires refunded_at | CHECK | no |
| Campaign end >= start | CHECK | no |
| Session end > start | CHECK | no |
| At most one captured payment per order | UNIQUE partial index | no |
| Eligible completed order has items and exactly one matching full capture | not expressible as simple row CHECK | yes |
| Cumulative refunds <= captured amount | multi-row aggregation | yes; transactional guard for concurrent writes |
| Event within session timestamps | cross-table comparison | yes |
| Purchase event order belongs to session customer | cross-table comparison | yes |
| Active campaign at purchase time | cross-table comparison | yes |
| Strictly ordered funnel | query/window logic | yes |

## Design risks

1. **Payment state consistency:** order marked completed without captured payment is invalid for analytics; reject via quality gate.
2. **Double counting:** never join multiple order_items, payments and refunds directly before independent aggregation.
3. **Concurrent refunds:** batch-level quality checks alone cannot prevent over-refunds under concurrent writes; a production system needs a transactional lock or equivalent enforcement. MVP is offline synthetic data.
4. **Timestamp semantics:** session events must lie within explicit boundaries; same-timestamp funnel stages do not advance.
5. **Reporting grain:** distinguish per-order, per-item, per-payment and per-session metrics.

## Day 07 handoff

Implement the ten-table DDL in dependency order, plus constraints and indexes described in [constraint matrix](CONSTRAINT_MATRIX.md). Confirm a clean PostgreSQL build and run negative fixtures. Keep cross-table quality checks separate from row-level SQL constraints.

**Review status:** design-level review complete; PostgreSQL execution pending.
