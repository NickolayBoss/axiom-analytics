# Delivery Log

## Current status

**Phase:** Days 01–14 source published; Day 11–14 runtime acceptance pending  
**Project start:** 2026-11-13  
**Target portfolio release:** 2026-12-12  
**Next:** Verify PostgreSQL import and revenue reconciliation; Day 15 window functions and CTEs

## Completed / verified

- [x] GitHub repository created and publicly accessible.
- [x] Initial project scope and 30-day delivery plan published.
- [x] Target architecture, initial data model and metric definitions documented.
- [x] Day 02: five simulated stakeholder personas, twelve business questions and four scenarios published.
- [x] Day 03: sixteen functional and ten non-functional requirements, twenty planned acceptance tests, five use cases and ADR-005 published.
- [x] Day 04: four BPMN-inspired Mermaid process diagrams, DFD-0/DFD-1, event taxonomy, failure routing and ADR-006 published.
- [x] Day 05: canonical field-level dictionary for ten entities, updated relational model and ingestion contracts.
- [x] Day 06: cardinality and normalization review, constraint matrix, index candidates and ADR-007.

## Not yet implemented

- [x] PostgreSQL DDL source and migration published (runtime verification pending)
- [x] Day 08 synthetic data specification, edge-case catalog, generator contract and JSON configuration published
- [x] Day 09 generator Python source, unit tests, CI workflow and usage guide published (green CI status shown in user screenshot; job logs not independently reviewed)
- [x] Day 10 orders, order_items and payments generator code, unit tests and CI workflow published (runtime CI result pending)
- [x] Day 11 campaigns, sessions and ordered funnel events published (CI outcome pending)
- [x] Day 12 refunds and Python quality gates published; CI and PostgreSQL import not yet verified
- [ ] Python ingestion pipeline
- [ ] SQL analytical cases
- [x] Python in-memory financial and referential quality checks published (runtime verification pending)
- [ ] PostgreSQL-backed end-to-end data quality checks
- [ ] BI dashboards
- [ ] Reproducible local deployment
- [ ] Final analytical report

## Daily journal

### Day 01 — 2026-11-13
**Goal:** Establish the scope, roadmap and documentation baseline.  
**Artifacts:** README.md, PROJECT_CHARTER.md, ROADMAP.md, ARCHITECTURE.md, DATA_MODEL.md, METRICS.md, quality and contribution standards.  
**Validation:** Published GitHub files were read back and confirmed.  
**Limitations:** No executable database or dashboards yet.

### Day 02 — 2026-11-14
**Goal:** Translate the business problem into stakeholder needs and measurable questions.  
**Artifacts:** [STAKEHOLDER_REQUIREMENTS.md](STAKEHOLDER_REQUIREMENTS.md).  
**Validation:** Five roles, twelve questions, six initial requirements and four scenarios documented.

### Day 03 — 2026-11-15
**Goal:** Formalize testable system requirements and freeze MVP business semantics.  
**Artifacts:** [REQUIREMENTS.md](REQUIREMENTS.md), [ACCEPTANCE_TESTS.md](ACCEPTANCE_TESTS.md), [USE_CASES.md](USE_CASES.md), [ADR-005](ADR/005-mvp-business-rules.md).  
**Validation:** GitHub publication verified; runtime tests not executed.

### Day 04 — 2026-11-16 (completed early 2026-11-15)
**Goal:** Describe order, refund, analytics and attribution processes and source-to-report data flows.  
**Artifacts:** [PROCESSES.md](PROCESSES.md), [DATA_FLOWS.md](DATA_FLOWS.md), [EVENT_TAXONOMY.md](EVENT_TAXONOMY.md), [ADR-006](ADR/006-quality-gated-analytics.md).  
**Validation:** Documentation consistency reviewed and files read back from GitHub. Mermaid source written; rendered diagrams not visually verified. No pipeline execution or database tests performed.  
**Key decisions:** Quality-gated publication, session-based ordered funnel, explicit error codes and attribution limitations.  
**Open questions:** Refund status field missing in original data model; session timeout and late-arriving events; daily spend granularity.  
**Next step:** Resolve field-level contracts in Day 05 data dictionary.

