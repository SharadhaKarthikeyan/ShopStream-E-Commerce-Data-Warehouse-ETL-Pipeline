# ShopStream Data Dictionary

This document registers metadata descriptions for tables and columns in the `raw` and `marts` schemas of the `shopstream_dw` database.

---

## 1. Raw Schema (`raw`)

These tables are clean replicas of the raw ingestion CSV datasets.

### `raw.customers`
* **`customer_id`** (VARCHAR, PK): Unique customer identifier.
* **`first_name`** (VARCHAR): Customer's first name.
* **`last_name`** (VARCHAR): Customer's last name.
* **`email`** (VARCHAR): E-mail address.
* **`signup_date`** (DATE): Sign up date.
* **`city`** (VARCHAR): Geographic city.
* **`state`** (VARCHAR): Geographic state.
* **`country`** (VARCHAR): Geographic country (always USA).
* **`customer_segment`** (VARCHAR): Behavioral classification (e.g. Gamers, Seniors, Fashionistas).

### `raw.products`
* **`product_id`** (VARCHAR, PK): Unique product identifier.
* **`product_name`** (VARCHAR): Item name.
* **`category`** (VARCHAR): Main product department.
* **`subcategory`** (VARCHAR): Specific product type.
* **`brand`** (VARCHAR): Product manufacturer.
* **`unit_price`** (NUMERIC): Selling price.
* **`cost_price`** (NUMERIC): Cost of goods sold.
* **`active_flag`** (VARCHAR): Active/Inactive flag (dirty casing).

### `raw.orders`
* **`order_id`** (VARCHAR, PK): Unique purchase transaction code.
* **`customer_id`** (VARCHAR): ID of the customer who ordered.
* **`order_date`** (DATE): Transaction date.
* **`order_status`** (VARCHAR): Order progress state.
* **`campaign_id`** (VARCHAR): Campaign attribution ID (can be NULL).

### `raw.order_items`
* **`order_item_id`** (VARCHAR, PK): Individual order line item code.
* **`order_id`** (VARCHAR): Parent order ID.
* **`product_id`** (VARCHAR): Ordered product ID.
* **`quantity`** (INT): Units purchased.
* **`unit_price`** (NUMERIC): Unit selling price.
* **`discount`** (NUMERIC): Promotional price discount.
* **`tax`** (NUMERIC): Sales tax applied.
* **`item_total`** (NUMERIC): Net total for line item.

### `raw.payments`
* **`payment_id`** (VARCHAR, PK): Transaction ID.
* **`order_id`** (VARCHAR): Linked order ID.
* **`payment_method`** (VARCHAR): Payment channel.
* **`payment_status`** (VARCHAR): Success/Failure status.
* **`payment_amount`** (NUMERIC): Amount paid.
* **`currency`** (VARCHAR): Payment currency.
* **`transaction_id`** (VARCHAR): Payment provider ID.
* **`payment_date`** (TIMESTAMP): Time of transaction.

### `raw.shipments`
* **`shipment_id`** (VARCHAR, PK): Unique tracking shipment code.
* **`order_id`** (VARCHAR): Linked order ID.
* **`shipment_date`** (DATE): Ship date.
* **`expected_delivery_date`** (DATE): Expected delivery date.
* **`actual_delivery_date`** (DATE): Actual delivery date.
* **`shipping_provider`** (VARCHAR): Carrier company.
* **`shipment_status`** (VARCHAR): Shipping progress state.

### `raw.refunds`
* **`refund_id`** (VARCHAR, PK): Refund log code.
* **`order_id`** (VARCHAR): Linked order ID.
* **`refund_reason`** (VARCHAR): Reason for refund.
* **`refund_status`** (VARCHAR): Refund progress state.
* **`refund_amount`** (NUMERIC): Value refunded.
* **`refund_date`** (DATE): Refund processing date.

### `raw.ingestion_log`
* **`log_id`** (INT, PK): Log auto-incrementing ID.
* **`file_name`** (VARCHAR): Input CSV file name.
* **`table_name`** (VARCHAR): Dest table.
* **`rows_loaded`** (INT): Loaded row volume.
* **`load_status`** (VARCHAR): Ingestion status.
* **`loaded_at`** (TIMESTAMP): Timestamp of run.
* **`error_message`** (TEXT): Log error message details if failed.

---

## 2. Mart Schema (`marts`)

These dimensional and analytics tables are populated by dbt after staging, deduplication, and transformation.

