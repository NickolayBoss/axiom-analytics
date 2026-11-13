# Verification and Evidence Policy

## Goal
Every public claim should be backed by a reproducible artifact or test.

## Verification levels
- **Design review:** consistency of requirements, model, definitions and diagrams.
- **Static checks:** formatting, file existence, SQL parsing where available.
- **Execution checks:** run schema, generators, queries and automated tests against PostgreSQL.
- **Business reconciliation:** compare dashboard metrics with independently calculated totals.
- **Visual checks:** capture actual dashboard screenshots after the BI application runs.

## Evidence convention
For each analytical case, record: business question, input tables, data grain, filters, query path, expected result, actual result, execution command, and limitations.

## Minimum release checklist
- [ ] Clean database initialization succeeds.
- [ ] Synthetic data generation is repeatable from a fixed seed.
- [ ] Foreign keys and business constraints are tested.
- [ ] Revenue and refunds reconcile.
- [ ] SQL analytical outputs match test fixtures.
- [ ] Dashboard metrics match source SQL.
- [ ] Docker-based setup works from a clean checkout.
- [ ] Screenshots are taken from the real running application.
- [ ] README commands are executed and verified.

## Reporting honesty
Do not mark execution checks as passed based on code inspection alone. If local infrastructure is unavailable, report tests as **not run**, with an exact reproduction command. Never fabricate screenshots, metrics or benchmark improvements.
