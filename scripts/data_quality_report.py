import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

def get_db_connection():
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_name = os.getenv("DB_NAME", "shopstream_dw")
    
    connection_uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(connection_uri)

def run_query_val(engine, query):
    with engine.connect() as conn:
        result = conn.execute(text(query)).fetchone()
        return result[0] if result else 0

def main():
    print("Generating Data Quality Report...")
    
    try:
        engine = get_db_connection()
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)
        
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    report_file_path = os.path.join(reports_dir, "data_quality_report.md")
    
    # 1. Row counts of raw tables
    raw_tables = [
        "marketing_campaigns", "customers", "products", 
        "orders", "order_items", "payments", "shipments", "refunds"
    ]
    raw_counts = {}
    for table in raw_tables:
        raw_counts[table] = run_query_val(engine, f"SELECT count(*) FROM raw.{table}")
        
    # 2. Row counts of marts tables
    mart_tables = [
        "dim_customers", "dim_products", "dim_marketing_campaigns",
        "fact_orders", "fact_order_items", "fact_payments", "fact_shipments", "fact_refunds",
        "mart_daily_revenue", "mart_customer_lifetime_value", "mart_product_performance",
        "mart_refund_analysis", "mart_delivery_performance", "mart_campaign_performance"
    ]
    mart_counts = {}
    for table in mart_tables:
        try:
            mart_counts[table] = run_query_val(engine, f"SELECT count(*) FROM marts.{table}")
        except Exception:
            mart_counts[table] = "N/A (Not built yet)"
            
    # 3. Check for duplicates in dimensions (should be 0)
    customer_duplicates = run_query_val(engine, """
        SELECT count(*) - count(distinct customer_id) FROM marts.dim_customers
    """)
    product_duplicates = run_query_val(engine, """
        SELECT count(*) - count(distinct product_id) FROM marts.dim_products
    """)
    campaign_duplicates = run_query_val(engine, """
        SELECT count(*) - count(distinct campaign_id) FROM marts.dim_marketing_campaigns
    """)
    
    # 4. Check for orphan records in facts (should be 0)
    orphan_orders = run_query_val(engine, """
        SELECT count(*) FROM marts.fact_orders 
        WHERE customer_id NOT IN (SELECT customer_id FROM marts.dim_customers)
    """)
    orphan_items = run_query_val(engine, """
        SELECT count(*) FROM marts.fact_order_items
        WHERE order_id NOT IN (SELECT order_id FROM marts.fact_orders)
    """)
    orphan_items_products = run_query_val(engine, """
        SELECT count(*) FROM marts.fact_order_items
        WHERE product_id NOT IN (SELECT product_id FROM marts.dim_products)
    """)
    orphan_payments = run_query_val(engine, """
        SELECT count(*) FROM marts.fact_payments
        WHERE order_id NOT IN (SELECT order_id FROM marts.fact_orders)
    """)
    orphan_shipments = run_query_val(engine, """
        SELECT count(*) FROM marts.fact_shipments
        WHERE order_id NOT IN (SELECT order_id FROM marts.fact_orders)
    """)
    orphan_refunds = run_query_val(engine, """
        SELECT count(*) FROM marts.fact_refunds
        WHERE order_id NOT IN (SELECT order_id FROM marts.fact_orders)
    """)
    
    # 5. Check business rule violations (should be 0 if data conforms or tests pass)
    negative_payments = run_query_val(engine, """
        SELECT count(*) FROM marts.fact_payments 
        WHERE payment_status = 'success' AND payment_amount <= 0
    """)
    negative_quantities = run_query_val(engine, """
        SELECT count(*) FROM marts.fact_order_items WHERE quantity <= 0
    """)
    excessive_refunds = run_query_val(engine, """
        SELECT count(*) FROM marts.fact_refunds r
        JOIN marts.fact_orders o ON r.order_id = o.order_id
        WHERE r.refund_status = 'processed' AND r.refund_amount > o.net_revenue
    """)
    null_delivery_shipped = run_query_val(engine, """
        SELECT count(*) FROM marts.fact_shipments 
        WHERE shipment_status = 'delivered' AND actual_delivery_date IS NULL
    """)
    invalid_delivery_dates = run_query_val(engine, """
        SELECT count(*) FROM marts.fact_shipments WHERE actual_delivery_date < shipment_date
    """)
    future_orders = run_query_val(engine, """
        SELECT count(*) FROM marts.fact_orders WHERE order_date > CURRENT_DATE
    """)
    
    # 6. Retrieve Ingestion Logs
    ingestion_logs = []
    try:
        with engine.connect() as conn:
            logs = conn.execute(text("""
                SELECT file_name, table_name, rows_loaded, load_status, loaded_at 
                FROM raw.ingestion_log 
                ORDER BY loaded_at DESC LIMIT 15
            """)).fetchall()
            for log in logs:
                ingestion_logs.append({
                    "file_name": log[0],
                    "table_name": log[1],
                    "rows_loaded": log[2],
                    "status": log[3],
                    "loaded_at": log[4].strftime('%Y-%m-%d %H:%M:%S')
                })
    except Exception as e:
        print(f"Failed to read ingestion logs: {e}")
        
    # Write report
    print(f"Writing report to {report_file_path}...")
    with open(report_file_path, "w") as f:
        f.write("# ShopStream Data Quality Report\n\n")
        f.write(f"**Report Generated At**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n")
        
        f.write("## 1. Ingestion Logs Summary\n")
        f.write("| File Name | Table Name | Rows Loaded | Status | Loaded At |\n")
        f.write("| --- | --- | --- | --- | --- |\n")
        for log in ingestion_logs:
            f.write(f"| `{log['file_name']}` | `raw.{log['table_name']}` | {log['rows_loaded']} | **{log['status']}** | {log['loaded_at']} |\n")
        f.write("\n")
        
        f.write("## 2. Row Count Comparison (Raw vs Marts)\n")
        f.write("Since dbt filters/deduplicates duplicates, some row counts in the marts layer will be slightly lower than raw files.\n\n")
        f.write("| Table (Raw Schema) | Raw Count | Table (Marts Schema) | Mart Count |\n")
        f.write("| --- | --- | --- | --- |\n")
        f.write(f"| `raw.customers` | {raw_counts['customers']} | `marts.dim_customers` | {mart_counts['dim_customers']} |\n")
        f.write(f"| `raw.products` | {raw_counts['products']} | `marts.dim_products` | {mart_counts['dim_products']} |\n")
        f.write(f"| `raw.marketing_campaigns` | {raw_counts['marketing_campaigns']} | `marts.dim_marketing_campaigns` | {mart_counts['dim_marketing_campaigns']} (includes organic row) |\n")
        f.write(f"| `raw.orders` | {raw_counts['orders']} | `marts.fact_orders` | {mart_counts['fact_orders']} |\n")
        f.write(f"| `raw.order_items` | {raw_counts['order_items']} | `marts.fact_order_items` | {mart_counts['fact_order_items']} |\n")
        f.write(f"| `raw.payments` | {raw_counts['payments']} | `marts.fact_payments` | {mart_counts['fact_payments']} |\n")
        f.write(f"| `raw.shipments` | {raw_counts['shipments']} | `marts.fact_shipments` | {mart_counts['fact_shipments']} |\n")
        f.write(f"| `raw.refunds` | {raw_counts['refunds']} | `marts.fact_refunds` | {mart_counts['fact_refunds']} |\n")
        f.write("\n")
        
        f.write("## 3. Mart Table Row Counts\n")
        f.write("| Mart Analytics Table | Row Count |\n")
        f.write("| --- | --- |\n")
        f.write(f"| `marts.mart_daily_revenue` | {mart_counts['mart_daily_revenue']} |\n")
        f.write(f"| `marts.mart_customer_lifetime_value` | {mart_counts['mart_customer_lifetime_value']} |\n")
        f.write(f"| `marts.mart_product_performance` | {mart_counts['mart_product_performance']} |\n")
        f.write(f"| `marts.mart_refund_analysis` | {mart_counts['mart_refund_analysis']} |\n")
        f.write(f"| `marts.mart_delivery_performance` | {mart_counts['mart_delivery_performance']} |\n")
        f.write(f"| `marts.mart_campaign_performance` | {mart_counts['mart_campaign_performance']} |\n")
        f.write("\n")
        
        f.write("## 4. Key Uniqueness and Integrity Assertions\n")
        f.write("| Validation Check | Count of Violations | Status |\n")
        f.write("| --- | --- | --- |\n")
        
        status_c_dup = "PASS" if customer_duplicates == 0 else "FAIL"
        f.write(f"| Duplicate Customer IDs in `dim_customers` | {customer_duplicates} | **{status_c_dup}** |\n")
        
        status_p_dup = "PASS" if product_duplicates == 0 else "FAIL"
        f.write(f"| Duplicate Product IDs in `dim_products` | {product_duplicates} | **{status_p_dup}** |\n")
        
        status_m_dup = "PASS" if campaign_duplicates == 0 else "FAIL"
        f.write(f"| Duplicate Campaign IDs in `dim_marketing_campaigns` | {campaign_duplicates} | **{status_m_dup}** |\n")
        
        status_o_order = "PASS" if orphan_orders == 0 else "FAIL"
        f.write(f"| Orphan Orders (customer not in `dim_customers`) | {orphan_orders} | **{status_o_order}** |\n")
        
        status_o_item = "PASS" if orphan_items == 0 else "FAIL"
        f.write(f"| Orphan Order Items (order not in `fact_orders`) | {orphan_items} | **{status_o_item}** |\n")
        
        status_o_item_p = "PASS" if orphan_items_products == 0 else "FAIL"
        f.write(f"| Orphan Order Items (product not in `dim_products`) | {orphan_items_products} | **{status_o_item_p}** |\n")
        
        status_o_pay = "PASS" if orphan_payments == 0 else "FAIL"
        f.write(f"| Orphan Payments (order not in `fact_orders`) | {orphan_payments} | **{status_o_pay}** |\n")
        
        status_o_ship = "PASS" if orphan_shipments == 0 else "FAIL"
        f.write(f"| Orphan Shipments (order not in `fact_orders`) | {orphan_shipments} | **{status_o_ship}** |\n")
        
        status_o_ref = "PASS" if orphan_refunds == 0 else "FAIL"
        f.write(f"| Orphan Refunds (order not in `fact_orders`) | {orphan_refunds} | **{status_o_ref}** |\n")
        
        f.write("\n")
        
        f.write("## 5. Custom Business Rules Check (Custom SQL Test Log)\n")
        f.write("| Business Rule Assertion | Violations Found | Status | Comment |\n")
        f.write("| --- | --- | --- | --- |\n")
        
        status_neg_p = "WARNING" if negative_payments > 0 else "PASS"
        f.write(f"| Successful Payment Amount > $0 | {negative_payments} | **{status_neg_p}** | Triggered by intentionally dirty raw records |\n")
        
        status_neg_q = "WARNING" if negative_quantities > 0 else "PASS"
        f.write(f"| Order Item Quantity > 0 | {negative_quantities} | **{status_neg_q}** | Triggered by intentionally dirty raw records |\n")
        
        status_exc_r = "WARNING" if excessive_refunds > 0 else "PASS"
        f.write(f"| Refund amount <= Order Net Amount | {excessive_refunds} | **{status_exc_r}** | Triggered by intentionally dirty raw records |\n")
        
        status_null_d = "PASS" if null_delivery_shipped == 0 else "FAIL"
        f.write(f"| Delivered Shipments have Delivery Date | {null_delivery_shipped} | **{status_null_d}** | Core schema requirement |\n")
        
        status_inv_d = "PASS" if invalid_delivery_dates == 0 else "FAIL"
        f.write(f"| Delivery date >= Shipment date | {invalid_delivery_dates} | **{status_inv_d}** | Chronological integrity check |\n")
        
        status_fut_o = "PASS" if future_orders == 0 else "FAIL"
        f.write(f"| Order Date is not in future | {future_orders} | **{status_fut_o}** | Temporal consistency check |\n")
        
    print(f"Data Quality Report successfully written to {report_file_path}")

if __name__ == "__main__":
    main()
