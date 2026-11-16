# Day 05 — Data Dictionary v1.0

**Date:** 2026-11-17 (completed early 2026-11-16)  
**Status:** Approved design baseline, **not yet implemented in PostgreSQL**.  
**Database:** PostgreSQL; all IDs `BIGINT`, money `NUMERIC(14,2)`, timestamps `TIMESTAMPTZ` (UTC), calendar dates `DATE`.

## Field conventions

- `PK` = primary key, `FK` = foreign key, `NN` = NOT NULL, `UQ` = unique.
- All monetary amounts are fictional **CU**, non-negative unless explicitly specified.
- Each row represents exactly the stated grain. Generated IDs are stable within a seed.
- Business event times must be timezone-aware; reports explicitly state their timezone.
- Enums are proposed `TEXT` + `CHECK` constraints in the MVP schema.
- Derived metrics (e.g. line net sales) belong in SQL marts, not duplicated columns.

## 1. customers — one row per customer

| Field | Type | Rules | Meaning |
|---|---|---|---|
| customer_id | BIGINT | PK, NN | Stable synthetic customer ID |
| created_at | TIMESTAMPTZ | NN | Registration timestamp |
| region | VARCHAR(80) | NN | Fictional region label |
| acquisition_source | VARCHAR(40) | NN | Acquisition source; `organic`, `paid_search`, `social`, `referral`, `direct` |

## 2. categories — one row per category

| Field | Type | Rules | Meaning |
|---|---|---|---|
| category_id | BIGINT | PK, NN | Category ID |
| category_name | VARCHAR(100) | NN, UQ | Category display name |

## 3. products — one row per catalog product

| Field | Type | Rules | Meaning |
|---|---|---|---|
| product_id | BIGINT | PK, NN | Product ID |
| category_id | BIGINT | FK → categories, NN | Product category |
| product_name | VARCHAR(160) | NN | Product display name |
| list_price | NUMERIC(14,2) | NN, >= 0 | Current catalog price; historical orders use snapshot unit_price |
| active | BOOLEAN | NN, default TRUE | Whether currently offered |

## 4. orders — one row per checkout order

| Field | Type | Rules | Meaning |
|---|---|---|---|
| order_id | BIGINT | PK, NN | Order ID |
| customer_id | BIGINT | FK → customers, NN | Buyer |
| placed_at | TIMESTAMPTZ | NN | Order creation timestamp |
| status | VARCHAR(20) | NN; `placed`, `completed`, `cancelled`, `expired` | Operational order state |

## 5. order_items — one row per order line

| Field | Type | Rules | Meaning |
|---|---|---|---|
| order_item_id | BIGINT | PK, NN | Order line ID |
| order_id | BIGINT | FK → orders, NN | Parent order |
| product_id | BIGINT | FK → products, NN | Purchased product |
| quantity | INTEGER | NN, > 0 | Number of units |
| unit_price | NUMERIC(14,2) | NN, >= 0 | Unit price snapshot at purchase |
| discount_amount | NUMERIC(14,2) | NN, >= 0 and <= quantity × unit_price | Total line discount |

## 6. payments — one row per payment attempt

| Field | Type | Rules | Meaning |
|---|---|---|---|
| payment_id | BIGINT | PK, NN | Attempt ID |
| order_id | BIGINT | FK → orders, NN | Attempted order |
| attempted_at | TIMESTAMPTZ | NN | Attempt timestamp |
| amount | NUMERIC(14,2) | NN, > 0 | Attempted/captured amount |
| status | VARCHAR(20) | NN; `pending`, `failed`, `captured` | Settlement state |

**Cross-row invariant:** eligible completed orders have exactly one full captured payment; multiple failed attempts are allowed. Enforce with tests and an appropriate unique partial index where possible.

## 7. refunds — one row per refund request / settlement

