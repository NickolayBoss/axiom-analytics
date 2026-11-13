# Metric Dictionary — Draft v0.1

> **Status:** Proposed definitions. Confirm business rules and implement reconciliation tests before publishing results.

| Metric | Proposed definition | Grain / caveat |
|---|---|---|
| Gross merchandise value (GMV) | Sum of order item quantities × unit prices before discounts | Completed eligible orders; exclude canceled orders |
| Discount value | Sum of eligible line discounts | Same order cohort as GMV |
| Gross sales after discounts | GMV − discount value | Excludes tax/shipping unless later specified |
| Refund value | Sum of settled refund amounts | Refund-event date; partial refunds allowed |
| Net sales | Gross sales after discounts − refund value | Period convention must be explicit |
| Orders | Count distinct eligible completed orders | Never count order items as orders |
| Average order value (AOV) | Gross sales after discounts / eligible orders | Null if denominator is zero |
| Purchase conversion | Sessions with a completed purchase / eligible sessions | Session-level, defined attribution window |
| 30-day repeat purchase | Customers with a second eligible purchase within 30 days of first / first-time purchasers with full 30-day observation | Right-censor recent cohorts |
| Cohort retention | Customers active in cohort month N / customers in original cohort | Define active as eligible purchase |
| Refund rate | Refunded eligible orders / eligible completed orders | Order-based; separate amount-based rate |
| ROAS | Attributed gross sales after discounts / campaign spend | Descriptive, not incremental causal impact |
| CAC | Campaign spend / new customers attributed to campaign | Undefined if zero acquisitions |
| RFM | Recency, frequency and monetary value of eligible customer purchases | Snapshot date and scoring boundaries required |

## Time and reconciliation policy

- Use UTC timestamps in storage; define reporting timezone in each report.
- Do not mix order-date revenue with refund-date reductions without stating the convention.
- Provide both transaction-period and order-cohort views if necessary.
- Avoid duplication when joining orders, items, payments and events.
- Track missing campaign attribution separately, not as zero spend.
- Treat all conclusions as findings from **synthetic** data, not empirical market evidence.

## Metric review checklist

1. What is the unit of analysis (grain)?
2. What records are included/excluded?
3. Which timestamp defines the period?
4. What is the numerator and denominator?
5. What happens for nulls, duplicates, canceled orders and partial refunds?
6. Can the result be independently reconciled?