### Day 05 — 2026-11-17 (completed early 2026-11-16)
**Goal:** Define field-level types, nullability, keys, enums, money rules and cross-table invariants.
**Artifacts:** [DATA_DICTIONARY.md](DATA_DICTIONARY.md), [DATA_MODEL.md](DATA_MODEL.md), [DATA_FLOWS.md](DATA_FLOWS.md).
**Validation:** GitHub files published and read back. Documentation-only checks; PostgreSQL schema not yet implemented.
**Decisions:** Refund lifecycle status added; explicit session end; campaign spend whole-campaign; currency CU.
**Next:** Review ER cardinalities on Day 06, implement DDL on Day 07.

### Day 06 — 2026-11-18 (completed early 2026-11-16)
**Goal:** Review ten-entity relational design, cardinality, normalization, integrity boundaries and indexes.
**Artifacts:** [RELATIONAL_DESIGN_REVIEW.md](RELATIONAL_DESIGN_REVIEW.md), [CONSTRAINT_MATRIX.md](CONSTRAINT_MATRIX.md), [INDEX_STRATEGY.md](INDEX_STRATEGY.md), [ADR-007](ADR/007-relational-integrity-boundaries.md).
**Validation:** Source documents reviewed for consistency and GitHub file publication checked. No PostgreSQL execution or measured index benchmarks.
**Decisions:** FK/CHECK/partial unique index for local integrity; cross-table invariants in quality suite.
**Next:** Day 07 executable DDL, clean build and negative fixture tests.

### Day 07 — 2026-11-18 (implementation published; acceptance gate open)
**Goal:** Build PostgreSQL DDL v1 and executable verification fixtures.
**Artifacts:** [migration](../database/migrations/001_initial_schema.sql), [constraint fixtures](../database/tests/001_constraints.sql), [quality gate SQL](../database/tests/002_quality_gate.sql), [test runner](../database/tests/run_constraints.sh), [setup guide](POSTGRESQL_SETUP.md).
**Verification:** GitHub publication and file read-back; local PostgreSQL execution unavailable (psql/server/Docker absent). Migration and fixtures **not executed**, so clean-schema acceptance criterion remains unverified.
**Decisions:** 10 tables; local CHECK/FK constraints; partial unique captured-payment index; 13 expected negative fixtures; cross-table quality queries separate.
**Open:** Run migration and tests on a PostgreSQL-equipped machine before closing Issue #6.
**Next:** Day 08 synthetic data specification after runtime gate is satisfied.

### Day 08 — 2026-11-20 (completed early 2026-11-19)
**Goal:** Specify a reproducible synthetic e-commerce dataset, distributions, edge cases and generator interface.
**Artifacts:** [SYNTHETIC_DATA_SPEC.md](SYNTHETIC_DATA_SPEC.md), [SYNTHETIC_EDGE_CASES.md](SYNTHETIC_EDGE_CASES.md), [GENERATOR_CONTRACT.md](GENERATOR_CONTRACT.md), [synthetic_data.json](../config/synthetic_data.json).
**Validation:** Documentation and JSON configuration published and read back from GitHub; no generator execution, dataset hashes or PostgreSQL imports have been performed.
**Decisions:** Seed 20261120, 2025 UTC observation window, fictional CU, stable ID ordering, independent RNG streams and separate invalid fixtures.
**Open:** Day 07 migration still awaits PostgreSQL runtime verification.
**Next:** Day 09 customer/catalog generator.

### Day 09 — 2026-11-21 (published early 2026-11-20)
**Goal:** Implement deterministic synthetic customer and catalog generation.
**Artifacts:** [Python generator](../src/generator.py), [unit tests](../tests/test_generator.py), [GitHub Actions workflow](../.github/workflows/day09-generator.yml), [run guide](DAY09_GENERATOR.md).
**Validation:** Local development prototype: 10/10 unit tests passed; 12 categories, 240 products and 10,000 customers generated, manifest hashes repeated. GitHub files read back. GitHub Actions status for the exact published revision not confirmed; PostgreSQL import not performed.
**Decisions:** Standard-library Python; deterministic independent RNG streams; data outputs generated on demand.
**Open:** Verify GitHub CI and Day 07 PostgreSQL migration.
**Next:** Day 10 order/item/payment generator.