| Field | Type | Rules | Meaning |
|---|---|---|---|
| refund_id | BIGINT | PK, NN | Refund event ID |
| payment_id | BIGINT | FK → payments, NN | Related payment attempt |
| requested_at | TIMESTAMPTZ | NN | Request timestamp |
| refunded_at | TIMESTAMPTZ | NULL unless settled; >= requested_at | Settlement timestamp |
| amount | NUMERIC(14,2) | NN, > 0 | Requested / settled amount |
| status | VARCHAR(20) | NN; `pending`, `failed`, `settled` | Refund lifecycle state |
| reason | VARCHAR(100) | NN | Synthetic refund reason |

**Invariant:** `settled` requires `refunded_at`; non-settled records must have `refunded_at IS NULL`. Sum of settled refunds per captured payment must not exceed captured amount; validate transactionally / via quality checks.

## 8. campaigns — one row per campaign

| Field | Type | Rules | Meaning |
|---|---|---|---|
| campaign_id | BIGINT | PK, NN | Campaign ID |
| campaign_name | VARCHAR(120) | NN | Campaign display name |
| channel | VARCHAR(40) | NN | Marketing channel |
| start_date | DATE | NN | Campaign start, inclusive |
| end_date | DATE | NN, >= start_date | Campaign end, inclusive |
| spend | NUMERIC(14,2) | NN, >= 0 | **Whole-campaign** spend, not daily spend |

## 9. sessions — one row per visit

| Field | Type | Rules | Meaning |
|---|---|---|---|
| session_id | BIGINT | PK, NN | Visit ID |
| customer_id | BIGINT | FK → customers, NULL allowed | Anonymous visits are supported |
| campaign_id | BIGINT | FK → campaigns, NULL allowed | Single-touch attribution candidate |
| started_at | TIMESTAMPTZ | NN | Visit start |
| ended_at | TIMESTAMPTZ | NN, > started_at | Visit end; generated explicitly |

**Session policy:** generator supplies `ended_at`; no implicit 30-minute timeout is assumed. Events must be within `[started_at, ended_at]`. This is a **synthetic session boundary**, not a production identity-stitching policy.

## 10. events — one row per behavioral event

| Field | Type | Rules | Meaning |
|---|---|---|---|
| event_id | BIGINT | PK, NN | Event ID |
| session_id | BIGINT | FK → sessions, NN | Parent visit |
| occurred_at | TIMESTAMPTZ | NN | Event timestamp within session |
| event_type | VARCHAR(30) | NN; `session_start`, `product_view`, `add_to_cart`, `checkout_start`, `purchase` | Funnel stage |
| order_id | BIGINT | FK → orders, nullable; NN for purchase | Associated order where applicable |
| product_id | BIGINT | FK → products, nullable | Product for view/cart events |

**Event policy:** `session_start` occurs at `sessions.started_at`; `purchase` references an eligible completed order. Events can repeat, but the funnel counts each session once per ordered stage.

## Referential dependency order

`categories → products`; `customers → orders → order_items`; `orders → payments → refunds`; `campaigns + customers → sessions → events`; `orders → events`.

Recommended load order: categories, products, customers, campaigns, orders, order_items, payments, refunds, sessions, events.

## Cross-table validation

| Rule ID | Invariant | Verification |
|---|---|---|
| DQ-F01 | Order items exist for each completed order | Anti-join query |
| DQ-F02 | Exactly one full captured payment per eligible completed order | Group by order_id and compare line net total |
| DQ-F03 | Settled refunds <= captured amount | Per-payment reconciliation |
| DQ-F04 | Event timestamp within session start/end | Join events to sessions |
| DQ-F05 | Purchase event order belongs to the session customer when known | Join session/order customer IDs |
| DQ-F06 | Purchase attribution uses active campaign on event date | Compare campaign date range |
| DQ-F07 | Event progression uses strictly increasing timestamps | Ordered funnel test fixtures |
| DQ-F08 | All money calculations use exact decimal arithmetic | SQL fixture assertions |

## Out of scope / unresolved

Partial captures, shipping, tax, multi-currency, daily campaign spend, late-arriving production events, cross-device identity stitching, and real payment integrations are excluded from the 30-day MVP. Actual database DDL and constraint enforcement are scheduled for Day 07.