### `marts.dim_customers`
* **`customer_id`** (VARCHAR, PK): Primary customer ID.
* **`full_name`** (VARCHAR): Combined first and last name.
* **`email`** (VARCHAR): Normalized email.
* **`signup_date`** (DATE): Signup date.
* **`city`** / **`state`** / **`country`** (VARCHAR): Geographic details.
* **`customer_segment`** (VARCHAR): Standardized segment.
* **`total_orders`** (INT): Total orders placed.
* **`first_order_date`** / **`last_order_date`** (DATE): First and last transactions.
* **`lifetime_value`** (NUMERIC): Customer lifetime spend.
* **`average_order_value`** (NUMERIC): Average purchase value.
* **`is_repeat_customer`** (BOOLEAN): Flag indicating if customer placed > 1 order.

### `marts.dim_products`
* **`product_id`** (VARCHAR, PK): Unique product code.
* **`product_name`** / **`category`** / **`subcategory`** / **`brand`** (VARCHAR): Product attributes.
* **`unit_price`** (NUMERIC): Retail price.
* **`cost_price`** (NUMERIC): Product acquisition cost.
* **`markup_amount`** (NUMERIC): Net markup ($).
* **`markup_pct`** (NUMERIC): Profit markup (%).
* **`is_active`** (BOOLEAN): Flag for catalog active status.

### `marts.dim_marketing_campaigns`
* **`campaign_id`** (VARCHAR, PK): Campaign code (includes `organic`).
* **`campaign_name`** (VARCHAR): Campaign name.
* **`channel`** (VARCHAR): Channel (e.g. Facebook, Instagram).
* **`budget`** (NUMERIC): Total budget.
* **`start_date`** / **`end_date`** (DATE): Timing logs.
* **`target_segment`** (VARCHAR): Target segment name.

### `marts.fact_orders`
* **`order_id`** (VARCHAR, PK): Unique order code.
* **`customer_id`** (VARCHAR, FK): References `dim_customers`.
* **`campaign_id`** (VARCHAR, FK): References `dim_marketing_campaigns`.
* **`order_date`** (DATE, FK): References `dim_date`.
* **`order_status`** (VARCHAR): Standardized order state.
* **`gross_revenue`** (NUMERIC): Gross order amount (items * price).
* **`total_discount`** (NUMERIC): Accumulated discount.
* **`total_tax`** (NUMERIC): Accumulated sales tax.
* **`net_revenue`** (NUMERIC): Total net revenue (gross - discount + tax).
* **`total_items`** (INT): Total unit items in order.
* **`refunded_amount`** (NUMERIC): Actual refunded amount if applicable.
* **`is_refunded`** (BOOLEAN): True if there was a processed refund.

### `marts.fact_order_items`
* **`order_item_id`** (VARCHAR, PK): Unique line item code.
* **`order_id`** (VARCHAR, FK): Link to order.
* **`product_id`** (VARCHAR, FK): Link to product.
* **`customer_id`** (VARCHAR, FK): Link to customer.
* **`campaign_id`** (VARCHAR, FK): Link to campaign.
* **`order_date`** (DATE): Date of purchase.
* **`quantity`** (INT): Quantity purchased.
* **`unit_price`** (NUMERIC): Retail price.
* **`discount`** (NUMERIC): Product discount.
* **`tax`** (NUMERIC): Tax applied.
* **`item_total`** (NUMERIC): Total line value.

### `marts.fact_payments`
* **`payment_id`** (VARCHAR, PK): Payment ID.
* **`order_id`** (VARCHAR, FK): Link to order.
* **`customer_id`** (VARCHAR, FK): Link to customer.
* **`order_date`** (DATE): Order date.
* **`payment_method`** / **`payment_status`** (VARCHAR): Payment details.
* **`payment_amount`** (NUMERIC): Total payment.
* **`currency`** (VARCHAR): USD.
* **`transaction_id`** (VARCHAR): Transaction string.
* **`payment_date`** (TIMESTAMP): Time of transaction.

### `marts.fact_shipments`
* **`shipment_id`** (VARCHAR, PK): Shipping ID.
* **`order_id`** (VARCHAR, FK): Link to order.
* **`customer_id`** (VARCHAR, FK): Link to customer.
* **`order_date`** (DATE): Order date.
* **`shipment_date`** / **`expected_delivery_date`** / **`actual_delivery_date`** (DATE): Tracking dates.
* **`shipping_provider`** (VARCHAR): Carrier.
* **`shipment_status`** (VARCHAR): Shipping state.
* **`delivery_duration_days`** (INT): Duration between ship and delivery.
* **`is_delayed`** (INT): Delayed delivery flag (1 = delayed, 0 = on time).

### `marts.fact_refunds`
* **`refund_id`** (VARCHAR, PK): Refund ID.
* **`order_id`** (VARCHAR, FK): Link to order.
* **`customer_id`** (VARCHAR, FK): Link to customer.
* **`order_date`** (DATE): Order date.
* **`refund_date`** (DATE): Refund processing date.
* **`refund_reason`** / **`refund_status`** (VARCHAR): Refund details.
* **`refund_amount`** (NUMERIC): Refunded value.
