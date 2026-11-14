# Delivery Log

## Current status

**Phase:** Day 03 — System Requirements Specification (completed)  
**Project start:** 2026-11-13  
**Target portfolio release:** 2026-12-12  
**Next:** Day 04 — Business processes and data flows

## Completed / verified

- [x] GitHub repository created and publicly accessible.
- [x] Initial project scope and 30-day delivery plan published.
- [x] Target architecture, initial data model and metric definitions documented.
- [x] Day 02: five simulated stakeholder personas, twelve business questions and four scenarios published.
- [x] Day 03: sixteen functional and ten non-functional requirements, twenty planned acceptance tests, five detailed use cases and ADR-005 published.

## Not yet implemented

- [ ] PostgreSQL DDL and migrations
- [ ] Synthetic dataset and generator
- [ ] Python ingestion pipeline
- [ ] SQL analytical cases
- [ ] Automated data quality checks
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
**Key decisions:** Prioritize financial reconciliation, retention, funnel analysis and data quality.

### Day 03 — 2026-11-15
**Goal:** Formalize testable system requirements and freeze MVP business semantics.  
**Artifacts:** [REQUIREMENTS.md](REQUIREMENTS.md), [ACCEPTANCE_TESTS.md](ACCEPTANCE_TESTS.md), [USE_CASES.md](USE_CASES.md), [ADR-005](ADR/005-mvp-business-rules.md).  
**Validation:** Document structure and ID coverage reviewed; GitHub file publication confirmed. Acceptance tests are **specifications only** and have not been executed.  
**Key decisions:** Eligible-order, refund-period, funnel-stage and attribution rules established for MVP.  
**Open questions:** Partial captures, daily spend allocation and multi-touch attribution deferred.  
**Next step:** Model business processes and data flows on Day 04.

## Daily journal template

### Day NN — YYYY-MM-DD
**Goal:**  
**Artifacts changed:**  
**Validation performed:**  
**Key decisions:**  
**Open questions:**  
**Next step:**  

Do not check off an item until the corresponding artifact exists and has been verified.
