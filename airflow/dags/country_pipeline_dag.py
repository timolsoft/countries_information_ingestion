import sys
import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Make our pipeline code importable inside the container
sys.path.insert(0, '/opt/airflow/pipeline')

from extract import extract_country_field1, extract_country_field2
from load import (
    ensure_bucket,
    ensure_dataset,
    build_country_dataframe,
    load_to_bigquery,
    BUCKET_NAME,
    DATASET_NAME,
    TABLE_NAME,
)

from google.cloud import bigquery

logger = logging.getLogger(__name__)

# ── DAG-level constants ────────────────────────────────────────────
PROJECT_ID  = "country-data-project-485122"
DATASET_ID  = f"{PROJECT_ID}.{DATASET_NAME}"
TABLE_ID    = f"{DATASET_ID}.{TABLE_NAME}"

WAREHOUSE_TABLES = [
    "dim_region",
    "dim_currency",
    "dim_language",
    "dim_geography",
    "fact_country",
]

# ── Default args ────────────────────────────────────────────────────
default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email": ["tolaniyi0612@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}
# ── Task functions ──────────────────────────────────────────────────

def task_extract(**context):
    """
    Extract data from both API endpoints and push to XCom
    so the validate task can inspect row counts.
    """
    logger.info("Starting extraction from REST Countries API...")

    data1 = extract_country_field1()
    data2 = extract_country_field2()

    if data1.empty:
        raise ValueError("extract_country_field1 returned an empty DataFrame.")
    if data2.empty:
        raise ValueError("extract_country_field2 returned an empty DataFrame.")

    logger.info("Field1 rows: %d | Field2 rows: %d", len(data1), len(data2))

    # Push counts to XCom for the validate task to check
    context["ti"].xcom_push(key="field1_rows", value=len(data1))
    context["ti"].xcom_push(key="field2_rows", value=len(data2))

    logger.info("Extraction complete.")


def task_validate(**context):
    """
    Pull row counts from XCom and enforce minimum thresholds.
    Fails the pipeline before anything reaches BigQuery if data looks wrong.
    """
    ti = context["ti"]
    field1_rows = ti.xcom_pull(task_ids="extract", key="field1_rows")
    field2_rows = ti.xcom_pull(task_ids="extract", key="field2_rows")

    logger.info("Validating — field1: %d rows, field2: %d rows", field1_rows, field2_rows)

    # Enforce minimum row thresholds — REST Countries API returns ~250 countries
    if field1_rows < 200:
        raise ValueError(f"field1 row count too low: {field1_rows}. Expected >= 200.")
    if field2_rows < 200:
        raise ValueError(f"field2 row count too low: {field2_rows}. Expected >= 200.")

    logger.info("Validation passed.")


def task_load_staging(**context):
    """
    Re-extract (stateless tasks are safer in Airflow than passing DataFrames),
    merge, and load into BigQuery staging.
    """
    logger.info("Loading to BigQuery staging...")

    bq_client  = bigquery.Client()
    project_id = bq_client.project

    ensure_bucket(project_id)
    ensure_dataset(bq_client, DATASET_ID)

    data1 = extract_country_field1()
    data2 = extract_country_field2()

    country_df = build_country_dataframe(data1, data2)
    load_to_bigquery(bq_client, country_df, TABLE_ID)

    logger.info("Staging load complete — %d rows.", len(country_df))


