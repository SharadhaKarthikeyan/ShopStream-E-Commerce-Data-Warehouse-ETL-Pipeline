# ShopStream Pipeline Architecture

This document describes the design, data ingestion, database topography, transformation layer, testing framework, and orchestration logic for the ShopStream batch data warehouse project.

---

## Architecture Diagram

The pipeline utilizes an ELT (Extract, Load, Transform) architecture designed for batch workloads:

```text
+------------------------+
| scripts/generate_data  |  <--- Runs locally or inside Airflow (Faker)
+------------------------+
            |
            v
   [ Raw CSV Dataset ] (Stored in data/raw/*.csv)
            |
            v
+-----------------------------+
| scripts/load_raw_to_postgres| <--- Truncates and drops; bulk imports
+-----------------------------+
            |
            v
   [ PostgreSQL raw Schema ] (Database: shopstream_dw)
            |
            v
  ========================== Transformation (dbt) ==========================
            |
            +--> [ models/staging/stg_* ]      (Data cleaning, deduplication)
            |
            +--> [ models/intermediate/int_* ] (Metric aggregations)
            |
            +--> [ models/marts/dim_* / fact_* ] (Star Schema Core dimensions & facts)
            |
            +--> [ models/marts/mart_* ]       (Analytic-ready aggregations)
  ==========================================================================
            |
            v
    [ dbt & Custom Tests ]
            |
            v
+-------------------------+
| scripts/export_marts    | ---> Exports clean tables to data/processed/*.csv
+-------------------------+
            |
            +--> [ reports/data_quality_report.md ] (Quality audit file)
            +--> [ dashboard/app.py ]               (Streamlit visual KPI)
```

---

## 1. Database Separation

In a production environment, database systems are isolated to protect resources and restrict permission scopes. This project adheres to this principle by dividing the local PostgreSQL instance into two distinct, isolated databases:
1. **`airflow`**: Serves exclusively as the metadata backend database for Apache Airflow (tracking DAG runs, scheduler heartbeat logs, worker states, and user sessions).
2. **`shopstream_dw`**: The data warehouse target, housing the analytics schemas:
   * **`raw`**: Storing the direct, un-modified bulk CSV imports.
   * **`staging`**: Storing dbt staging views (`stg_*`) and intermediate metrics (`int_*`).
   * **`marts`**: Storing fact, dimension, and business intelligence tables.

---

## 2. Ingestion & Loader (`load_raw_to_postgres.py`)

Ingestion is implemented in Python using `pandas` and `sqlalchemy`.
* **Idempotency**: At the start of a run, the loader executes `sql/create_raw_tables.sql` which drops existing tables in the `raw` schema and rebuilds them.
* **Bulk Loading**: CSV tables are loaded sequentially using Pandas' optimized `to_sql` method.
* **Metadata Logging**: The loader logs details of every table's ingestion (file name, destination table, start timestamp, row counts, and error messages if applicable) into the `raw.ingestion_log` table.

---

## 3. Transformation Layer (`dbt_ecommerce`)

Transformations are configured inside `dbt_ecommerce/` targeting the PostgreSQL `shopstream_dw` database.

### Path-Based Selectors
To keep execution organized, we partition dbt runs by selecting specific model subfolders:
* **Staging layer**: `dbt run --select models/staging`
* **Intermediate layer**: `dbt run --select models/intermediate`
* **Marts layer**: `dbt run --select models/marts`

### Custom Schema Resolution
A macro `generate_schema_name.sql` is deployed to override dbt's default behavior (which appends custom schemas to the default target schema). This allows dbt to write directly to `staging` (for staging and intermediate models) and `marts` (for core facts, dimensions, and marts) schemas.

---

## 4. Orchestration & DAG (`dags/ecommerce_batch_pipeline.py`)

Apache Airflow orchestrates the pipeline on a daily batch schedule:
1. **`generate_raw_data`**: Spawns python mock generator.
2. **`load_raw_data_to_postgres`**: Spawns Python Postgres loader.
3. **`dbt_debug`**: Runs `dbt debug` to verify connection and configuration settings.
4. **`dbt_run_staging`**: Executes staging cleanups.
5. **`dbt_run_intermediate`**: Calculates intermediate aggregates.
6. **`dbt_run_marts`**: Rebuilds fact and dimension tables.
7. **`run_dbt_tests`**: Runs all schema tests and custom SQL tests.
8. **`export_analytical_marts`**: Dumps final marts to `data/processed/` for dashboard integration.
9. **`generate_data_quality_report`**: Compiles data metrics into `reports/data_quality_report.md`.

---

## 5. Security & Environment Configuration

* **Zero Hardcoded Secrets**: DB passwords, host locations, and configuration directories are loaded at runtime from `.env` via `python-dotenv`.
* **Shared Volumes**: The repository's folders (`dags/`, `scripts/`, `dbt_ecommerce/`, `data/`, `reports/`) are mounted directly to the Airflow scheduler and webserver containers, meaning outputs sync back to the host machine immediately.
