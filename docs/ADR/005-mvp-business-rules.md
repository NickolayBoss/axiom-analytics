# ADR-005 — Freeze MVP accounting and funnel semantics

**Date:** 2026-11-15  
**Status:** Accepted for MVP design; implementation pending.

## Context
Stakeholder requirements exposed ambiguity in revenue eligibility, refunds, attribution and funnel stage counts. Without explicit conventions, SQL reports can disagree even when individually valid.

## Decision
- Count only completed orders with a full successful capture as eligible purchases.
- Compute line-level amounts with fixed precision and exclude shipping/taxes.
- Report sales by order date, refunds by settlement date, and net sales by calendar-period difference.
- Use a session-contained purchase event for single-touch campaign attribution.
- Enforce ordered, deduplicated session funnel stages.
- Keep whole-campaign spend analysis separate from time-sliced reporting until spend granularity is designed.
- Explicitly exclude immature customers from 30-day repeat-purchase denominators.

## Alternatives considered
- Count all placed orders: rejected because abandoned/unpaid orders inflate sales.
- Join payments/refunds directly to items: rejected due to row multiplication.
- Allocate campaign spend uniformly per day: deferred because it introduces an unvalidated assumption.
- Multi-touch attribution: deferred to keep MVP auditable.

## Consequences
Definitions are simpler to test but deliberately exclude partial capture and multi-touch marketing effects. These limitations must appear in reports and dashboards.

## Revisit when
Realistic settlement state transitions, daily marketing spend or cross-session attribution become requirements.
