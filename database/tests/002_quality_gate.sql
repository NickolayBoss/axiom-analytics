-- Read-only cross-table quality gate; returns zero rows when all checks pass.
-- Run AFTER fixture loading. Each result is a blocking integrity violation.
WITH item_totals AS (
 SELECT order_id, SUM(quantity::numeric * unit_price - discount_amount) AS net_amount
 FROM order_items GROUP BY order_id
), captures AS (
 SELECT order_id, COUNT(*) AS capture_count, MAX(amount) AS captured_amount
 FROM payments WHERE status='captured' GROUP BY order_id
), refund_totals AS (
 SELECT payment_id, SUM(amount) AS refund_amount
 FROM refunds WHERE status='settled' GROUP BY payment_id
)
SELECT 'DQ-F01' AS rule_id, o.order_id::text AS entity_id
 FROM orders o LEFT JOIN item_totals i ON i.order_id=o.order_id
 WHERE o.status='completed' AND i.order_id IS NULL
UNION ALL
SELECT 'DQ-F02', o.order_id::text
 FROM orders o LEFT JOIN item_totals i ON i.order_id=o.order_id
 LEFT JOIN captures c ON c.order_id=o.order_id
 WHERE o.status='completed' AND (COALESCE(c.capture_count,0) <> 1 OR c.captured_amount IS DISTINCT FROM i.net_amount)
UNION ALL
SELECT 'DQ-F03', p.payment_id::text
 FROM payments p JOIN refund_totals r ON r.payment_id=p.payment_id
 WHERE p.status <> 'captured' OR r.refund_amount > p.amount
UNION ALL
SELECT 'DQ-F04', e.event_id::text
 FROM events e JOIN sessions s ON s.session_id=e.session_id
 WHERE e.occurred_at < s.started_at OR e.occurred_at > s.ended_at
UNION ALL
SELECT 'DQ-F05', e.event_id::text
 FROM events e JOIN sessions s ON s.session_id=e.session_id JOIN orders o ON o.order_id=e.order_id
 WHERE e.event_type='purchase' AND s.customer_id IS NOT NULL AND s.customer_id <> o.customer_id
UNION ALL
SELECT 'DQ-F06', e.event_id::text
 FROM events e JOIN sessions s ON s.session_id=e.session_id JOIN campaigns c ON c.campaign_id=s.campaign_id
 WHERE e.event_type='purchase' AND ( (e.occurred_at AT TIME ZONE 'UTC')::date < c.start_date OR (e.occurred_at AT TIME ZONE 'UTC')::date > c.end_date )
ORDER BY rule_id, entity_id;
