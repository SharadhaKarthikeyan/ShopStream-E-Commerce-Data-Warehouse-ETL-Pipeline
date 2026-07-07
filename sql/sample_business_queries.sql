-- ShopStream Sample Business Queries
-- These queries leverage the analytical tables in the marts schema.

-- 1. Daily Revenue Trend (Excluding cancelled orders)
SELECT 
    order_date,
    total_orders,
    net_revenue,
    average_order_value,
    total_items_sold
FROM marts.mart_daily_revenue
ORDER BY order_date DESC
LIMIT 30;

-- 2. Top Product Categories by Revenue
SELECT 
    category,
    COUNT(DISTINCT product_id) as unique_products_sold,
    SUM(total_units_sold) as total_units,
    SUM(net_revenue) as total_revenue,
    SUM(gross_profit) as total_profit,
    ROUND(SUM(gross_profit) / NULLIF(SUM(net_revenue), 0), 4) as profit_margin
FROM marts.mart_product_performance
GROUP BY category
ORDER BY total_revenue DESC;

-- 3. Top 10 Customers by Lifetime Value (LTV)
SELECT 
    ltv_rank,
    customer_id,
    full_name,
    customer_segment,
    total_orders,
    lifetime_value,
    average_order_value
FROM marts.mart_customer_lifetime_value
ORDER BY lifetime_value DESC
LIMIT 10;

-- 4. Shipping Providers with Highest Delay Rates
SELECT 
    shipping_provider,
    total_shipments,
    completed_deliveries,
    average_delivery_days,
    delayed_shipments,
    ROUND(delay_rate * 100, 2) as delay_percentage
FROM marts.mart_delivery_performance
ORDER BY delay_rate DESC;

-- 5. Product Categories with Highest Refund Rates (by unit and revenue)
SELECT 
    category,
    SUM(total_units_sold) as units_sold,
    SUM(order_refund_count) as total_refunds,
    SUM(net_revenue) as category_sales,
    SUM(estimated_refund_amount) as total_refund_amount,
    ROUND((SUM(estimated_refund_amount) / NULLIF(SUM(net_revenue), 0)) * 100, 2) as revenue_refund_percentage
FROM marts.mart_product_performance
GROUP BY category
ORDER BY revenue_refund_percentage DESC;

-- 6. Marketing Campaign Performance and ROI
SELECT 
    campaign_name,
    channel,
    budget,
    total_orders,
    total_revenue,
    campaign_roi as revenue_per_campaign_dollar
FROM marts.mart_campaign_performance
WHERE campaign_id <> 'organic'
ORDER BY total_revenue DESC;

-- 7. Payment Method Failure Rates
SELECT 
    payment_method,
    COUNT(payment_id) as total_transactions,
    COUNT(CASE WHEN LOWER(payment_status) = 'failed' THEN 1 END) as failed_transactions,
    ROUND((COUNT(CASE WHEN LOWER(payment_status) = 'failed' THEN 1 END)::NUMERIC / COUNT(payment_id)) * 100, 2) as failure_percentage
FROM marts.fact_payments
GROUP BY payment_method
ORDER BY failure_percentage DESC;