### PostgreSQL Day 07 verification follow-up — 2026-11-20
**Goal:** Remove the need for user-installed PostgreSQL by using a disposable GitHub Actions PostgreSQL 16 service.
**Artifacts:** [PostgreSQL CI workflow](../.github/workflows/postgres-integration.yml), [schema assertions](../database/tests/003_schema_assertions.sql), [quality-gate fixtures](../database/tests/004_quality_gate_assertions.sql), [setup guide](POSTGRESQL_SETUP.md).
**Verification:** GitHub source publication verified. A successful PostgreSQL CI run has **not** been observed yet; Day 07 acceptance issue remains open until that evidence exists.
**Next:** Inspect the Actions run; fix any failures and record the actual result.

### CI status update — 2026-11-20
**Day 09:** User-provided GitHub Actions screenshot shows both Day 09 Python Generator Checks runs successful (15s and 9s). Issue #8 closed. This is evidence of overall workflow success; individual step logs were not inspected.
**Day 07:** Earlier screenshot shows latest PostgreSQL Integration Tests run green (28s), after two red runs. Job logs not independently reviewed; Issue #6 remains open pending acceptance evidence.
**Next:** Day 10 and final Day 07 log review.

### Day 07 acceptance closure — 2026-11-20
**Evidence:** User-provided GitHub Actions screenshot shows latest PostgreSQL schema integration test run successful (green check, 28 seconds) after two failed earlier attempts. The committed workflow includes transactional migration, schema assertions, 13 negative constraint fixtures, cross-table quality fixtures and final rollback check; its overall green status indicates those configured steps completed without failing the workflow.
**Limitation:** Individual job logs and assertions were not independently retrieved. This records workflow-level evidence, not a separate manual database audit.
**Decision:** Close Issue #6 as the requested clean-schema CI gate has a successful workflow result. Follow-up regression and detailed log review remain appropriate.

### Day 10 — 2026-11-22 (published early 2026-11-21)
**Goal:** Generate deterministic orders, order lines and payment attempts.
**Artifacts:** [Order generator](../src/order_generator.py), [integrated CLI](../src/generator.py), [unit tests](../tests/test_orders.py), [CI](../.github/workflows/day09-generator.yml), [runbook](DAY10_TRANSACTIONS.md).
**Verification:** GitHub source published; CI execution result not independently observed yet. No PostgreSQL import claim.
**Decisions:** Decimal-based discounted line totals, exactly one captured payment for completed orders, no captures for other statuses, seeded independent transaction RNG.
**Open:** CI green run and actual six-table PostgreSQL import verification.
**Next:** Day 11 marketing, sessions and events.

### Day 10 CI stabilization — 2026-11-21
**Incident:** GitHub Actions screenshot shows Day 10 CI failures on several consecutive push commits.
**Root cause identified in source:** `parse_config` mistakenly required exact `counts` for `order_items` and `payments`, which are configured only under `targets_approximate`.
**Fix:** Parse only exact-count tables; verify manifest checksums for all six CSVs; change Python CI to a single Python 3.12 job with `workflow_dispatch` only. This avoids an email-producing workflow run on each push.
**Evidence:** Updated files published and read back from GitHub. A passing CI run for the new revision has not yet been observed. Issue #9 remains open pending execution.

### Day 10 acceptance — 2026-11-21
**Evidence:** User-provided GitHub Actions screenshot shows Python synthetic data generator checks #9 (commit `1aebeecc`) succeeded in 23 seconds. This confirms the workflow for that revision, including unit tests, generation, validation and repeatability checks configured at the time of the run.
**CI noise:** Subsequent workflow revision switches to manual-only dispatch and one Python 3.12 job, preventing repeated automatic push runs. That manual-only revision has not itself been run in the screenshot.
**Decision:** Close Issue #9 for the Day 10 generator acceptance gate. Full six-table PostgreSQL import and future CI workflow revisions are not independently verified.

