-- Day 14: reusable revenue mart, PostgreSQL 15+.
-- Apply after migration 001. Currency CU; UTC calendar dates.
BEGIN;
CREATE SCHEMA IF NOT EXISTS analytics;
-- One row per completed order. Preaggregate lines before any other joins.
CREATE OR REPLACE VIEW analytics.completed_order_sales AS
SELECT o.order_id, o.customer_id, (o.placed_at AT TIME ZONE 'UTC')::date AS sales_date,
       SUM(i.quantity * i.unit_price) AS gmv,
       SUM(i.discount_amount) AS discounts,
       SUM(i.quantity * i.unit_price - i.discount_amount) AS sales
FROM public.orders o JOIN public.order_items i USING (order_id)
WHERE o.status = 'completed'
GROUP BY o.order_id, o.customer_id, (o.placed_at AT TIME ZONE 'UTC')::date;

-- Transaction-period convention: sales on placement date, refunds on settlement date.
-- Include refund-only dates. No artificial zero-date calendar.
CREATE OR REPLACE VIEW analytics.daily_revenue AS
WITH sales AS (
 SELECT sales_date AS report_date, COUNT(*) AS completed_orders,
        SUM(gmv) AS gmv, SUM(discounts) AS discounts, SUM(sales) AS sales
 FROM analytics.completed_order_sales GROUP BY sales_date
), refunds AS (
 SELECT (refunded_at AT TIME ZONE 'UTC')::date AS report_date,
        SUM(amount) AS refund_value
 FROM public.refunds WHERE status = 'settled' GROUP BY 1
)
SELECT COALESCE(s.report_date,r.report_date) AS report_date,
       COALESCE(s.completed_orders,0) AS completed_orders,
       COALESCE(s.gmv,0) AS gmv, COALESCE(s.discounts,0) AS discounts,
       COALESCE(s.sales,0) AS sales, COALESCE(r.refund_value,0) AS refund_value,
       COALESCE(s.sales,0)-COALESCE(r.refund_value,0) AS net_sales,
       ROUND(s.sales / NULLIF(s.completed_orders,0),2) AS aov
FROM sales s FULL JOIN refunds r USING (report_date);

-- Recompute weighted AOV rather than averaging daily AOV.
CREATE OR REPLACE VIEW analytics.monthly_revenue AS
SELECT date_trunc('month',report_date::timestamp)::date AS report_month,
       SUM(completed_orders) AS completed_orders, SUM(gmv) AS gmv,
       SUM(discounts) AS discounts, SUM(sales) AS sales,
       SUM(refund_value) AS refund_value, SUM(net_sales) AS net_sales,
       ROUND(SUM(sales)/NULLIF(SUM(completed_orders),0),2) AS aov
FROM analytics.daily_revenue GROUP BY 1;
COMMIT;

-- Acceptance gate: run against populated, quality-checked synthetic data.
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;
DO $$
DECLARE expected_orders bigint; expected_sales numeric; expected_refunds numeric;
        actual_orders numeric; actual_sales numeric; actual_refunds numeric;
BEGIN
 SELECT COUNT(*) INTO expected_orders FROM public.orders WHERE status='completed';
 SELECT COALESCE(SUM(amount),0) INTO expected_sales FROM public.payments WHERE status='captured';
 SELECT COALESCE(SUM(amount),0) INTO expected_refunds FROM public.refunds WHERE status='settled';
 SELECT COALESCE(SUM(completed_orders),0), COALESCE(SUM(sales),0), COALESCE(SUM(refund_value),0)
 INTO actual_orders,actual_sales,actual_refunds FROM analytics.monthly_revenue;
 IF expected_orders=0 THEN RAISE EXCEPTION 'Load synthetic data before acceptance'; END IF;
 IF (actual_orders,actual_sales,actual_refunds) IS DISTINCT FROM
    (expected_orders::numeric,expected_sales,expected_refunds)
 THEN RAISE EXCEPTION 'Revenue mart reconciliation failed'; END IF;
 IF EXISTS (SELECT 1 FROM analytics.daily_revenue
 WHERE sales <> gmv-discounts OR net_sales <> sales-refund_value
 OR (completed_orders=0 AND aov IS NOT NULL))
 THEN RAISE EXCEPTION 'Daily KPI identity failed'; END IF;
 IF EXISTS (
 SELECT 1 FROM public.orders o
 LEFT JOIN analytics.completed_order_sales s USING(order_id)
 LEFT JOIN public.payments p ON p.order_id=o.order_id AND p.status='captured'
 WHERE o.status='completed' AND (s.order_id IS NULL OR p.payment_id IS NULL OR s.sales<>p.amount)
 ) THEN RAISE EXCEPTION 'Per-order reconciliation failed'; END IF;
END $$;
SELECT * FROM analytics.monthly_revenue ORDER BY report_month;
COMMIT;
