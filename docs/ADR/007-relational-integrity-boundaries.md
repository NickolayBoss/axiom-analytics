# ADR-007 — Split row constraints from cross-table quality gates

**Date:** 2026-11-16  
**Status:** Accepted for design; not yet implemented.

## Context
The dictionary requires both local validity (positive amounts, valid enums) and cross-row rules (captured payment matching item total, cumulative refunds not exceeding capture, session/event time bounds).

## Decision
Enforce local constraints through PostgreSQL PRIMARY KEY, FOREIGN KEY, NOT NULL, CHECK and partial UNIQUE indexes. Enforce aggregate/cross-table analytics invariants in a versioned data-quality suite. For the offline MVP, block publication when critical invariants fail. Do not pretend batch validation provides production-grade concurrent payment safety.

## Alternatives
- Encode everything as CHECK: impossible for cross-table subqueries.
- Omit checks and trust synthetic data: rejected because it undermines reproducibility and correctness.
- Build triggers and transaction locks for every invariant immediately: deferred; excessive for a read-oriented portfolio MVP.

## Consequences
The schema is maintainable and testable; some invalid intermediate operational states can exist and must be caught by the quality gate. Production systems would require stronger transactional enforcement.

## References
[Relational review](../RELATIONAL_DESIGN_REVIEW.md) · [Constraints](../CONSTRAINT_MATRIX.md) · [Dictionary](../DATA_DICTIONARY.md)
