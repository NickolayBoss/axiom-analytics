# Day 03 — System Requirements Specification (SRS)

**Baseline:** v0.1 · **Date:** 2026-11-15 · **Status:** Proposed requirements approved for implementation planning; not implemented.

## 1. Purpose and boundaries

AXIOM is a local, reproducible analytical solution for a fictional online retailer. It ingests generated records, validates them, computes governed metrics and presents results to business stakeholders. It does not process live payments, personal customer information or production traffic.

**Actors:** General Manager (ST-01), Marketing Lead (ST-02), Product Manager (ST-03), Finance Analyst (ST-04), Data Analyst (ST-05). Personas are simulated, not interviewed.

## 2. Functional requirements

| ID | Priority | Requirement | Source | Acceptance evidence |
|---|---|---|---|---|
| FR-01 | Must | Define normalized customer, catalog, order, payment, refund, campaign and event entities with keys | BR-01, BR-03, BR-04 | Schema creation + FK checks |
| FR-02 | Must | Generate reproducible synthetic records from a configurable seed | BR-05 | Same seed produces same canonical dataset hashes |
| FR-03 | Must | Load records into PostgreSQL without creating duplicates on rerun | BR-05 | Second load leaves row counts and keys unchanged |
| FR-04 | Must | Reject invalid quantities, negative prices and broken references | BR-05 | Negative fixture tests fail predictably |
| FR-05 | Must | Calculate eligible order count, GMV, discounts, gross sales and AOV | BR-01, BQ-01,03,04 | Reconcile line-level fixture totals |
| FR-06 | Must | Reconcile settled refunds and net sales without multiplying order rows | BR-01, BQ-02 | Multi-attempt and partial-refund fixtures |
| FR-07 | Must | Produce monthly sales and category contribution analyses | BQ-01,03 | Deterministic expected aggregates |
| FR-08 | Must | Produce cohort retention and 30-day repeat purchase metrics | BR-02, BQ-05,06 | Mature-cohort and censoring tests |
| FR-09 | Must | Produce ordered session funnel with stage deduplication | BR-03, BQ-07 | Repeated/out-of-order event fixtures |
| FR-10 | Must | Surface missing data, duplicates and broken financial reconciliation | BR-05, BQ-12 | Quality report with exception counts |
| FR-11 | Should | Attribute orders to campaigns using a disclosed deterministic rule | BR-04, BQ-08,09 | Missing/ambiguous attribution fixtures |
| FR-12 | Should | Report campaign spend, descriptive ROAS and CAC | BR-04, BQ-08,09 | Zero-spend and zero-acquisition tests |
| FR-13 | Should | Analyze cancellation and refund rates by segment | BR-05, BQ-10 | Independent denominators and source reconciliation |
| FR-14 | Could | Compute RFM customer segments with documented thresholds | BR-06, BQ-11 | Snapshot-date boundary tests |
| FR-15 | Must | Expose at least three documented dashboards | BQ-01,05,07 | Screenshot and source-query reconciliation |
| FR-16 | Must | Provide documented local setup and clean rebuild | BR-05 | Clean-checkout runbook execution |

## 3. Non-functional requirements

| ID | Category | Requirement / target | Verification |
|---|---|---|---|
| NFR-01 | Reproducibility | Same configuration and seed yield identical generated business records | Compare canonical hashes across two runs |
| NFR-02 | Data integrity | All mandatory FK and CHECK constraints hold after loading | Automated SQL assertions |
| NFR-03 | Financial correctness | Monetary values use NUMERIC; reconciled totals agree to 0.01 currency unit | Fixture reconciliation |
| NFR-04 | Observability | Pipeline emits per-table counts and explicit error messages | Inspect sample success/failure logs |
| NFR-05 | Performance | Target: core KPI queries complete within 5s on a documented 100k-order local fixture | EXPLAIN ANALYZE and machine/spec disclosure |
| NFR-06 | Portability | Rebuild on documented Docker Compose environment | Clean-checkout test |
| NFR-07 | Maintainability | Versioned schema, named SQL queries, tests and documented metric definitions | Repository review |
| NFR-08 | Privacy | No real personal data, secrets or production credentials committed | Content review and gitignore |
| NFR-09 | Usability | Dashboard labels specify units, period and filters | Screenshot review |
| NFR-10 | Traceability | Every released dashboard KPI links to SQL and a metric definition | Traceability audit |

Performance figures are **targets, not achieved measurements**.

## 4. Business rules baseline

- **BRULE-01 — Eligible order:** order status `completed`, at least one valid item, and exactly one successful captured payment for the full discounted item total. Failed attempts do not count.
- **BRULE-02 — Amounts:** `line_gross = quantity * unit_price`; `line_net = line_gross - discount_amount`; taxes and shipping are out of scope.
- **BRULE-03 — Refund:** only settled refund events count. Sum of settled refunds on a captured payment must not exceed its captured amount. Multiple partial refunds are allowed.
- **BRULE-04 — Period accounting:** order-based sales are grouped by `placed_at` for completed eligible orders; refund events by `refunded_at`. The combined calendar-period net-sales series subtracts refunds settled during that period, including refunds of older orders.
- **BRULE-05 — Retention:** cohort is the month of the first eligible purchase; returning activity means another eligible purchase. Exclude immature 30-day cohorts from the repeat-rate denominator.
- **BRULE-06 — Funnel:** eligible session events progress `session_start → product_view → add_to_cart → checkout_start → purchase`. Count a session once at each reached stage and enforce chronological order.
- **BRULE-07 — Attribution:** for MVP, a completed order may be attributed to the campaign on the session containing its purchase event, if the event is within the session and the campaign is active; otherwise attribution is `unattributed`. This is a descriptive rule, not causal inference.
- **BRULE-08 — Marketing spend:** campaigns initially store total spend and start/end dates; period ROAS is not valid without a spend allocation policy. Whole-campaign comparisons only until daily spend is modeled.
- **BRULE-09 — Currency/time:** one fictional currency unit (CU), fixed precision `NUMERIC(14,2)`; UTC timestamps; report timezone stated.
- **BRULE-10 — Refund rate:** order-based rate uses eligible completed orders as denominator and orders with at least one settled refund as numerator.

## 5. Traceability and delivery

All FR and NFR IDs are proposals until tested. See [stakeholder questions](STAKEHOLDER_REQUIREMENTS.md), [metric dictionary](METRICS.md) and [acceptance test matrix](ACCEPTANCE_TESTS.md). Day 04 will document processes and event flows. Day 07 will implement the first database schema.

## 6. Outstanding design questions

- How to handle partially captured payments (excluded from MVP)?
- Whether to represent payment reversals separately from refunds (deferred)?
- How to handle cross-session purchases and multi-touch attribution (deferred)?
- How to handle currency conversions and shipping (out of scope)?
