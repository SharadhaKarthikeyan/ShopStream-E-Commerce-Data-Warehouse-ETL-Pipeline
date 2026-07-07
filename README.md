# ShopStream: E-Commerce Data Warehouse & ETL Pipeline

![ShopStream Analytics Dashboard](reports/dashboard_screenshot.png)

**ShopStream** is a production-style, end-to-end batch ETL/ELT pipeline and modern data warehouse. It simulates a fast-growing e-commerce platform by generating relationally consistent transactions, loading them into PostgreSQL, executing layered transformations with dbt Core, validating metrics with schema assertions, and orchestrating the entire lifecycle using Apache Airflow in Docker.

---

## 💼 Resume Positioning

> **E-Commerce Data Warehouse & ETL Pipeline | Python, PostgreSQL, Airflow, dbt, SQL, Docker**
>
> Built an end-to-end batch data pipeline to process 50K+ orders, 120K+ order items, 10K+ customers, payments, refunds, and shipment records into analytics-ready PostgreSQL warehouse tables.
>
> Designed dbt staging, intermediate, fact, dimension, and mart models to support revenue tracking, customer lifetime value, product performance, refund analysis, and delivery delay reporting.
>
> Automated pipeline orchestration with Airflow DAGs and implemented 20+ data quality checks for uniqueness, null handling, accepted values, referential integrity, and business rule validation.

---

## 🏪 Business Problem

Modern e-commerce operators struggle with fragmented, raw transactional datasets. Key commercial metrics—such as Customer Lifetime Value (LTV), marketing Campaign ROI, refund leakage, and shipping carrier delay rates—cannot be queried directly from operational tables without causing severe performance lag. 

ShopStream resolves this by implementing a structured **Star Schema** data warehouse. It cleans raw transaction records (addressing casing inconsistencies, duplicates, and missing tracking parameters) and generates consolidated facts, dimensions, and reporting marts optimized for BI reporting.

---

## 🔄 Pipeline Workflow & Architecture

The following flow illustrates how raw data moves through ingestion, staging, transformations, testing, and dashboard reporting:

```text
Raw CSV Files (Faker)
      ↓
Python Data Generation (scripts/generate_data.py)
      ↓
Python Raw Data Loader (scripts/load_raw_to_postgres.py)
      ↓
PostgreSQL raw schema (shopstream_dw Database)
      ↓
dbt staging models (Deduplication, standardized casing)
      ↓
dbt intermediate models (Metric pre-calculations)
      ↓
dbt mart models (Facts, Dimensions, Analytics-ready)
      ↓
dbt tests & Custom SQL tests (Data Quality validation)
      ↓
Analytics-ready tables (marts schema)
      ↓
Marts Export (scripts/export_marts.py)
      ↓
Data Quality Report & Streamlit Dashboard (dashboard/app.py)
```

---

## 🛠️ Tech Stack & Tools

* **Database / DW**: PostgreSQL 15 (Isolated databases: `airflow` for metadata, `shopstream_dw` for analytics)
* **Ingestion**: Python 3.10 (Pandas, SQLAlchemy, Psycopg2-binary, Faker, Dotenv)
* **Transformations**: dbt Core 1.5 (Postgres Adapter)
* **Orchestration**: Apache Airflow 2.7.1
* **Environment**: Docker & Docker Compose
* **Visualization**: Streamlit & Plotly (Offline-ready)

---

## 📊 Dataset Description

The pipeline processes synthetic but highly realistic datasets generated using `scripts/generate_data.py`. The generated dataset is relationally consistent and includes:

* **Customers** (10,000): Profile info, signup logs, geography, segments (Gamers, Tech, Fashion, etc.).
* **Products** (2,000): Catalog details, subcategories, cost vs selling prices, active flag.
* **Orders** (50,000): Customer links, date logs, order status (completed, shipped, returned, cancelled, pending), and campaign attributions.
* **Order Items** (120,000): Itemized purchases, quantities, unit prices, discounts, taxes, totals.
* **Payments** (50,000): Payment methods, success/failed status, currencies, transaction IDs.
* **Shipments** (45,000): Delivery timelines, carrier choices (DHL, FedEx, UPS, USPS), delay metrics.
* **Refunds** (5,000): Refund reasons (damaged, defective, sizing), processing states, refund amounts.
* **Campaigns** (100): Launch budgets, channels (TikTok, Meta, Email), start/end dates.

### Dirty Data Cases Included
* Duplicate entries (~0.1%) to validate deduplication algorithms.
* Mixed casing in string fields (e.g. `PENDING`, `Pending`, `pending`).
* Null campaign IDs to represent organic traffic.
* Chronological delivery delays and refund mismatches.
* Intentionally invalid quantities (<=0) and successful payments with <= $0 values to trigger data quality test assertions.

---

## 🗄️ Database Schema Design

The `shopstream_dw` database is structured into three schemas:

1. **`raw`**: Houses the raw transactional tables (`customers`, `products`, `orders`, `order_items`, `payments`, `shipments`, `refunds`, `marketing_campaigns`) and an `ingestion_log`.
2. **`staging`**: Houses dbt staging views (`stg_*`) and pre-aggregated intermediate views (`int_*`).
3. **`marts`**: Core dimensional model tables (`dim_customers`, `dim_products`, `dim_date`, `dim_marketing_campaigns`) and fact tables (`fact_orders`, `fact_order_items`, `fact_payments`, `fact_shipments`, `fact_refunds`) along with analytical aggregate tables (`mart_*`).

---

## ⚙️ dbt Model Layers

