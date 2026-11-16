# Relational Constraints — Implementation Contract

**Status:** Day 06 design; DDL and runtime assertions pending Day 07.

| Table | Primary key | Foreign keys | CHECK / UNIQUE |
|---|---|---|---|
| customers | customer_id | — | acquisition_source enum; nonempty region |
| categories | category_id | — | category_name UNIQUE and nonempty |
| products | product_id | category_id → categories | list_price >= 0; nonempty product_name |
| orders | order_id | customer_id → customers | status enum |
| order_items | order_item_id | order_id → orders; product_id → products | quantity > 0; unit_price >= 0; discount_amount between 0 and quantity × unit_price |
| payments | payment_id | order_id → orders | amount > 0; status enum; unique captured payment per order (partial index) |
| refunds | refund_id | payment_id → payments | amount > 0; status enum; settled iff refunded_at IS NOT NULL; refunded_at >= requested_at |
| campaigns | campaign_id | — | spend >= 0; end_date >= start_date; nonempty name/channel |
| sessions | session_id | customer_id → customers nullable; campaign_id → campaigns nullable | ended_at > started_at |
| events | event_id | session_id → sessions; order_id → orders nullable; product_id → products nullable | event_type enum; purchase requires order_id; view/cart requires product_id |

## PostgreSQL implementation notes

- Use `NUMERIC(14,2)` for monetary columns; `TIMESTAMPTZ` for instants.
- Prefer explicit constraint names such as `chk_refunds_settlement_timestamp` and `fk_events_session`.
- Use `CREATE UNIQUE INDEX ... ON payments(order_id) WHERE status = 'captured'` for at-most-one capture.
- `CHECK` constraints cannot contain subqueries in PostgreSQL. Cross-row and cross-table rules belong in a separate validation suite or transactional application logic.
- FK constraints do not ensure completed orders have children; this requires explicit verification.
- Choose `ON DELETE RESTRICT` / default `NO ACTION` for financial records; do not cascade-delete transaction history.

## Negative fixtures to implement

1. Zero quantity; negative unit price; excessive discount.
2. Invalid order or refund status.
3. Missing parent FK.
4. Second captured payment for same order.
5. Settled refund without refunded_at; pending refund with refunded_at.
6. Campaign end before start.
7. Session end before start.
8. Purchase event without order_id.
9. Refund sum above captured amount (cross-row check).
10. Event timestamp outside session (cross-table check).

These are **planned tests**, not executed results.
