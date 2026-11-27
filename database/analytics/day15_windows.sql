-- Day 15 | PostgreSQL 15+ | Advanced SQL casebook
-- Prerequisites: populated schema and accepted Day 14 revenue mart.
-- Run: psql -X -v ON_ERROR_STOP=1 -f database/analytics/day15_windows.sql
-- All dates UTC; monetary values CU; synthetic data only.
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;

-- 1. Customer rankings: ties share ranks; ROW_NUMBER has a stable tie-breaker.
WITH totals AS (
    SELECT customer_id, SUM(sales) AS sales, COUNT(*) AS orders
    FROM analytics.completed_order_sales GROUP BY customer_id
)
SELECT customer_id, sales, orders,
       RANK() OVER (ORDER BY sales DESC) AS sales_rank,
       DENSE_RANK() OVER (ORDER BY sales DESC) AS dense_sales_rank,
       ROW_NUMBER() OVER (ORDER BY sales DESC, customer_id) AS row_num
FROM totals ORDER BY row_num LIMIT 30;

-- 2. Top three revenue ranks per category (ties may return >3 products).
WITH totals AS (
    SELECT p.category_id, p.product_id,
           SUM(i.quantity * i.unit_price - i.discount_amount) AS sales
    FROM public.orders o JOIN public.order_items i USING (order_id)
    JOIN public.products p USING (product_id)
    WHERE o.status = 'completed' GROUP BY p.category_id, p.product_id
), ranked AS (
    SELECT *, DENSE_RANK() OVER (PARTITION BY category_id ORDER BY sales DESC) AS product_rank
    FROM totals
)
SELECT * FROM ranked WHERE product_rank <= 3
ORDER BY category_id, product_rank, product_id;

-- 3. Calendar-day trend, running sales and net sales, trailing seven-day mean.
-- Fill internal inactive dates with zero. Do not extrapolate beyond observed bounds.
-- Partial first six windows are NULL; daily average includes inactive dates.
WITH bounds AS (
    SELECT MIN(report_date) AS first_day, MAX(report_date) AS last_day
    FROM analytics.daily_revenue
), calendar AS (
    SELECT day::date AS report_date
    FROM bounds CROSS JOIN LATERAL
    generate_series(first_day::timestamp, last_day::timestamp, interval '1 day') AS g(day)
), daily AS (
    SELECT c.report_date, COALESCE(r.sales,0) AS sales,
           COALESCE(r.net_sales,0) AS net_sales
    FROM calendar c LEFT JOIN analytics.daily_revenue r USING (report_date)
)
SELECT report_date, sales, net_sales,
       SUM(sales) OVER running AS cumulative_sales,
       SUM(net_sales) OVER running AS cumulative_net_sales,
       LAG(sales) OVER chronological AS previous_day_sales,
       LEAD(sales) OVER chronological AS next_day_sales,
       CASE WHEN COUNT(*) OVER trailing = 7
            THEN ROUND(AVG(sales) OVER trailing,2) END AS sales_ma7
