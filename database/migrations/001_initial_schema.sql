-- AXIOM Analytics | PostgreSQL 15+ | migration 001
-- Apply to a NEW, EMPTY database with psql -X -v ON_ERROR_STOP=1 -1 -f ...
-- IDs are externally generated deterministic BIGINTs; timestamps are instants.
CREATE TABLE customers (
 customer_id BIGINT PRIMARY KEY,
 created_at TIMESTAMPTZ NOT NULL,
 region VARCHAR(80) NOT NULL CONSTRAINT chk_customers_region CHECK (length(btrim(region)) > 0),
 acquisition_source VARCHAR(40) NOT NULL CONSTRAINT chk_customers_source CHECK (acquisition_source IN ('organic','paid_search','social','referral','direct'))
);
CREATE TABLE categories (
 category_id BIGINT PRIMARY KEY,
 category_name VARCHAR(100) NOT NULL UNIQUE,
 CONSTRAINT chk_categories_name CHECK (length(btrim(category_name)) > 0)
);
CREATE TABLE products (
 product_id BIGINT PRIMARY KEY,
 category_id BIGINT NOT NULL CONSTRAINT fk_products_category REFERENCES categories(category_id),
 product_name VARCHAR(160) NOT NULL,
 list_price NUMERIC(14,2) NOT NULL CONSTRAINT chk_products_price CHECK (list_price >= 0),
 active BOOLEAN NOT NULL DEFAULT TRUE,
 CONSTRAINT chk_products_name CHECK (length(btrim(product_name)) > 0)
);
CREATE TABLE campaigns (
 campaign_id BIGINT PRIMARY KEY,
 campaign_name VARCHAR(120) NOT NULL,
 channel VARCHAR(40) NOT NULL,
 start_date DATE NOT NULL,
 end_date DATE NOT NULL,
 spend NUMERIC(14,2) NOT NULL CONSTRAINT chk_campaigns_spend CHECK (spend >= 0),
 CONSTRAINT chk_campaigns_dates CHECK (end_date >= start_date),
 CONSTRAINT chk_campaigns_name CHECK (length(btrim(campaign_name)) > 0),
 CONSTRAINT chk_campaigns_channel CHECK (length(btrim(channel)) > 0)
);
CREATE TABLE orders (
 order_id BIGINT PRIMARY KEY,
 customer_id BIGINT NOT NULL CONSTRAINT fk_orders_customer REFERENCES customers(customer_id),
 placed_at TIMESTAMPTZ NOT NULL,
 status VARCHAR(20) NOT NULL CONSTRAINT chk_orders_status CHECK (status IN ('placed','completed','cancelled','expired'))
);
CREATE TABLE order_items (
 order_item_id BIGINT PRIMARY KEY,
 order_id BIGINT NOT NULL CONSTRAINT fk_order_items_order REFERENCES orders(order_id),
 product_id BIGINT NOT NULL CONSTRAINT fk_order_items_product REFERENCES products(product_id),
 quantity INTEGER NOT NULL CONSTRAINT chk_order_items_quantity CHECK (quantity > 0),
 unit_price NUMERIC(14,2) NOT NULL CONSTRAINT chk_order_items_price CHECK (unit_price >= 0),
 discount_amount NUMERIC(14,2) NOT NULL CONSTRAINT chk_order_items_discount CHECK (discount_amount >= 0 AND discount_amount <= quantity::numeric * unit_price)
);
CREATE TABLE payments (
 payment_id BIGINT PRIMARY KEY,
 order_id BIGINT NOT NULL CONSTRAINT fk_payments_order REFERENCES orders(order_id),
 attempted_at TIMESTAMPTZ NOT NULL,
 amount NUMERIC(14,2) NOT NULL CONSTRAINT chk_payments_amount CHECK (amount > 0),
 status VARCHAR(20) NOT NULL CONSTRAINT chk_payments_status CHECK (status IN ('pending','failed','captured'))
);
CREATE TABLE refunds (
 refund_id BIGINT PRIMARY KEY,
 payment_id BIGINT NOT NULL CONSTRAINT fk_refunds_payment REFERENCES payments(payment_id),
 requested_at TIMESTAMPTZ NOT NULL,
 refunded_at TIMESTAMPTZ,
 amount NUMERIC(14,2) NOT NULL CONSTRAINT chk_refunds_amount CHECK (amount > 0),
 status VARCHAR(20) NOT NULL CONSTRAINT chk_refunds_status CHECK (status IN ('pending','failed','settled')),
 reason VARCHAR(100) NOT NULL,
 CONSTRAINT chk_refunds_reason CHECK (length(btrim(reason)) > 0),
 CONSTRAINT chk_refunds_settlement_timestamp CHECK (
   (status = 'settled' AND refunded_at IS NOT NULL AND refunded_at >= requested_at)
   OR (status <> 'settled' AND refunded_at IS NULL)
 )
);
CREATE TABLE sessions (
 session_id BIGINT PRIMARY KEY,
 customer_id BIGINT CONSTRAINT fk_sessions_customer REFERENCES customers(customer_id),
 campaign_id BIGINT CONSTRAINT fk_sessions_campaign REFERENCES campaigns(campaign_id),
 started_at TIMESTAMPTZ NOT NULL,
 ended_at TIMESTAMPTZ NOT NULL,
 CONSTRAINT chk_sessions_dates CHECK (ended_at > started_at)
);
CREATE TABLE events (
 event_id BIGINT PRIMARY KEY,
 session_id BIGINT NOT NULL CONSTRAINT fk_events_session REFERENCES sessions(session_id),
 occurred_at TIMESTAMPTZ NOT NULL,
 event_type VARCHAR(30) NOT NULL CONSTRAINT chk_events_type CHECK (event_type IN ('session_start','product_view','add_to_cart','checkout_start','purchase')),
 order_id BIGINT CONSTRAINT fk_events_order REFERENCES orders(order_id),
 product_id BIGINT CONSTRAINT fk_events_product REFERENCES products(product_id),
 CONSTRAINT chk_events_purchase_order CHECK (event_type <> 'purchase' OR order_id IS NOT NULL),
 CONSTRAINT chk_events_product_reference CHECK (event_type NOT IN ('product_view','add_to_cart') OR product_id IS NOT NULL)
);
CREATE UNIQUE INDEX uq_payments_captured_order ON payments(order_id) WHERE status = 'captured';
CREATE INDEX idx_orders_customer_placed ON orders(customer_id, placed_at);
CREATE INDEX idx_orders_placed_status ON orders(placed_at, status);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_payments_order ON payments(order_id);
CREATE INDEX idx_refunds_payment_settled ON refunds(payment_id, refunded_at) WHERE status = 'settled';
CREATE INDEX idx_sessions_customer_start ON sessions(customer_id, started_at);
CREATE INDEX idx_sessions_campaign ON sessions(campaign_id);
CREATE INDEX idx_events_session_time ON events(session_id, occurred_at, event_id);
CREATE INDEX idx_events_order ON events(order_id) WHERE order_id IS NOT NULL;
CREATE INDEX idx_products_category ON products(category_id);
