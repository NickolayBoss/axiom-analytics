#!/usr/bin/env bash
set -euo pipefail
# Requires psql and a disposable PostgreSQL database selected by PG* variables.
# BEGIN/ROLLBACK guarantee that fixture rows do not persist on success.
{ echo 'BEGIN;'; cat database/tests/001_constraints.sql; echo 'ROLLBACK;'; } | psql -X -v ON_ERROR_STOP=1
echo 'PASS: constraint fixtures completed and rolled back'
