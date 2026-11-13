# Architecture Decision Records (ADR Index)

## ADR-001 — Synthetic-first dataset
**Date:** 2026-11-13  
**Status:** Accepted  
**Context:** A portfolio repository should be safe to publish and easy to reproduce.  
**Decision:** Generate fictional deterministic data with Python and document distributions.  
**Consequences:** No privacy exposure from real customer data; findings cannot be generalized to real commerce.

## ADR-002 — PostgreSQL as analytical source
**Date:** 2026-11-13  
**Status:** Accepted  
**Decision:** Use PostgreSQL for relational constraints, analytical SQL and EXPLAIN-based tuning.  
**Consequences:** Local database setup is required; Docker will simplify onboarding.

## ADR-003 — Metrics before dashboards
**Date:** 2026-11-13  
**Status:** Accepted  
**Decision:** Define KPI semantics and reconciliation tests before visualization.  
**Consequences:** Dashboards are delayed until the definitions are stable, reducing inconsistent reporting.

## ADR-004 — Evidence-based portfolio
**Date:** 2026-11-13  
**Status:** Accepted  
**Decision:** Separate proposed, implemented, tested and demonstrated functionality.  
**Consequences:** No placeholder charts or invented performance statistics are described as achieved results.
