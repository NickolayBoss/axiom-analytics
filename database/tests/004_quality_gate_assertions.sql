-- Exercise quality gate on a disposable DB; all fixture data is rolled back.
BEGIN;
INSERT INTO customers VALUES (9001,'2025-01-01T00:00:00Z','North','organic');
INSERT INTO categories VALUES (9001,'Quality demo');
INSERT INTO products VALUES (9001,9001,'Quality item',100.00,true);
INSERT INTO orders VALUES (9001,9001,'2025-02-01T00:00:00Z','completed');
INSERT INTO order_items VALUES (9001,9001,9001,1,100.00,0.00);
INSERT INTO payments VALUES (9001,9001,'2025-02-01T00:01:00Z',100.00,'captured');
INSERT INTO sessions VALUES (9001,9001,NULL,'2025-02-01T00:00:00Z','2025-02-01T00:10:00Z');
INSERT INTO events VALUES (9001,9001,'2025-02-01T00:00:00Z','session_start',NULL,NULL);
CREATE TEMP TABLE gate_violations AS
WITH item_totals AS (
 SELECT order_id,SUM(quantity::numeric * unit_price - discount_amount) net_amount
 FROM order_items GROUP BY order_id
), captures AS (
 SELECT order_id,COUNT(*) capture_count,MAX(amount) captured_amount
 FROM payments WHERE status='captured' GROUP BY order_id
), refund_totals AS (
 SELECT payment_id,SUM(amount) refund_amount FROM refunds WHERE status='settled' GROUP BY payment_id
)
SELECT 'DQ-F01' AS rule_id,o.order_id::text entity_id
FROM orders o LEFT JOIN item_totals i ON i.order_id=o.order_id
WHERE o.status='completed' AND i.order_id IS NULL
UNION ALL
SELECT 'DQ-F02',o.order_id::text FROM orders o
LEFT JOIN item_totals i ON i.order_id=o.order_id
LEFT JOIN captures c ON c.order_id=o.order_id
WHERE o.status='completed' AND (COALESCE(c.capture_count,0)<>1 OR c.captured_amount IS DISTINCT FROM i.net_amount)
UNION ALL
SELECT 'DQ-F03',p.payment_id::text FROM payments p
JOIN refund_totals r ON r.payment_id=p.payment_id
WHERE p.status<>'captured' OR r.refund_amount>p.amount
UNION ALL
SELECT 'DQ-F04',e.event_id::text FROM events e JOIN sessions s ON s.session_id=e.session_id
WHERE e.occurred_at<s.started_at OR e.occurred_at>s.ended_at
UNION ALL
SELECT 'DQ-F05',e.event_id::text FROM events e JOIN sessions s ON s.session_id=e.session_id
JOIN orders o ON o.order_id=e.order_id
WHERE e.event_type='purchase' AND s.customer_id IS NOT NULL AND s.customer_id<>o.customer_id;
DO $$
BEGIN
 IF EXISTS (SELECT 1 FROM gate_violations) THEN
  RAISE EXCEPTION 'Valid fixture triggered quality-gate violation';
 END IF;
 RAISE NOTICE 'PASS: valid fixture has no quality violations';
END $$;
DROP TABLE gate_violations;
INSERT INTO refunds VALUES (9001,9001,'2025-02-02T00:00:00Z','2025-02-02T00:01:00Z',90,'settled','Test');
INSERT INTO refunds VALUES (9002,9001,'2025-02-03T00:00:00Z','2025-02-03T00:01:00Z',20,'settled','Test');
DO $$
BEGIN
 IF NOT EXISTS (
   SELECT 1 FROM payments p JOIN refunds r ON r.payment_id=p.payment_id
   WHERE p.payment_id=9001 GROUP BY p.payment_id,p.amount
   HAVING SUM(r.amount)>p.amount
 ) THEN RAISE EXCEPTION 'Over-refund was not detected'; END IF;
 RAISE NOTICE 'PASS: cross-row over-refund detected';
END $$;
ROLLBACK;
