# Day 04 — Event Taxonomy and Funnel Semantics

**Status:** Proposed specification; event instrumentation not implemented.

## Event catalog

| Event type | Meaning | Required fields | Optional fields |
|---|---|---|---|
| session_start | Session begins | event_id, session_id, occurred_at | customer_id |
| product_view | Product detail viewed | event_id, session_id, occurred_at | product_id |
| add_to_cart | Item added to cart | event_id, session_id, occurred_at | product_id |
| checkout_start | Checkout initiated | event_id, session_id, occurred_at | order_id |
| purchase | Completed eligible order associated with session | event_id, session_id, occurred_at, order_id | campaign_id via session |

## Ordered funnel contract

The canonical stage order is `session_start → product_view → add_to_cart → checkout_start → purchase`.

1. Cohort = sessions whose `started_at` is inside the reporting period.
2. Deduplicate by `session_id + event_type` for stage membership; preserve earliest qualifying occurrence after the prior stage.
3. For each session, a stage is reached only if the immediately preceding stage was reached at an earlier timestamp. Ties do **not** count as progression.
4. `purchase` requires an eligible completed order and an order ID consistent with the purchase event.
5. Count each session once per stage; multiple product views cannot inflate conversion.
6. Anonymous sessions are allowed; unknown campaign remains unattributed.
7. Event timestamps must be >= session start. Session end and timeout rules are pending Day 05 design.

## Example fixtures

| Session | Events in time order | Expected last reached stage |
|---|---|---|
| S-01 | start, view, cart, checkout, purchase | purchase |
| S-02 | start, view, view, cart | add_to_cart |
| S-03 | start, checkout, view | product_view |
| S-04 | start, view, cart, checkout, purchase for invalid order | checkout_start |
| S-05 | start and view at same timestamp | session_start |

## KPI calculations

- `stage_sessions`: distinct sessions reaching each ordered stage.
- `stage_conversion`: sessions reaching stage N / sessions reaching stage N-1.
- `overall_conversion`: sessions reaching purchase / sessions reaching session_start.
- For a zero denominator, return NULL rather than division by zero.
- Label funnel as session-based, not user-based.

## Data integrity and assumptions

The session record has `started_at` and optional customer/campaign IDs. Event IDs are unique. Session start event must be present for eligible funnel sessions; a missing start event is a data-quality exception. Do not infer checkout completion from payment attempts alone.

**Open design decision:** session timeout/end timestamp, late-arriving events and events crossing reporting boundaries. Specify before SQL implementation.
