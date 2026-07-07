import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator

# Fetch database credentials dynamically from environment variables
# This avoids hard-coding secrets in DAG files, pulling them from Docker Compose env
DB_HOST = os.environ.get('DB_HOST', 'postgres')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
DB_NAME = os.environ.get('DB_NAME', 'shopstream_dw')

# Common environment dictionary to inject into dbt execution contexts
DBT_ENV = {
    'DB_HOST': DB_HOST,
    'DB_PORT': DB_PORT,
    'DB_USER': DB_USER,
    'DB_PASSWORD': DB_PASSWORD,
    'DB_NAME': DB_NAME
}

# Default arguments for the batch pipeline DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

# Define the DAG
with DAG(
    dag_id='ecommerce_batch_pipeline',
    default_args=default_args,
    description='A production-style ETL batch pipeline for ShopStream E-Commerce Data Warehouse',
    schedule_interval='@daily',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['shopstream', 'etl', 'dbt', 'postgres'],
) as dag:

    # 1. Start pipeline run boundary marker
    start_task = EmptyOperator(
        task_id='start'
    )

    # 2. Python task to generate mock raw transaction CSV files
    generate_raw_data_task = BashOperator(
        task_id='generate_raw_data',
        bash_command='python /opt/airflow/scripts/generate_data.py',
        cwd='/opt/airflow'
    )

    # 3. Python task to read CSV files and reload PostgreSQL raw schema tables
    load_raw_data_to_postgres_task = BashOperator(
        task_id='load_raw_data_to_postgres',
        bash_command='python /opt/airflow/scripts/load_raw_to_postgres.py',
        cwd='/opt/airflow'
    )

    # 4. DBT Debug task: checks database connectivity and profile configuration
    dbt_debug_task = BashOperator(
        task_id='dbt_debug',
        bash_command='dbt debug --project-dir /opt/airflow/dbt_ecommerce --profiles-dir /opt/airflow/dbt_ecommerce',
        env=DBT_ENV
    )

    # 5. DBT Run Staging Models: uses path-based selector path:models/staging
    dbt_run_staging_task = BashOperator(
        task_id='dbt_run_staging_models',
        bash_command='dbt run --select path:models/staging --project-dir /opt/airflow/dbt_ecommerce --profiles-dir /opt/airflow/dbt_ecommerce',
        env=DBT_ENV
    )

    # 6. DBT Run Intermediate Models: uses path-based selector path:models/intermediate
    dbt_run_intermediate_task = BashOperator(
        task_id='dbt_run_intermediate_models',
        bash_command='dbt run --select path:models/intermediate --project-dir /opt/airflow/dbt_ecommerce --profiles-dir /opt/airflow/dbt_ecommerce',
        env=DBT_ENV
    )

    # 7. DBT Run Mart Models: uses path-based selector path:models/marts
    dbt_run_marts_task = BashOperator(
        task_id='dbt_run_mart_models',
        bash_command='dbt run --select path:models/marts --project-dir /opt/airflow/dbt_ecommerce --profiles-dir /opt/airflow/dbt_ecommerce',
        env=DBT_ENV
    )

    # 8. DBT Test task: executes schema and custom SQL quality tests
    dbt_test_task = BashOperator(
        task_id='run_dbt_tests',
        bash_command='dbt test --project-dir /opt/airflow/dbt_ecommerce --profiles-dir /opt/airflow/dbt_ecommerce',
        env=DBT_ENV
    )

    # 9. Python task to export transformed marts as CSVs to data/processed
    export_analytical_marts_task = BashOperator(
        task_id='export_analytical_marts',
        bash_command='python /opt/airflow/scripts/export_marts.py',
        cwd='/opt/airflow'
    )

    # 10. Python task to generate final validation statistics and write quality report
    generate_data_quality_report_task = BashOperator(
        task_id='generate_data_quality_report',
        bash_command='python /opt/airflow/scripts/data_quality_report.py',
        cwd='/opt/airflow'
    )

    # 11. End pipeline run boundary marker
    end_task = EmptyOperator(
        task_id='end'
    )

    # Define DAG Orchestration Flow
    start_task >> generate_raw_data_task
    generate_raw_data_task >> load_raw_data_to_postgres_task
    load_raw_data_to_postgres_task >> dbt_debug_task
    dbt_debug_task >> dbt_run_staging_task
    dbt_run_staging_task >> dbt_run_intermediate_task
    dbt_run_intermediate_task >> dbt_run_marts_task
    dbt_run_marts_task >> dbt_test_task
    dbt_test_task >> export_analytical_marts_task
    export_analytical_marts_task >> generate_data_quality_report_task
    generate_data_quality_report_task >> end_task
