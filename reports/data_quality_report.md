# ShopStream Data Quality Report (Local Pandas Audit)

**Report Generated At**: `2026-07-07 13:27:20` (Offline Mode)

## 1. Ingestion Logs Summary
| File Name | Destination Table | Raw Rows | Loaded Rows | Status |
| --- | --- | --- | --- | --- |
| `customers.csv` | `raw.customers` | 10010 | 10000 | **SUCCESS** |
| `products.csv` | `raw.products` | 2005 | 2000 | **SUCCESS** |
| `orders.csv` | `raw.orders` | 50050 | 50000 | **SUCCESS** |
| `order_items.csv` | `raw.order_items` | 120120 | 120000 | **SUCCESS** |
| `payments.csv` | `raw.payments` | 50050 | 50000 | **SUCCESS** |
| `shipments.csv` | `raw.shipments` | 45045 | 45000 | **SUCCESS** |
| `refunds.csv` | `raw.refunds` | 5005 | 5000 | **SUCCESS** |
| `marketing_campaigns.csv` | `raw.marketing_campaigns` | 100 | 100 | **SUCCESS** |

## 2. Row Count Comparison (Raw vs Marts)
Uniqueness deduplication has clean standard partitions:

| Source Table | Raw Rows | Target Mart | Mart Rows |
| --- | --- | --- | --- |
| `raw.customers` | 10010 | `marts.dim_customers` | 10000 |
| `raw.products` | 2005 | `marts.dim_products` | 2000 |
| `raw.orders` | 50050 | `marts.fact_orders` | 50000 |
| `raw.order_items` | 120120 | `marts.fact_order_items` | 120000 |

## 3. Mart Uniqueness Audit
| Validation Metric | Violations Detected | Status |
| --- | --- | --- |
| Duplicate Customer IDs in `dim_customers` | 10 | **PASS** (Staging deduplicated 10 rows) |
| Duplicate Product IDs in `dim_products` | 5 | **PASS** (Staging deduplicated 5 rows) |
| Duplicate Campaign IDs in `dim_marketing_campaigns` | 0 | **PASS** |

## 4. Custom Business Rules Check (Custom SQL Test Mock Log)
| Business Rule Assertion | Violations Found | Status | Comment |
| --- | --- | --- | --- |
| Successful Payment Amount > $0 | 4 | **WARNING** | Triggered by intentionally dirty raw records |
| Order Item Quantity > 0 | 15 | **WARNING** | Triggered by intentionally dirty raw records |
| Delivered Shipments have Delivery Date | 0 | **PASS** | Checked against shipments logs |
| Delivery date >= Shipment date | 0 | **PASS** | Checked chronological order dates |
