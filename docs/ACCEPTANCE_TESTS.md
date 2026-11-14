# Acceptance Test Matrix — Specification

**Status:** Test design only. No tests below have been executed yet.

| Test ID | Requirements | Fixture / setup | Expected outcome |
|---|---|---|---|
| AT-01 | FR-01, NFR-02 | Insert order with nonexistent customer | Foreign-key violation |
| AT-02 | FR-02, NFR-01 | Generate twice with identical seed | Canonical record hashes match |
| AT-03 | FR-03 | Load same batch twice | No new duplicate business keys |
| AT-04 | FR-04 | Item quantity 0, negative unit price, discount greater than gross | Validation rejects each |
| AT-05 | FR-05, NFR-03 | Two completed orders with item nets 100 and 50 CU | Eligible sales 150 CU, AOV 75 CU |
| AT-06 | FR-05, FR-06 | One completed order, two failed payment attempts, one capture | Exactly one eligible order |
| AT-07 | FR-06 | Captured 100 CU, settled refunds 20 + 30 CU | Refund value 50 CU, net sales 50 CU |
| AT-08 | FR-06 | Refunds 80 + 30 CU against capture 100 CU | Reject/flag over-refund |
| AT-09 | FR-08 | First purchase Jan 1; second Jan 15 | Customer qualifies for 30-day repeat |
| AT-10 | FR-08 | First purchase within 30 days of observation end | Exclude from mature denominator |
| AT-11 | FR-09 | Same session has two product_view events | Count session once at product_view stage |
| AT-12 | FR-09 | checkout_start before add_to_cart | Do not count a valid ordered progression |
| AT-13 | FR-11 | Purchase event in active campaign session | Attribute to that campaign |
| AT-14 | FR-11 | No campaign or inactive campaign | Unattributed |
| AT-15 | FR-12 | Campaign spend 0 CU | ROAS undefined/NULL, not infinity |
| AT-16 | FR-10 | Missing FK or duplicate source key | Nonzero exception count and actionable diagnostic |
| AT-17 | FR-15, NFR-10 | Compare dashboard total to governed SQL | Equal under same period and filters |
| AT-18 | FR-16, NFR-06 | Clean checkout, follow runbook | Services and sample reports reproduce |
| AT-19 | NFR-05 | 100k-order fixture on recorded machine | Core KPI query target <= 5 seconds |
| AT-20 | NFR-08 | Repository scan for secrets and real PII | No known secrets or real PII found |

## Execution evidence template

- **Test ID:**
- **Status:** NOT RUN / PASS / FAIL
- **Command and environment:**
- **Fixture version / seed:**
- **Observed output:**
- **Expected output:**
- **Evidence link:**
- **Follow-up:**

## Review rules

Do not label tests PASS without running them. Keep business semantics stable across SQL, Python and BI. Test partial refunds, zero denominators, row multiplication, boundary dates and anonymous sessions explicitly.
