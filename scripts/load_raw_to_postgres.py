import os
import sys
import pandas as pd
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
    print(f"Connecting to database: postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")
    return create_engine(connection_uri)

def run_ddl_initialization(engine):
    sql_path = os.path.join("sql", "create_raw_tables.sql")
    if not os.path.exists(sql_path):
        print(f"Error: Schema script not found at {sql_path}")
        sys.exit(1)
        
    print(f"Executing DDL initialization from {sql_path}...")
    with open(sql_path, "r") as f:
        ddl_sql = f.read()
        
    # Split queries by semicolon to execute them properly, or run them as a block
    with engine.begin() as connection:
        connection.execute(text(ddl_sql))
    print("Database DDL initialization completed successfully.")

def log_ingestion(engine, file_name, table_name, rows_loaded, status, error_message=None):
    log_query = """
    INSERT INTO raw.ingestion_log (file_name, table_name, rows_loaded, load_status, loaded_at, error_message)
    VALUES (:file_name, :table_name, :rows_loaded, :load_status, :loaded_at, :error_message);
    """
    with engine.begin() as connection:
        connection.execute(text(log_query), {
            "file_name": file_name,
            "table_name": table_name,
            "rows_loaded": rows_loaded,
            "load_status": status,
            "loaded_at": datetime.now(),
            "error_message": error_message
        })

def load_csv_to_postgres(engine, csv_name, table_name):
    csv_path = os.path.join("data", "raw", csv_name)
    
    if not os.path.exists(csv_path):
        error_msg = f"Missing raw CSV file: {csv_path}"
        print(f"Error: {error_msg}")
        log_ingestion(engine, csv_name, table_name, 0, "FAILED", error_msg)
        raise FileNotFoundError(error_msg)
        
    print(f"Loading {csv_name} into raw.{table_name}...")
    try:
        df = pd.read_csv(csv_path)
        row_count = len(df)
        
        # Write to PostgreSQL
        df.to_sql(
            name=table_name,
            con=engine,
            schema="raw",
            if_exists="append",
            index=False,
            method="multi"
        )
        
        log_ingestion(engine, csv_name, table_name, row_count, "SUCCESS")
        print(f"Successfully loaded {row_count} rows into raw.{table_name}")
        return row_count
    except Exception as e:
        error_msg = str(e)
        print(f"Failed to load {csv_name}: {error_msg}")
        log_ingestion(engine, csv_name, table_name, 0, "FAILED", error_msg)
        raise e

def main():
    print("Starting raw ingestion pipeline...")
    
    try:
        # Get database engine connection
        engine = get_db_connection()
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection test successful.")
        
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Please check your .env file and ensure that the Postgres database container is running.")
        sys.exit(1)
        
    # Run DDL schema and tables setup
    run_ddl_initialization(engine)
    
    # Define mapping between CSV files and raw target tables
    load_mappings = [
        ("marketing_campaigns.csv", "marketing_campaigns"),
        ("customers.csv", "customers"),
        ("products.csv", "products"),
        ("orders.csv", "orders"),
        ("order_items.csv", "order_items"),
        ("payments.csv", "payments"),
        ("shipments.csv", "shipments"),
        ("refunds.csv", "refunds")
    ]
    
    summary = []
    has_errors = False
    
    for csv_file, table in load_mappings:
        try:
            rows = load_csv_to_postgres(engine, csv_file, table)
            summary.append((table, "SUCCESS", rows, ""))
        except Exception as e:
            summary.append((table, "FAILED", 0, str(e)))
            has_errors = True
            
    print("\n" + "="*50)
    print("INGESTION PIPELINE SUMMARY:")
    print("="*50)
    for table, status, rows, err in summary:
        print(f"Table: raw.{table:<25} | Status: {status:<10} | Rows: {rows:<10} {f'| Error: {err}' if err else ''}")
    print("="*50)
    
    if has_errors:
        print("Ingestion pipeline finished with errors.")
        sys.exit(1)
    else:
        print("Ingestion pipeline finished successfully!")

if __name__ == "__main__":
    main()
