-- ShopStream Validation and Audit Queries
-- Use these queries to manually verify database consistency, uniqueness, and referential integrity.

-- ==========================================
-- 1. Row Count Validation (Raw vs. Marts)
-- ==========================================
SELECT 'raw.customers' as table_name, count(*) as row_count FROM raw.customers
UNION ALL
SELECT 'marts.dim_customers' as table_name, count(*) as row_count FROM marts.dim_customers
UNION ALL
SELECT 'raw.products' as table_name, count(*) as row_count FROM raw.products
UNION ALL
SELECT 'marts.dim_products' as table_name, count(*) as row_count FROM marts.dim_products
UNION ALL
SELECT 'raw.orders' as table_name, count(*) as row_count FROM raw.orders
UNION ALL
SELECT 'marts.fact_orders' as table_name, count(*) as row_count FROM marts.fact_orders
UNION ALL
SELECT 'raw.order_items' as table_name, count(*) as row_count FROM raw.order_items
UNION ALL
SELECT 'marts.fact_order_items' as table_name, count(*) as row_count FROM marts.fact_order_items;

-- ==========================================
-- 2. Duplicate Primary Key Checks (Should be 0)
-- ==========================================
SELECT 'dim_customers' as table_name, COUNT(*) - COUNT(DISTINCT customer_id) as duplicate_count FROM marts.dim_customers
UNION ALL
SELECT 'dim_products' as table_name, COUNT(*) - COUNT(DISTINCT product_id) as duplicate_count FROM marts.dim_products
UNION ALL
SELECT 'dim_marketing_campaigns' as table_name, COUNT(*) - COUNT(DISTINCT campaign_id) as duplicate_count FROM marts.dim_marketing_campaigns
UNION ALL
SELECT 'fact_orders' as table_name, COUNT(*) - COUNT(DISTINCT order_id) as duplicate_count FROM marts.fact_orders;

-- ==========================================
-- 3. Referential Integrity / Orphan Records (Should be 0)
-- ==========================================

-- Orphan orders (reference non-existent customers)
SELECT COUNT(*) as orphan_orders FROM marts.fact_orders WHERE customer_id NOT IN (SELECT customer_id FROM marts.dim_customers);

-- Orphan order items (reference non-existent orders)
SELECT COUNT(*) as orphan_items FROM marts.fact_order_items WHERE order_id NOT IN (SELECT order_id FROM marts.fact_orders);

-- Orphan order items products (reference non-existent products)
SELECT COUNT(*) as orphan_items_products FROM marts.fact_order_items WHERE product_id NOT IN (SELECT product_id FROM marts.dim_products);

-- Orphan payments (reference non-existent orders)
SELECT COUNT(*) as orphan_payments FROM marts.fact_payments WHERE order_id NOT IN (SELECT order_id FROM marts.fact_orders);

-- Orphan shipments (reference non-existent orders)
SELECT COUNT(*) as orphan_shipments FROM marts.fact_shipments WHERE order_id NOT IN (SELECT order_id FROM marts.fact_orders);

-- Orphan refunds (reference non-existent orders)
SELECT COUNT(*) as orphan_refunds FROM marts.fact_refunds WHERE order_id NOT IN (SELECT order_id FROM marts.fact_orders);


-- ==========================================
-- 4. Business Rule Violations (Should correspond to known dirty records)
-- ==========================================

-- Successful payments with non-positive values
SELECT payment_id, order_id, payment_amount, payment_status 
FROM marts.fact_payments 
WHERE payment_status = 'success' AND payment_amount <= 0;

-- Quantities that are zero or negative
SELECT order_item_id, order_id, quantity 
FROM marts.fact_order_items 
WHERE quantity <= 0;

-- Refund amounts exceeding original order sales
SELECT r.refund_id, r.order_id, r.refund_amount, o.net_revenue 
FROM marts.fact_refunds r
JOIN marts.fact_orders o ON r.order_id = o.order_id
WHERE r.refund_status = 'processed' AND r.refund_amount > o.net_revenue;

-- Shipped deliveries with missing actual delivery dates
SELECT shipment_id, order_id, shipment_status, actual_delivery_date
FROM marts.fact_shipments
WHERE shipment_status = 'delivered' AND actual_delivery_date IS NULL;

-- Chronologically invalid delivery timings
SELECT shipment_id, shipment_date, actual_delivery_date
FROM marts.fact_shipments
WHERE actual_delivery_date < shipment_date;

-- Orders placed in future dates
SELECT order_id, order_date
FROM marts.fact_orders
WHERE order_date > CURRENT_DATE;