### Day 11 — 2026-11-22 (published ahead of roadmap date)
**Goal:** Generate deterministic campaigns, sessions and ordered funnel events with optional purchase linkage.
**Artifacts:** [marketing generator](../src/marketing_generator.py), [integrated CLI](../src/generator.py), [marketing tests](../tests/test_marketing.py), [runbook](DAY11_MARKETING.md), [manual CI workflow](../.github/workflows/day09-generator.yml).
**Verification:** GitHub source publication and read-back. The current code has not yet been observed passing GitHub Actions; local git clone was blocked by unavailable external DNS. Issue #10 stays open until verified.
**Decisions:** 24 fictional campaigns, 100k sessions, independent seeded streams, strict funnel ordering, purchase/customer match, explicit whole-campaign spend and unattributed sessions.
**Open:** CI green evidence, refunds, PostgreSQL import, end-to-end SQL quality gate.
**Next:** Day 12 data quality and remaining refunds table.

## Daily journal template

### Day NN — YYYY-MM-DD
**Goal:**  
**Artifacts changed:**  
**Validation performed:**  
**Key decisions:**  
**Open questions:**  
**Next step:**  

Do not check off an item until the corresponding artifact exists and has been verified.

### Day 12 — 2026-11-23
**Goal:** Complete ten-entity synthetic data generation with refunds and quality checks.
**Artifacts:** [refund/quality source](../src/refund_quality.py), [generator CLI](../src/generator.py), [tests](../tests/test_refunds.py), [guide](DAY12_QUALITY.md), [manual-only CI](../.github/workflows/day09-generator.yml).
**Verification:** Source and documentation published on GitHub. No successful CI run for this revision observed. External Git clone unavailable in current environment (DNS failure). PostgreSQL import and SQL quality-gate results not confirmed.
**Publication policy:** Few meaningful commits; manual-only CI prevents per-commit email noise. Do not manufacture contribution activity.
**Open:** Day 11 CI, Day 12 CI, real ten-table PostgreSQL import, SQL quality gate.
**Next:** Day 13 SQL fundamentals after quality acceptance.

### Day 13 — 2026-11-25
**Artifacts:** [SQL fundamentals casebook](../database/analytics/day13_fundamentals.sql).
**Scope:** Ten business queries covering filtering, joins, grouping, HAVING, anti-joins, category sales, monthly AOV, payment attempts and settled refunds. Completed-order totals are aggregated before calculating AOV. UTC reporting; refund settlement month is separate from order month.
**Run:** `psql -X -v ON_ERROR_STOP=1 -f database/analytics/day13_fundamentals.sql` against a populated PostgreSQL database. The read-only transaction checks sales/capture reconciliation and rejects empty completed-order datasets and missing order items.
**Verification:** Source publication only; PostgreSQL execution and fixture results pending. No numerical findings claimed. Day 11–12 CI acceptance remains pending. No workflow changes or automatic generator runs requested.
**Next:** Day 14 revenue and order KPI mart.

### Day 14 — 2026-11-27
**Artifact:** [Revenue KPI mart](../database/analytics/day14_revenue_mart.sql).
**Design:** Three reusable views at completed-order, daily and monthly grain. UTC order placement date for sales; UTC settlement date for refunds. Refund-only dates retained; no zero-activity calendar spine. AOV is weighted by order count and null without orders. Currency CU, synthetic data only.
**Run:** After migration 001 and loading validated synthetic data, execute `psql -X -v ON_ERROR_STOP=1 -f database/analytics/day14_revenue_mart.sql`. Requires permission to create analytics schema/views. DDL commits before read-only acceptance checks; failed acceptance does not remove views.
**Acceptance:** Compare completed order counts, captured amounts and settled refunds to monthly totals; verify daily identities and per-order capture reconciliation. Source published; runtime results not verified. No actual KPI values claimed. Day 11–13 runtime gates remain pending.
**Next:** Day 15 window functions and CTE casebook.
