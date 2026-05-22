import os
import logging
import pandas as pd
from google.cloud import storage, bigquery
from google.api_core.exceptions import Conflict
from extract import extract_country_field1, extract_country_field2
from google.cloud import secretmanager
from google.oauth2 import service_account
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
# Set GOOGLE_APPLICATION_CREDENTIALS in your environment before running,
# e.g. export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
# Never hardcode credential paths in source code.
BUCKET_NAME = "country-bucket-02"
DATASET_NAME = "staging"
TABLE_NAME = "country_data"

COUNTRY_SCHEMA = [
    bigquery.SchemaField("countryId",      "INTEGER",  mode="REQUIRED"),
    bigquery.SchemaField("commonName",     "STRING",   mode="NULLABLE"),
    bigquery.SchemaField("officialName",   "STRING",   mode="NULLABLE"),
    bigquery.SchemaField("startOfWeek",    "STRING",   mode="NULLABLE"),
    bigquery.SchemaField("independent",    "BOOLEAN",  mode="NULLABLE"),
    bigquery.SchemaField("unMember",       "BOOLEAN",  mode="NULLABLE"),
    bigquery.SchemaField("currencyCode",   "STRING",   mode="NULLABLE"),
    bigquery.SchemaField("currencyName",   "STRING",   mode="NULLABLE"),
    bigquery.SchemaField("currencySymbol", "STRING",   mode="NULLABLE"),
    bigquery.SchemaField("idd",            "STRING",   mode="NULLABLE"),
    bigquery.SchemaField("capital",        "STRING",   mode="NULLABLE"),
    bigquery.SchemaField("region",         "STRING",   mode="NULLABLE"),
    bigquery.SchemaField("subregion",      "STRING",   mode="NULLABLE"),
    bigquery.SchemaField("languages",      "STRING",   mode="NULLABLE"),
    bigquery.SchemaField("area",           "FLOAT",    mode="NULLABLE"),
    bigquery.SchemaField("population",     "INTEGER",  mode="NULLABLE"),
    bigquery.SchemaField("continents",     "STRING",   mode="NULLABLE"),
]
def get_credentials_from_secret(secret_name: str, project_id: str):
    """
    Fetches service account credentials from GCP Secret Manager.
    Falls back to default credentials if secret fetch fails.
    This means local development still works with the key file,
    and production uses Secret Manager.
    """
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        secret_json = response.payload.data.decode("UTF-8")
        credentials_info = json.loads(secret_json)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        logger.info("Credentials loaded from Secret Manager.")
        return credentials
    except Exception as e:
        logger.warning("Could not fetch from Secret Manager: %s. Using default credentials.", e)
        return None

def ensure_bucket(project_id: str) -> None:
    """Creates the GCS bucket if it does not already exist."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    if not bucket.exists():
        bucket.location = "US"
        bucket.create(project=project_id, location="US")
        logger.info("Bucket %s created.", BUCKET_NAME)
    else:
        logger.info("Bucket %s already exists.", BUCKET_NAME)


def ensure_dataset(client: bigquery.Client, dataset_id: str) -> None:
    """Creates the BigQuery dataset if it does not already exist."""
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "US"
    try:
        client.create_dataset(dataset)
        logger.info("Dataset %s created.", dataset_id)
    except Conflict:
        logger.info("Dataset %s already exists.", dataset_id)


def validate_dataframes(data1: pd.DataFrame, data2: pd.DataFrame) -> bool:
    """Returns False and logs a warning if either extract returned empty."""
    if data1.empty:
        logger.error("extract_country_field1 returned an empty DataFrame. Aborting.")
        return False
    if data2.empty:
        logger.error("extract_country_field2 returned an empty DataFrame. Aborting.")
        return False
    return True


def build_country_dataframe(data1: pd.DataFrame, data2: pd.DataFrame) -> pd.DataFrame:
    """Merges and prepares the two extract DataFrames."""
    df = pd.merge(data1, data2, left_on="commonName", right_on="nameCommon", how="inner")
    df.drop(columns=["nameCommon"], inplace=True)
    df["countryId"] = df.index + 1

    # Log basic quality stats
    for col in df.columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            logger.warning("Column '%s' has %d null values.", col, null_count)

    logger.info("DataFrame built: %d rows, %d columns.", len(df), len(df.columns))
    return df


def load_to_bigquery(client: bigquery.Client, df: pd.DataFrame, table_id: str) -> None:
    """
    Loads the DataFrame into BigQuery using WRITE_TRUNCATE.
    This replaces the table contents on every run, preventing duplicate rows.
    The schema is explicit — no autodetect — to keep types stable across runs.
    """
    job = client.load_table_from_dataframe(
        df,
        table_id,
        job_config=bigquery.LoadJobConfig(
            schema=COUNTRY_SCHEMA,
            write_disposition="WRITE_TRUNCATE",
        ),
    )
    job.result()
    logger.info("Loaded %d rows into %s.", job.output_rows, table_id)


if __name__ == "__main__":
    PROJECT_ID = "country-data-project-485122"
    
    # Try to get credentials from Secret Manager
    credentials = get_credentials_from_secret("country-data-gcp-key", PROJECT_ID)
    
    # Pass credentials to clients — if None, uses default (key file)
    bq_client = bigquery.Client(project=PROJECT_ID, credentials=credentials)
    storage_client = storage.Client(project=PROJECT_ID, credentials=credentials)
    
    project_id = bq_client.project
    dataset_id = f"{project_id}.{DATASET_NAME}"
    table_id = f"{dataset_id}.{TABLE_NAME}"

    ensure_bucket(project_id)
    ensure_dataset(bq_client, dataset_id)

    data1 = extract_country_field1()
    data2 = extract_country_field2()

    if not validate_dataframes(data1, data2):
        raise SystemExit(1)

    country_df = build_country_dataframe(data1, data2)
    load_to_bigquery(bq_client, country_df, table_id)