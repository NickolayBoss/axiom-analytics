# Day 06 — PostgreSQL Index Design

**Status:** Candidate indexes; performance is unmeasured until Day 21.

## Principles

Primary keys and UNIQUE constraints create indexes automatically. PostgreSQL does **not** automatically index the referencing side of a foreign key. Indexes below target join paths and filtering used by planned reports; avoid indexing every column indiscriminately.

| Candidate | Table(columns) | Query rationale | Priority |
|---|---|---|---|
| idx_orders_customer_placed | orders(customer_id, placed_at) | first/repeat purchase, cohorts | High |
| idx_orders_placed_status | orders(placed_at, status) | monthly eligible-order filters | High |
| idx_order_items_order | order_items(order_id) | order revenue aggregation | High |
| idx_order_items_product | order_items(product_id) | category/product sales | Medium |
| idx_payments_order | payments(order_id) | payment eligibility/reconciliation | High |
| uq_payments_captured_order | payments(order_id) WHERE status='captured' UNIQUE | at most one captured payment | High |
| idx_refunds_payment_settled | refunds(payment_id, refunded_at) WHERE status='settled' | settled refunds by payment and date | High |
| idx_sessions_customer_start | sessions(customer_id, started_at) | visit history | Medium |
| idx_sessions_campaign | sessions(campaign_id) | attribution joins | Medium |
| idx_events_session_time | events(session_id, occurred_at, event_id) | ordered funnel | High |
| idx_events_order | events(order_id) WHERE order_id IS NOT NULL | purchase-event linkage | Medium |
| idx_products_category | products(category_id) | category joins | Medium |

## Tradeoffs and verification

- Each index adds write and storage overhead; test before retaining.
- Compare `EXPLAIN (ANALYZE, BUFFERS)` with and without candidate indexes on a documented fixture.
- Small synthetic tables may favor sequential scans; this is not automatically a defect.
- Do not claim an optimization or measured speedup without actual execution evidence.
- The Day 07 schema should include integrity-critical unique indexes; optional performance indexes can be introduced selectively.
