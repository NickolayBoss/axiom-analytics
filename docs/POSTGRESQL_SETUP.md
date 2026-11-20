# Day 07 — PostgreSQL setup and verification

**Requires:** PostgreSQL 15+ and `psql` (or a PostgreSQL Docker image). **Never use a production database.**

## Local quickstart

Create a fresh disposable database (replace the database name if necessary):

```bash
createdb axiom_dev
export PGDATABASE=axiom_dev
psql -X -v ON_ERROR_STOP=1 -1 -f database/migrations/001_initial_schema.sql
psql -X -v ON_ERROR_STOP=1 -Atc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"
bash database/tests/run_constraints.sh
```

The table count should be **10**. The test runner inserts valid fixtures, asserts **13 expected constraint failures**, and rolls back the test transaction. A second migration on the same database is expected to fail; use a new database for a clean-room test. The migration is **not** idempotent.

## Docker alternative

```bash
docker run --rm --name axiom-pg -e POSTGRES_PASSWORD=axiom -e POSTGRES_DB=axiom_dev -p 127.0.0.1:5433:5432 -d postgres:16
# Wait for readiness:
docker exec axiom-pg pg_isready -U postgres -d axiom_dev
docker exec -i axiom-pg psql -U postgres -d axiom_dev -X -v ON_ERROR_STOP=1 -1 < database/migrations/001_initial_schema.sql
docker exec -i axiom-pg psql -U postgres -d axiom_dev -X -v ON_ERROR_STOP=1 -Atc "SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"
{ echo 'BEGIN;'; cat database/tests/001_constraints.sql; echo 'ROLLBACK;'; } | docker exec -i axiom-pg psql -U postgres -d axiom_dev -X -v ON_ERROR_STOP=1
docker stop axiom-pg
```

The fixture suite tests row-level constraints, not the full cross-table quality gate. After loading generated data, run `psql -X -f database/tests/002_quality_gate.sql` and require zero result rows.

## Automated integration test (added 2026-11-20)

[GitHub Actions PostgreSQL integration workflow](../.github/workflows/postgres-integration.yml) provisions PostgreSQL 16 as a disposable service and performs:

1. Transactional schema migration with `ON_ERROR_STOP=1`.
2. Schema assertions for ten tables, eleven foreign keys and captured-payment uniqueness.
3. Thirteen negative row-level constraint fixtures, with rollback.
4. Cross-table quality fixture assertions and rollback.
5. A final check that test rows were not persisted.

**Check execution:** Open [Actions](https://github.com/NickolayBoss/axiom-analytics/actions/workflows/postgres-integration.yml) to inspect the latest run. Creating a workflow file does not itself prove a successful CI run. Only close the Day 07 acceptance issue after a green run has been confirmed.

## Verification record (2026-11-18)

- GitHub file publication and read-back: verified.
- SQL design compared to Day 05 dictionary and Day 06 constraint matrix.
- **PostgreSQL execution: not performed in this automation environment** (no `psql`, PostgreSQL server or Docker executable installed).
- No claim of successful migration or passing SQL runtime tests is made. Run the commands above on a PostgreSQL-equipped host to satisfy the roadmap's clean-schema acceptance gate.

## Boundaries

Partial capture, concurrency-safe refund prevention, cross-table event-time constraints and financial reconciliation are **not** enforced by row-level DDL. See [quality gate SQL](../database/tests/002_quality_gate.sql), [ADR-007](ADR/007-relational-integrity-boundaries.md) and [data dictionary](DATA_DICTIONARY.md).
