# Day 08 — Synthetic Data Edge-Case Catalog

**Status:** Planned deterministic fixtures; none executed.

| ID | Scenario | Expected handling | Related checks |
|---|---|---|---|
| EDGE-01 | Completed order with two failed attempts followed by one capture | Count one order; failed attempts excluded | FR-05, AT-06 |
| EDGE-02 | Completed order with two item lines | Aggregate item net before joining payments | FR-05, FR-06 |
| EDGE-03 | Captured 100 CU with two settled refunds 20 and 30 CU | Refunds total 50 CU | AT-07 |
| EDGE-04 | Refund total exceeds captured amount | Invalid fixture, rejected/quarantined | AT-08, DQ-F03 |
| EDGE-05 | Pending refund with no settlement timestamp | Exclude from settled refunds | BRULE-03 |
| EDGE-06 | Customer with first purchase near observation end | Exclude from mature 30-day repeat denominator | AT-10 |
| EDGE-07 | Zero eligible orders in a period | Orders = 0, AOV = NULL | UC-01 |
| EDGE-08 | Duplicate product_view events in one session | Count stage once | AT-11 |
| EDGE-09 | checkout_start before add_to_cart | No valid advancement beyond last ordered stage | AT-12 |
| EDGE-10 | Session_start and product_view share timestamp | Strictly increasing progression fails | Event taxonomy |
| EDGE-11 | Anonymous session with no campaign | Retain in session denominator; unattributed | BRULE-07 |
| EDGE-12 | Purchase linked to inactive campaign | Unattributed | AT-14 |
| EDGE-13 | Campaign with zero spend | ROAS NULL | AT-15 |
| EDGE-14 | Product becomes inactive after historical purchase | Preserve historical item snapshot | Data dictionary |
| EDGE-15 | Invalid FK for product or customer | Negative fixture rejected | AT-01 |
| EDGE-16 | Discount greater than line gross | Negative fixture rejected | AT-04 |
| EDGE-17 | Event outside session bounds | Negative fixture rejected by quality gate | DQ-F04 |
| EDGE-18 | Purchase event references order belonging to another identified customer | Negative fixture rejected by quality gate | DQ-F05 |
| EDGE-19 | Duplicate source primary key | Negative fixture rejected or quarantined | DQ-001 |
| EDGE-20 | Event exactly at session end | Allowed by inclusive boundary; funnel chronology still required | DQ-F04 |

## Fixture separation

- **Clean dataset:** valid rare cases (EDGE-01,02,03,05,06,07,08,09,10,11,12,13,14,20).
- **Invalid dataset:** deliberately corrupted rows (EDGE-04,15,16,17,18,19). Never mix these into clean baseline CSV exports.
- Each fixture will have a stable ID, seed and expected assertion in future automated tests.

## Caveats

A session's ordered funnel stage membership can stop before later events even when those later events are individually valid. The generator must not claim production-realistic behavioral rates or statistical representativeness.
