# Day 02 — Stakeholder Analysis & Decision Requirements

**Date:** 2026-11-14  
**Status:** Completed (documentation/design review only)  
**Domain:** Fictional e-commerce marketplace  
**Source of requirements:** Simulated stakeholder interviews; no real interviews were conducted.

## 1. Problem statement

Commercial decisions are made using inconsistent operational reports. Revenue may be double counted across order items and payment attempts; retention and campaign performance lack stable definitions. AXIOM must turn raw transactional and event records into traceable metrics and actionable questions.

## 2. Stakeholder personas

| ID | Persona | Responsibility | Decisions | Primary metrics | Reporting cadence |
|---|---|---|---|---|---|
| ST-01 | General Manager | Business growth | Which revenue drivers need attention? | Net sales, orders, AOV, repeat rate | Weekly/monthly |
| ST-02 | Marketing Lead | Acquisition budgets | Which channels merit further spend? | Spend, attributed sales, CAC, ROAS | Weekly |
| ST-03 | Product Manager | Checkout experience | Which funnel stage loses sessions? | Step conversion, abandonment | Weekly |
| ST-04 | Finance Analyst | Transaction reconciliation | Are sales and refunds correctly reported? | Gross sales, refund value, net sales | Daily/monthly |
| ST-05 | Data Analyst | Metric quality | Can KPI results be reproduced and audited? | Completeness, duplicates, reconciliation | Daily |

## 3. Business decision questions

| ID | Decision owner | Business question | Metric / output | Required entities | Intended decision |
|---|---|---|---|---|---|
| BQ-01 | ST-01 | How are eligible sales changing month over month? | Monthly sales trend | orders, order_items | Prioritize growth investigations |
| BQ-02 | ST-04 | What is the impact of refunds on net sales? | Refund value and net sales reconciliation | orders, order_items, payments, refunds | Audit commercial reporting |
| BQ-03 | ST-01 | Which categories drive sales? | Sales by category | products, categories, order_items, orders | Review category strategy |
| BQ-04 | ST-01 | How does average order value vary by acquisition source? | AOV by source | customers, orders, order_items | Segment customer strategy |
| BQ-05 | ST-01 | Which customer cohorts return to purchase? | Monthly cohort retention | customers, orders | Evaluate retention initiatives |
| BQ-06 | ST-01 | What share of first-time customers reorder within 30 days? | 30-day repeat rate | customers, orders | Monitor repeat purchase |
| BQ-07 | ST-03 | Where do sessions drop out of the purchase funnel? | Stage-to-stage conversion | sessions, events, orders | Prioritize product fixes |
| BQ-08 | ST-02 | Which campaigns produce the highest attributed sales per spend? | Descriptive ROAS | campaigns, sessions, orders, order_items | Reallocate test budgets |
| BQ-09 | ST-02 | What is observed customer acquisition cost by campaign? | CAC | campaigns, sessions, customers | Compare acquisition efficiency |
| BQ-10 | ST-04 | Which segments show elevated cancellation/refund rates? | Rates by cohort/category | orders, refunds, order_items, products | Investigate operational risks |
| BQ-11 | ST-01 | Which customers have high frequency and monetary value? | RFM segments | customers, orders, order_items | Define retention experiments |
| BQ-12 | ST-05 | How much can missing or duplicated records distort KPIs? | DQ exception counts and reconciliation | all core tables | Prevent misleading decisions |

## 4. Prioritization

**Must have for MVP:** BQ-01, BQ-02, BQ-03, BQ-05, BQ-07, BQ-12.  
**Should have:** BQ-04, BQ-06, BQ-08, BQ-10.  
**Could have if time permits:** BQ-09, BQ-11.

## 5. Requirements traceability (initial)

| Requirement ID | Requirement | Business questions | Acceptance evidence |
|---|---|---|---|
| BR-01 | Standardized financial KPI definitions | BQ-01,02,03,04 | Metric dictionary, SQL reconciliation tests |
| BR-02 | Repeat purchase and cohort analysis | BQ-05,06 | Cohort SQL, fixture with expected counts |
| BR-03 | Session-level funnel reporting | BQ-07 | Defined event taxonomy, stage conversion query |
| BR-04 | Campaign attribution with disclosed assumptions | BQ-08,09 | Attribution spec and tested joins |
| BR-05 | Exception reporting and reproducibility | BQ-10,12 | DQ checks and validation log |
| BR-06 | Customer segmentation | BQ-11 | Documented RFM scoring rules and test cases |

## 6. Analyst scenarios

### Scenario A — Executive revenue review
**Given** the manager selects a reporting month, **when** the executive report runs, **then** it shows eligible order count, gross sales after discounts, refunds and net sales using a stated period convention. The totals must reconcile with source-level SQL.

### Scenario B — Marketing budget review
**Given** a marketing lead selects a campaign, **when** its performance is displayed, **then** spend, attributed orders, attributed sales and ROAS appear with an attribution window and warnings about observational rather than causal measurement.

### Scenario C — Checkout funnel diagnosis
**Given** the product manager selects a date range, **when** the funnel report runs, **then** sessions are counted once per stage, stage order is enforced, and missing or anonymous identities are handled explicitly.

### Scenario D — Finance audit
**Given** a period with partial refunds and repeated payment attempts, **when** net sales are calculated, **then** refunds are not double counted and payment attempts do not inflate revenue.

## 7. Open decisions for Day 03

1. What exactly qualifies as a completed/eligible order?
2. Which date determines period revenue when refunds arrive later?
3. How are marketing campaign spend and attribution windows represented?
4. What is the funnel event taxonomy and deduplication rule?
5. What are the expected performance and reproducibility targets?

## 8. Day 02 acceptance review

- [x] Five distinct simulated stakeholder roles (minimum three).
- [x] Twelve decision questions (minimum ten).
- [x] Each question has an owner, metric/output, required entities and intended decision.
- [x] Initial requirement IDs and prioritization.
- [x] Four concrete analyst scenarios.
- [x] Unresolved semantics explicitly deferred to Day 03.

**Validation:** Manual consistency review against PROJECT_CHARTER.md, DATA_MODEL.md and METRICS.md. No SQL runtime checks performed: database not implemented yet.
