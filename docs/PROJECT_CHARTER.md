# Project Charter

## Executive summary

AXIOM Analytics is a portfolio-grade, locally reproducible business intelligence solution for a **fictional e-commerce marketplace**. It demonstrates requirements analysis, relational modeling, PostgreSQL analytics, Python data pipelines, data quality, performance engineering and decision-oriented reporting.

## Business problem

A fictional commerce team cannot reliably answer which products drive net revenue, which customer cohorts return, where the purchase funnel loses users, or whether marketing spend produces profitable acquisition. Operational records are fragmented and metric definitions are inconsistent.

## Objectives

1. Define a single, testable vocabulary of commercial metrics.
2. Model customers, products, orders, payments, refunds, campaigns and behavioral events.
3. Generate deterministic, realistic-looking **synthetic** data.
4. Build auditable SQL analyses and reusable reporting marts.
5. Present decision-ready findings with limitations and supporting queries.
6. Make the demonstration reproducible on a clean local machine.

## Stakeholders (simulated)

| Stakeholder | Key decisions |
|---|---|
| CEO / General Manager | Revenue growth, customer retention, business risks |
| Head of Marketing | Campaign allocation, acquisition effectiveness |
| Product Manager | Funnel bottlenecks and checkout improvements |
| Finance Analyst | Gross/net sales reconciliation, refunds |
| Data Analyst | Metric definitions, queries, data quality |

## Scope

**In:** PostgreSQL schema; Python synthetic generator; local ETL; SQL analyses; data quality tests; BI dashboards; architecture and requirements documents; Docker-based reproducibility.

**Out:** Real customer data; payment processing; production-grade authentication; live integrations; machine learning predictions; claims of real commercial impact.

## Decision questions

1. How do gross sales, refunds and net sales change by month?
2. Which categories and products contribute most to revenue?
3. What proportion of customers return within 30/60/90 days?
4. Which acquisition cohorts have the strongest retention?
5. At which stage does the purchase funnel lose the most sessions?
6. How do cancellation and refund rates vary by segment?
7. Which campaigns have the best observed return on ad spend?
8. How does average order value vary by acquisition source?
9. Which customers belong to actionable RFM segments?
10. Which metric changes are explained by data-quality issues?

## Acceptance criteria

- The database can be recreated from versioned SQL scripts.
- Synthetic data generation is deterministic with a fixed seed.
- Every reported metric has an explicit numerator, denominator, grain and filters.
- Core metrics reconcile to the underlying transactions.
- Referential integrity and important business rules have automated checks.
- At least three BI dashboards are reproducible.
- Each analytical case links to its query and explains business implications.
- Documentation distinguishes implemented functionality from planned functionality.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Unrealistic synthetic data | Document generation assumptions and inject controlled anomalies |
| Ambiguous revenue | Maintain a metric dictionary and reconciliation checks |
| Scope creep | Prioritize a working vertical slice and defer optional features |
| Unverifiable dashboard results | Store source queries and validation cases |
| Misleading marketing attribution | Label assumptions; do not infer causality from correlations |
| Unmanageable data volume | Start small, scale only for performance experiments |

## Success

Success is not commit volume. It is a reviewer being able to clone the repository, understand the problem, reproduce the data, execute the SQL, inspect results, and assess the quality of analytical reasoning.
