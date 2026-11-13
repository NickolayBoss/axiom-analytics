# AXIOM Analytics — 30-Day Delivery Roadmap

**Period:** 2026-11-13 to 2026-12-12  
**Status:** Planning / Foundation  
**Cadence:** One independently verifiable deliverable per day.  
**Scope:** One coherent MVP, not a production deployment.

## Milestones

| Sprint | Days | Outcome | Acceptance criteria |
|---|---|---|---|
| 1 — Discovery & Design | 01–07 | Business specification and relational model | Documented requirements, metric definitions, ERD, initial DDL |
| 2 — Data & SQL | 08–14 | Reproducible sample dataset and SQL analyses | Seed pipeline, validation queries, tested reporting queries |
| 3 — Advanced Analytics | 15–21 | Retention, revenue and marketing investigations | Cohort/RFM/funnel analyses with explained assumptions |
| 4 — BI & Delivery | 22–30 | Dashboards, quality checks, reproducible demo | Dashboard exports, documented runbook, final case study |

## Daily delivery plan

| Day | Date | Deliverable | Definition of done |
|---|---|---|---|
| 01 | Nov 13 | Project charter, README, roadmap, documentation skeleton | Scope and milestones published |
| 02 | Nov 14 | Stakeholders, user personas and decision questions | At least 3 roles and 10 answerable questions |
| 03 | Nov 15 | Functional and non-functional requirements | Prioritized requirements with acceptance criteria |
| 04 | Nov 16 | Business processes and data flow | Mermaid context and ingestion diagrams |
| 05 | Nov 17 | Data dictionary v1 | Entities, fields, types, nullability and ownership |
| 06 | Nov 18 | ER diagram and relational design | Keys, relationships and cardinalities reviewed |
| 07 | Nov 19 | PostgreSQL DDL v1 | Schema applies cleanly to an empty database |
| 08 | Nov 20 | Synthetic data specification | Distributions, constraints, edge cases and seed |
| 09 | Nov 21 | Customer and catalog data generator | Deterministic records pass validation |
| 10 | Nov 22 | Order, item and payment generator | Referential integrity and status rules pass |
| 11 | Nov 23 | Marketing and event generator | Funnel events and attribution assumptions documented |
| 12 | Nov 24 | Data quality suite | Missing, duplicate, orphan and invalid-state checks |
| 13 | Nov 25 | SQL fundamentals casebook | Joins, aggregations and grouping tested |
| 14 | Nov 26 | Revenue and order KPI mart | Reconciled revenue, AOV and order counts |
| 15 | Nov 27 | Window functions and CTE casebook | Rankings, running totals, moving averages |
| 16 | Nov 28 | Customer retention analysis | Cohort definition and retention matrix |
| 17 | Nov 29 | RFM segmentation | Explicit scoring boundaries and validation |
| 18 | Nov 30 | Sales funnel analysis | Defined stages, deduplication and conversion |
| 19 | Dec 01 | Marketing efficiency analysis | CAC/ROAS with caveats for attribution |
| 20 | Dec 02 | Cancellation and refund investigation | Root-cause hypotheses and segment comparisons |
| 21 | Dec 03 | SQL optimization lab | EXPLAIN ANALYZE before/after evidence |
| 22 | Dec 04 | Analytics marts | Reusable documented views/materialized views |
| 23 | Dec 05 | Python ETL and orchestration script | Idempotent local execution |
| 24 | Dec 06 | Automated SQL/Python checks | Repeatable tests and failure messages |
| 25 | Dec 07 | Executive dashboard | Revenue, orders, AOV and trend filters |
| 26 | Dec 08 | Customer dashboard | Cohorts, retention and segments |
| 27 | Dec 09 | Marketing dashboard | Funnel and campaign performance |
| 28 | Dec 10 | Business case report | Problem, methodology, findings, recommendations |
| 29 | Dec 11 | Docker/runbook and clean-room test | New user can reproduce results from instructions |
| 30 | Dec 12 | Portfolio release v1.0 | Screenshots, limitations, demo walkthrough and retrospective |

## Working agreement

- Each day: issue → implementation → verification → documentation → meaningful commit.
- Record actual progress in `docs/PROGRESS.md`; never mark planned work as complete.
- SQL is reviewed for correctness, edge cases, readability and performance.
- Synthetic data is clearly labeled; no fabricated claims about real companies.
- If a task overruns, preserve quality and move unfinished work to backlog.
- Prefer one complete end-to-end scenario over many unfinished features.

## Release gates

**Gate A (Day 7):** documented business questions and executable DDL.  
**Gate B (Day 14):** reproducible data and validated core KPIs.  
**Gate C (Day 21):** analytical cases with transparent assumptions.  
**Gate D (Day 30):** reproducible demonstration and portfolio-grade case study.