FROM daily
WINDOW chronological AS (ORDER BY report_date),
       running AS (ORDER BY report_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),
       trailing AS (ORDER BY report_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
ORDER BY report_date;

-- 4. Month-over-month growth: fill missing internal months, guard zero denominator.
WITH bounds AS (
    SELECT MIN(report_month) AS first_month, MAX(report_month) AS last_month
    FROM analytics.monthly_revenue
), calendar AS (
    SELECT month::date AS report_month FROM bounds CROSS JOIN LATERAL
    generate_series(first_month::timestamp,last_month::timestamp,interval '1 month') AS g(month)
), monthly AS (
    SELECT c.report_month, COALESCE(r.sales,0) AS sales
    FROM calendar c LEFT JOIN analytics.monthly_revenue r USING (report_month)
), comparison AS (
    SELECT *, LAG(sales) OVER (ORDER BY report_month) AS previous_sales
    FROM monthly
)
SELECT *, ROUND(100 * (sales-previous_sales)/NULLIF(previous_sales,0),2) AS growth_pct
FROM comparison ORDER BY report_month;

-- 5. Customer purchase sequence and days between completed orders.
-- Same-day orders can have zero gap; order_id breaks equal timestamp ties.
WITH sequence AS (
    SELECT order_id, customer_id, placed_at,
           ROW_NUMBER() OVER w AS purchase_number,
           LAG(placed_at) OVER w AS previous_purchase,
           LEAD(placed_at) OVER w AS next_purchase
    FROM public.orders WHERE status='completed'
    WINDOW w AS (PARTITION BY customer_id ORDER BY placed_at, order_id)
)
SELECT *, ROUND(EXTRACT(EPOCH FROM (placed_at-previous_purchase))/86400,2) AS days_since_previous
FROM sequence ORDER BY customer_id,purchase_number LIMIT 100;

-- 6. Monthly contribution to total sales; zero total yields NULL share.
SELECT report_month, sales,
       ROUND(100*sales/NULLIF(SUM(sales) OVER (),0),2) AS sales_share_pct
FROM analytics.monthly_revenue ORDER BY report_month;

-- Deterministic regression fixtures, independent of generated data.
DO $$
DECLARE failures integer;
BEGIN
    WITH fixture(id,sales) AS (VALUES (1,100::numeric),(2,100),(3,50)),
    ranked AS (
        SELECT id,RANK() OVER (ORDER BY sales DESC) AS r,
               DENSE_RANK() OVER (ORDER BY sales DESC) AS d,
               ROW_NUMBER() OVER (ORDER BY sales DESC,id) AS n
        FROM fixture
    ), expected(id,r,d,n) AS (VALUES (1,1,1,1),(2,1,1,2),(3,3,2,3))
    SELECT COUNT(*) INTO failures FROM ranked JOIN expected USING(id)
    WHERE (ranked.r,ranked.d,ranked.n) IS DISTINCT FROM (expected.r,expected.d,expected.n);
    IF failures <> 0 THEN RAISE EXCEPTION 'Ranking fixture failed'; END IF;

    WITH fixture(day,sales) AS (VALUES (1,10::numeric),(3,20),(7,40)),
    daily AS (
        SELECT g.day,COALESCE(f.sales,0) AS sales
        FROM generate_series(1,7) AS g(day) LEFT JOIN fixture f USING(day)
    ), calculated AS (
        SELECT day,SUM(sales) OVER (ORDER BY day ROWS UNBOUNDED PRECEDING) AS total,
               LAG(sales) OVER (ORDER BY day) AS previous,
               LEAD(sales) OVER (ORDER BY day) AS following,
               CASE WHEN COUNT(*) OVER w=7 THEN AVG(sales) OVER w END AS ma
        FROM daily WINDOW w AS (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
    )
    SELECT COUNT(*) INTO failures FROM calculated
    WHERE (day=1 AND (previous IS NOT NULL OR ma IS NOT NULL))
       OR (day=2 AND (previous IS DISTINCT FROM 10::numeric OR following IS DISTINCT FROM 20::numeric))
       OR (day=7 AND (total IS DISTINCT FROM 70::numeric OR ma IS DISTINCT FROM 10::numeric OR following IS NOT NULL))
       OR (day<7 AND ma IS NOT NULL);
    IF failures <> 0 THEN RAISE EXCEPTION 'Calendar/window fixture failed'; END IF;

    IF NOT EXISTS (SELECT 1 FROM analytics.completed_order_sales) THEN
        RAISE EXCEPTION 'Load and validate synthetic data before acceptance';
    END IF;
    IF (SELECT SUM(sales) FROM analytics.daily_revenue) IS DISTINCT FROM
       (SELECT SUM(sales) FROM analytics.completed_order_sales) THEN
        RAISE EXCEPTION 'Daily sales do not reconcile with order sales';
    END IF;
END $$;
COMMIT;
