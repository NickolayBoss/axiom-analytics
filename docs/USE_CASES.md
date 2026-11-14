# Use Case Specifications — Day 03

These use cases refine the simulated stakeholder scenarios in [Day 02](STAKEHOLDER_REQUIREMENTS.md).

## UC-01 — Executive monthly performance review
**Actor:** General Manager (ST-01)  
**Preconditions:** Valid orders and payment records loaded; reporting timezone configured.  
**Trigger:** User chooses a month.  
**Main flow:** 1. Select month. 2. Filter eligible completed orders. 3. Aggregate item-level sales. 4. Subtract settled refunds dated in the selected month. 5. Display orders, sales, refunds, net sales and AOV.  
**Alternate flow:** No eligible orders → show zero order count and NULL AOV.  
**Acceptance:** AT-05, AT-06, AT-07, AT-17.  
**Output:** Decision-ready monthly summary with metric definitions.

## UC-02 — Finance reconciliation
**Actor:** Finance Analyst (ST-04)  
**Preconditions:** Order, payment and refund data available.  
**Trigger:** Analyst requests reconciliation for a date range.  
**Main flow:** 1. Check eligible order payment capture. 2. Aggregate item amounts by order. 3. Aggregate refunds separately by payment. 4. Compare totals without multiplying joins. 5. Report mismatches.  
**Exceptions:** Over-refund, missing capture, repeated payment attempts.  
**Acceptance:** AT-06, AT-07, AT-08, AT-16.

## UC-03 — Checkout funnel diagnosis
**Actor:** Product Manager (ST-03)  
**Preconditions:** Sessions and timestamped events loaded.  
**Trigger:** User selects date range.  
**Main flow:** 1. Identify eligible sessions. 2. Sort events chronologically. 3. Deduplicate stage events. 4. Enforce progression. 5. Calculate stage counts and conversions.  
**Exceptions:** Anonymous session, missing stages, out-of-order events.  
**Acceptance:** AT-11, AT-12.

## UC-04 — Campaign review
**Actor:** Marketing Lead (ST-02)  
**Preconditions:** Campaign dates/spend and attributed purchase sessions available.  
**Trigger:** User selects a completed campaign.  
**Main flow:** 1. Determine campaign duration. 2. Apply attribution rule. 3. Aggregate attributed eligible purchases. 4. Compute whole-campaign descriptive ROAS. 5. Display caveats.  
**Exceptions:** No campaign attribution, zero spend, incomplete campaign.  
**Acceptance:** AT-13, AT-14, AT-15.

## UC-05 — Cohort retention review
**Actor:** General Manager (ST-01)  
**Preconditions:** Customer purchase history available.  
**Trigger:** User chooses a cohort month.  
**Main flow:** 1. Find first eligible purchase. 2. Assign cohort month. 3. Count eligible return purchases by cohort age. 4. Exclude immature 30-day observation windows. 5. Display retention matrix.  
**Acceptance:** AT-09, AT-10.

## Non-goals
No real customer profiling, production marketing optimization, causal inference or real-time alerts are promised in the MVP.