* **Staging Layer (`models/staging/`)**: Normalizes case casing, trims strings, casts columns to correct types, and deduplicates records using `row_number() over (partition by id)`.
* **Intermediate Layer (`models/intermediate/`)**: Focuses on aggregations like order gross/net totals, delivery delay days, and customer spend aggregations.
* **Marts Layer (`models/marts/`)**: Formulates the dimensional star schema (Facts/Dimensions) and compiles analytical marts like `mart_daily_revenue`, `mart_customer_lifetime_value`, `mart_product_performance`, `mart_refund_analysis`, `mart_delivery_performance`, and `mart_campaign_performance`.

---

## 🧪 Data Quality Checks

Over **20+ dbt tests** and **6 custom SQL tests** are executed to prevent bad data from reaching the production tables:
* Primary key uniqueness and non-null checks.
* State machine values validation (accepted statuses for orders, payments, shipments, refunds).
* Referential integrity (foreign key relationship lookups).
* Custom SQL tests:
  * `test_payment_amount_positive`: Confirms no successful payments have <= $0 value.
  * `test_quantity_positive`: Flags order items with negative/zero quantities.
  * `test_refund_amount_limit`: Verifies refund amounts do not exceed the original order's net revenue.
  * `test_delivered_shipment_has_delivery_date`: Ensures delivered packages have delivery date logs.
  * `test_delivery_date_after_shipment_date`: Blocks delivery dates logged prior to ship dates.
  * `test_order_date_not_future`: Blocks transactions with future dates.

---

## 🌬️ Airflow Orchestration

The daily batch DAG `ecommerce_batch_pipeline` consists of the following steps:
1. `start` -> Empty initialization.
2. `generate_raw_data` -> Executes Python generator script.
3. `load_raw_data_to_postgres` -> Recreates `raw` schema and bulk inserts CSVs, writing execution details to `raw.ingestion_log`.
4. `dbt_debug` -> Tests warehouse connection routing.
5. `dbt_run_staging` -> Compiles staging views.
6. `dbt_run_intermediate` -> Compiles metrics models.
7. `dbt_run_marts` -> Generates physical dimensions/facts/marts.
8. `run_dbt_tests` -> Executes all tests.
9. `export_analytical_marts` -> Exports clean marts to CSVs for reporting.
10. `generate_data_quality_report` -> Compiles quality reports under `reports/data_quality_report.md`.
11. `end` -> Empty end marker.

---

## 🚀 How to Run the Project

### Prerequisites
* Docker & Docker Compose
* Python 3.10+
* Local Port `5432` (PostgreSQL) and Port `8080` (Airflow) must be available.

### Step 1: Clone and Configure Environment
Copy `.env.example` into a new `.env` file:
```bash
cp .env.example .env
```
Ensure you have the required Python modules installed for local running:
```bash
pip install -r requirements.txt
```

### Step 2: Spin up the Containers
Run Docker Compose to start PostgreSQL and Airflow services:
```bash
docker-compose up -d
```
*Wait ~1-2 minutes for Airflow migrations to complete and dependency packages to install.*

### Step 3: Run the Pipeline Locally (CLI Method)
For rapid verification without wait times, you can run the pipeline stages sequentially on your host machine:

```bash
# 1. Generate local datasets
python scripts/generate_data.py

# 2. Populate PostgreSQL database
python scripts/load_raw_to_postgres.py

# 3. Verify dbt connectivity, compile models, and run tests
cd dbt_ecommerce
dbt debug
dbt run
dbt test

# 4. Generate final quality reports and export marts
python ../scripts/data_quality_report.py
python ../scripts/export_marts.py
```

> [!NOTE]
> During development, you can execute individual layers using path-based selectors:
> * Staging: `dbt run --select path:models/staging`
> * Intermediate: `dbt run --select path:models/intermediate`
> * Marts: `dbt run --select path:models/marts`

### Step 4: Run the Pipeline via Airflow (GUI Method)
1. Open your browser and navigate to: [http://localhost:8080](http://localhost:8080).
2. Log in with user: `admin` and password: `admin`.
3. Locate `ecommerce_batch_pipeline`, unpause the DAG, and click **Trigger DAG**.
4. Monitor the task execution tree. Once completed, your local `data/processed/` and `reports/` folder will sync automatically.

### Step 5: Launch the Streamlit Dashboard (Optional)
Visualize the resulting e-commerce insights offline using the exported CSV files:
```bash
streamlit run dashboard/app.py
```
This launches a browser tab at `http://localhost:8501` showcasing the interactive analytics.

---

## 📈 Example Business Questions Answered

* **Daily Net Sales**: Evaluated via `marts.mart_daily_revenue` to check transaction run-rates.
* **Segment Purchasing Power**: Querying LTV sums on `marts.mart_customer_lifetime_value` grouped by customer segment.
* **Carrier Performance**: Finding late-delivery patterns on `marts.mart_delivery_performance` to evaluate carrier SLAs.
* **Marketing Efficiency**: Evaluating ROIs and campaign attributions on `marts.mart_campaign_performance` to budget channel spend.
* **Refund Leakage**: Spotting high-return categories in `marts.mart_product_performance` and return reasons in `marts.mart_refund_analysis`.

---

## ⚠️ Known Limitations

* **Local Sandbox Environment**: This project is built as a production-style *local* pipeline and uses local Docker containers (PostgreSQL and Apache Airflow) rather than a deployed production cloud environment (e.g. AWS Redshift/Snowflake, managed MWAA, or dbt Cloud).
* **Synthetic Data**: The transactional data processed is synthetically generated using Python's `faker` library and does not represent real-world customer traffic or commercial histories.

