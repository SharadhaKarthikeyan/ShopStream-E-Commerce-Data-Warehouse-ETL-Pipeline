import os
import sys
import pandas as pd
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

def main():
    print("Starting analytical marts export...")
    
    try:
        engine = get_db_connection()
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)
        
    # Ensure processed directory exists
    processed_dir = os.path.join("data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    marts_to_export = [
        "dim_customers",
        "dim_products",
        "fact_orders",
        "mart_daily_revenue",
        "mart_customer_lifetime_value",
        "mart_product_performance",
        "mart_refund_analysis",
        "mart_delivery_performance",
        "mart_campaign_performance"
    ]
    
    print(f"Exporting analytics-ready tables to {processed_dir}...")
    for mart in marts_to_export:
        try:
            query = f"SELECT * FROM marts.{mart};"
            df = pd.read_sql_query(query, engine)
            
            output_path = os.path.join(processed_dir, f"{mart}.csv")
            df.to_csv(output_path, index=False)
            print(f"Successfully exported {len(df)} rows of {mart} -> {output_path}")
        except Exception as e:
            print(f"Failed to export mart {mart}: {e}")
            sys.exit(1)
            
    print("Marts export complete!")

if __name__ == "__main__":
    main()