def task_build_warehouse(**context):
    """
    Rebuilds all 5 warehouse tables from staging using BigQuery SQL jobs.
    Tables are created/replaced in dependency order — dimensions first, fact last.
    """
    logger.info("Building warehouse tables...")
    client = bigquery.Client()

    sql_statements = {

        "dim_region": f"""
            CREATE OR REPLACE TABLE `{PROJECT_ID}.warehouse.dim_region` (
                regionId  INT64  NOT NULL,
                continent STRING,
                region    STRING,
                subregion STRING
            );
            INSERT INTO `{PROJECT_ID}.warehouse.dim_region`
            SELECT
                ROW_NUMBER() OVER (ORDER BY region, subregion) AS regionId,
                continents AS continent,
                region,
                subregion
            FROM (
                SELECT DISTINCT continents, region, subregion
                FROM `{PROJECT_ID}.staging.country_data`
                WHERE region IS NOT NULL
            );
        """,

        "dim_currency": f"""
            CREATE OR REPLACE TABLE `{PROJECT_ID}.warehouse.dim_currency` (
                currencyId     INT64  NOT NULL,
                currencyCode   STRING,
                currencyName   STRING,
                currencySymbol STRING
            );
            INSERT INTO `{PROJECT_ID}.warehouse.dim_currency`
            SELECT
                ROW_NUMBER() OVER (ORDER BY currencyCode) AS currencyId,
                currencyCode, currencyName, currencySymbol
            FROM (
                SELECT DISTINCT currencyCode, currencyName, currencySymbol
                FROM `{PROJECT_ID}.staging.country_data`
                WHERE currencyCode IS NOT NULL
            );
        """,

        "dim_language": f"""
            CREATE OR REPLACE TABLE `{PROJECT_ID}.warehouse.dim_language` (
                languageId   INT64  NOT NULL,
                countryId    INT64  NOT NULL,
                languageName STRING
            )
            CLUSTER BY countryId;
            INSERT INTO `{PROJECT_ID}.warehouse.dim_language`
            SELECT
                ROW_NUMBER() OVER (ORDER BY countryId, languageName) AS languageId,
                countryId,
                TRIM(languageName) AS languageName
            FROM (
                SELECT countryId, lang AS languageName
                FROM `{PROJECT_ID}.staging.country_data`,
                UNNEST(SPLIT(languages, ',')) AS lang
                WHERE languages IS NOT NULL
            );
        """,

        "dim_geography": f"""
            CREATE OR REPLACE TABLE `{PROJECT_ID}.warehouse.dim_geography` (
                countryId    INT64  NOT NULL,
                commonName   STRING,
                officialName STRING,
                capital      STRING,
                independent  BOOL,
                unMember     BOOL,
                startOfWeek  STRING,
                idd          STRING
            )
            CLUSTER BY commonName;
            INSERT INTO `{PROJECT_ID}.warehouse.dim_geography`
            SELECT countryId, commonName, officialName, capital,
                   independent, unMember, startOfWeek, idd
            FROM `{PROJECT_ID}.staging.country_data`;
        """,

        "fact_country": f"""
            CREATE OR REPLACE TABLE `{PROJECT_ID}.warehouse.fact_country` (
                countryId  INT64   NOT NULL,
                regionId   INT64,
                currencyId INT64,
                population INT64,
                area       FLOAT64
            )
            CLUSTER BY regionId, currencyId;
            INSERT INTO `{PROJECT_ID}.warehouse.fact_country`
            SELECT
                s.countryId,
                r.regionId,
                c.currencyId,
                s.population,
                s.area
            FROM `{PROJECT_ID}.staging.country_data` s
            LEFT JOIN `{PROJECT_ID}.warehouse.dim_region` r
                ON s.region = r.region AND s.subregion = r.subregion
            LEFT JOIN `{PROJECT_ID}.warehouse.dim_currency` c
                ON s.currencyCode = c.currencyCode;
        """,
    }

    for table_name, sql in sql_statements.items():
        logger.info("Building %s...", table_name)
        # BigQuery requires each statement to be run separately
        for statement in [s.strip() for s in sql.strip().split(";") if s.strip()]:
            job = client.query(statement)
            job.result()
        logger.info("%s built successfully.", table_name)

    logger.info("All warehouse tables built.")


# ── DAG definition ──────────────────────────────────────────────────

with DAG(
    dag_id="country_data_pipeline",
    description="Extract country data from REST API → validate → load BigQuery staging → build warehouse",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval="0 6 * * *",      # daily at 06:00 UTC
    catchup=False,                       # don't backfill historical runs
    tags=["country-data", "etl", "bigquery"],
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=task_extract,
    )

    validate = PythonOperator(
        task_id="validate",
        python_callable=task_validate,
    )

    load_staging = PythonOperator(
        task_id="load_staging",
        python_callable=task_load_staging,
    )

    build_warehouse = PythonOperator(
        task_id="build_warehouse",
        python_callable=task_build_warehouse,
    )

    # ── Task dependencies ──────────────────────────────────────────
    extract >> validate >> load_staging >> build_warehouse