# ADR-006 — Quality-gated analytical publication

**Date:** 2026-11-15  
**Status:** Accepted for design; implementation pending.

## Context
A dashboard can display plausible but incorrect numbers when source data is incomplete, payment attempts multiply order rows, or refunds exceed captured amounts.

## Decision
Introduce a logical quality gate between loading operational data and refreshing analytical marts. Validate referential integrity, event ordering and financial reconciliation. On critical failures, block publishing the affected reports and retain actionable diagnostics.

## Alternatives
- Publish all data with warning banners: rejected for critical financial integrity failures.
- Ignore invalid rows silently: rejected due to hidden bias.
- Stop on every missing campaign ID: rejected because unattributed sessions are expected and valid.

## Consequences
Reports become auditable and trustworthy but require explicit failure handling and reproducible test fixtures. The gate is a **design decision**, not a currently running service.

## References
[Processes](../PROCESSES.md) · [Data flows](../DATA_FLOWS.md) · [Requirements](../REQUIREMENTS.md)
