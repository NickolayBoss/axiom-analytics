-- Day 13 | PostgreSQL 15+ | SQL fundamentals casebook
-- Run with psql -X -v ON_ERROR_STOP=1 -f database/analytics/day13_fundamentals.sql
-- Synthetic data only. Read-only snapshot; UTC reporting.
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;
SET LOCAL TIME ZONE 'UTC';

-- 1. Active catalog: filtering, sorting, limiting.
SELECT product_id, product_name, list_price
FROM products WHERE active AND list_price >= 100
ORDER BY list_price DESC, product_id LIMIT 20;

-- 2. Customer acquisition mix: GROUP BY, COUNT.
SELECT acquisition_source, COUNT(*) AS customers
FROM customers GROUP BY acquisition_source ORDER BY customers DESC, acquisition_source;

-- 3. Orders by status: conditional aggregation.
SELECT status, COUNT(*) AS orders
FROM orders GROUP BY status ORDER BY status;

-- 4. Catalog coverage: LEFT JOIN preserves empty categories.
SELECT c.category_id, c.category_name, COUNT(p.product_id) AS products
FROM categories c LEFT JOIN products p USING (category_id)
GROUP BY c.category_id, c.category_name ORDER BY c.category_id;

-- 5. Repeat buyers: HAVING at customer grain.
SELECT customer_id, COUNT(*) AS completed_orders
FROM orders WHERE status = 'completed'
GROUP BY customer_id HAVING COUNT(*) >= 2
ORDER BY completed_orders DESC, customer_id LIMIT 20;

-- 6. Customers without completed orders: anti-join.
SELECT c.customer_id, c.region
FROM customers c WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id AND o.status = 'completed'
) ORDER BY c.customer_id LIMIT 20;

-- 7. Completed sales by category: item grain; no payment/event joins.
SELECT c.category_id, c.category_name,
       SUM(i.quantity) AS units,
       SUM(i.quantity * i.unit_price) AS gmv,
       SUM(i.discount_amount) AS discounts,
       SUM(i.quantity * i.unit_price - i.discount_amount) AS sales
FROM orders o JOIN order_items i USING (order_id)
JOIN products p USING (product_id) JOIN categories c USING (category_id)
WHERE o.status = 'completed'
GROUP BY c.category_id, c.category_name ORDER BY sales DESC, c.category_id;

-- 8. Monthly completed orders and AOV: preaggregate at order grain.
WITH order_totals AS (
    SELECT o.order_id, o.placed_at,
           SUM(i.quantity * i.unit_price - i.discount_amount) AS sales
    FROM orders o JOIN order_items i USING (order_id)
    WHERE o.status = 'completed' GROUP BY o.order_id, o.placed_at
)
SELECT date_trunc('month', placed_at)::date AS month,
       COUNT(*) AS completed_orders, SUM(sales) AS sales,
       ROUND(SUM(sales) / NULLIF(COUNT(*), 0), 2) AS aov
FROM order_totals GROUP BY 1 ORDER BY 1;

-- 9. Payment attempts by status; attempts are not orders.
SELECT status, COUNT(*) AS attempts, SUM(amount) AS attempted_amount
FROM payments GROUP BY status ORDER BY status;

-- 10. Settled refunds by settlement month, not order month.
SELECT date_trunc('month', refunded_at)::date AS month,
       COUNT(*) AS settled_refunds, SUM(amount) AS refund_value
FROM refunds WHERE status = 'settled' GROUP BY 1 ORDER BY 1;

-- Acceptance assertions: independently aggregate completed sales and captures.
-- Raise an error rather than silently report inconsistent financial data.
DO $$
DECLARE sales numeric; captured numeric;
BEGIN
    SELECT COALESCE(SUM(i.quantity * i.unit_price - i.discount_amount), 0)
      INTO sales FROM orders o JOIN order_items i USING (order_id)
      WHERE o.status = 'completed';
    SELECT COALESCE(SUM(amount), 0) INTO captured FROM payments WHERE status = 'captured';
    IF sales <> captured THEN
        RAISE EXCEPTION 'Sales/capture reconciliation failed: % vs %', sales, captured;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM orders WHERE status = 'completed') THEN
        RAISE EXCEPTION 'No completed orders; load synthetic data before acceptance';
    END IF;
    IF EXISTS (
        SELECT 1 FROM orders o
        LEFT JOIN order_items i USING (order_id)
        WHERE o.status = 'completed' AND i.order_item_id IS NULL
    ) THEN RAISE EXCEPTION 'Completed order without items'; END IF;
END $$;
COMMIT;
