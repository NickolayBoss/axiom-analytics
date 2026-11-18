#!/usr/bin/env bash
set -euo pipefail
# Requires PostgreSQL psql and a disposable database configured by PG* env vars.
# Never run on production data.
psql -X -v ON_ERROR_STOP=1 -c "BEGIN; $(printf '')" >/dev/null
# The test file is executed in a transaction and explicitly rolled back on success.
{ echo 'BEGIN;'; cat database/tests/001_constraints.sql; echo 'ROLLBACK;'; } | psql -X -v ON_ERROR_STOP=1
echo 'PASS: SQL fixture transaction rolled back'
