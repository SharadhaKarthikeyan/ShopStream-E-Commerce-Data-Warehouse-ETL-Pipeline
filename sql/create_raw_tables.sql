-- Create target database schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

-- Drop existing tables to support idempotent initial runs
DROP TABLE IF EXISTS raw.ingestion_log CASCADE;
DROP TABLE IF EXISTS raw.refunds CASCADE;
DROP TABLE IF EXISTS raw.shipments CASCADE;
DROP TABLE IF EXISTS raw.payments CASCADE;
DROP TABLE IF EXISTS raw.order_items CASCADE;
DROP TABLE IF EXISTS raw.orders CASCADE;
DROP TABLE IF EXISTS raw.products CASCADE;
DROP TABLE IF EXISTS raw.customers CASCADE;
DROP TABLE IF EXISTS raw.marketing_campaigns CASCADE;

-- 1. Marketing Campaigns Table
CREATE TABLE raw.marketing_campaigns (
    campaign_id VARCHAR(100),
    campaign_name VARCHAR(100),
    channel VARCHAR(100),
    budget NUMERIC(12, 2),
    start_date DATE,
    end_date DATE,
    target_segment VARCHAR(100)
);

-- 2. Customers Table
CREATE TABLE raw.customers (
    customer_id VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(150),
    signup_date DATE,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    customer_segment VARCHAR(100)
);

-- 3. Products Table
CREATE TABLE raw.products (
    product_id VARCHAR(100),
    product_name VARCHAR(200),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    unit_price NUMERIC(12, 2),
    cost_price NUMERIC(12, 2),
    active_flag VARCHAR(50)
);

-- 4. Orders Table
CREATE TABLE raw.orders (
    order_id VARCHAR(100),
    customer_id VARCHAR(100),
    order_date DATE,
    order_status VARCHAR(100),
    campaign_id VARCHAR(100)
);

-- 5. Order Items Table
CREATE TABLE raw.order_items (
    order_item_id VARCHAR(100),
    order_id VARCHAR(100),
    product_id VARCHAR(100),
    quantity INT,
    unit_price NUMERIC(12, 2),
    discount NUMERIC(12, 2),
    tax NUMERIC(12, 2),
    item_total NUMERIC(12, 2)
);

-- 6. Payments Table
CREATE TABLE raw.payments (
    payment_id VARCHAR(100),
    order_id VARCHAR(100),
    payment_method VARCHAR(100),
    payment_status VARCHAR(100),
    payment_amount NUMERIC(12, 2),
    currency VARCHAR(50),
    transaction_id VARCHAR(150),
    payment_date TIMESTAMP
);

-- 7. Shipments Table
CREATE TABLE raw.shipments (
    shipment_id VARCHAR(100),
    order_id VARCHAR(100),
    shipment_date DATE,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    shipping_provider VARCHAR(100),
    shipment_status VARCHAR(100)
);

-- 8. Refunds Table
CREATE TABLE raw.refunds (
    refund_id VARCHAR(100),
    order_id VARCHAR(100),
    refund_reason VARCHAR(200),
    refund_status VARCHAR(100),
    refund_amount NUMERIC(12, 2),
    refund_date DATE
);

-- 9. Ingestion Log Table (Keeps serial PK for audit logs)
CREATE TABLE raw.ingestion_log (
    log_id SERIAL PRIMARY KEY,
    file_name VARCHAR(150),
    table_name VARCHAR(100),
    rows_loaded INT,
    load_status VARCHAR(50),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT
);
