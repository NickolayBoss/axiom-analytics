# Development Workflow

## Principles

This is a portfolio project with production-inspired standards. Changes should be small, reviewable, reproducible and supported by evidence.

## Daily workflow

1. Read the current day in [ROADMAP.md](ROADMAP.md).
2. Write a concise problem statement and acceptance criteria.
3. Implement the smallest complete increment.
4. Run available tests and verify results manually.
5. Update documentation and [PROGRESS.md](PROGRESS.md).
6. Commit with a meaningful message.

## Commit convention

Use conventional commit prefixes:
- `docs:` documentation and decisions
- `feat:` new functionality
- `test:` verification
- `fix:` bug fixes
- `refactor:` structural changes without behavior changes
- `perf:` measured performance improvements
- `chore:` tooling

Example: `docs: define business metrics and 30-day roadmap`.

## SQL review checklist

- Clear purpose and input grain.
- Explicit joins and filters.
- No accidental row multiplication.
- Correct handling of nulls and zero denominators.
- Consistent timestamp and monetary semantics.
- Test case or reconciliation query.
- `EXPLAIN ANALYZE` evidence for optimization claims.

## Documentation standards

Write project-facing docs in English. Every analytical report should include the business question, dataset assumptions, methodology, SQL reference, results, limitations and recommendation. Do not claim that proposed functionality is already implemented.

## Definition of done

A task is complete only when the artifact exists in the repository, relevant checks pass, documentation is current and the result is reproducible.
