# Countries Information Ingestion Project
## Project Overview

An end-to-end, production-style ELT data pipeline that ingests global country data from a public REST API, models it into a star-schema data warehouse on Google BigQuery, and serves it for analytics on travel destinations. The pipeline is orchestrated with Apache Airflow, transformed with dbt, tested with pytest and dbt data tests, and shipped through a GitHub Actions CI pipeline.
## Business Objectives
A travel agency needs accurate geographical and cultural data to recommend destinations by language, region, currency, population and independence status. This pipeline turns the raw REST Countries API into clean, query-ready analytics tables that answer those questions.

## Data Source
The data is sourced from a REST API https://restcountries.com/v3.1/all

## Key Feature
 End-to-end ELT from public API to a dimensional warehouse, fully automated.
 Apache Airflow orchestration — DAG country_data_pipeline runs daily at 06:00 UTC with retries, failure email alerts, and a extract → validate → load → build task flow.
 Data quality gates — row-count validation in Airflow before anything reaches the warehouse, plus 21 dbt tests (unique, not_null, relationships).
 dbt star schema — staging views feed a fact table and four dimensions, with documented sources and tested grain.
 Idempotent loads — WRITE_TRUNCATE and explicit BigQuery schemas keep runs repeatable and prevent duplicates.
 Secrets done right — credentials fetched from GCP Secret Manager at runtime, with a local-key fallback for development.
 CI pipeline — GitHub Actions runs the pytest suite on every push and pull request to main.
 Unit-tested extraction & load — pytest with mocked API responses; the pipeline degrades gracefully (returns empty DataFrames rather than crashing) on API failure.
 Local dev stack — Docker Compose spins up Postgres + pgAdmin as an alternative target to BigQuery.
## Data Architecture
<img width="631" height="251" alt="image" src="https://github.com/user-attachments/assets/4f875fcb-f724-431d-bc66-64fa80f79a86" />

#Structure .
├── api/
│   ├── extract.py              # Pull & shape data from REST Countries API
│   ├── load.py                 # Build DataFrame → load to BigQuery staging
│   ├── load2db.py              # Alternative: load into local Postgres
│   └── tests/                  # pytest unit tests (mocked API)
├── airflow/
│   ├── dags/country_pipeline_dag.py   # Orchestration DAG
│   ├── Dockerfile
│   └── docker-compose.yml
├── country_data/               # dbt project
│   └── models/
│       ├── staging/            # stg_country_data (view) + sources.yml
│       └── warehouse/          # dim_* + fact_country + schema.yml (tests)
├── *.sql                       # Ad-hoc analytics queries
├── docker-compose.yml          # Local Postgres + pgAdmin
├── countrydata.drawio(.svg)    # Architecture diagram source
├── requirements.txt
└── .github/workflows/ci.yml    # CI pipeline

# Prerequisites
Python 3.11+
A GCP project with BigQuery + Cloud Storage enabled
A service account with BigQuery and Storage permissions
Docker & Docker Compose (for Airflow / local Postgres)

# Clone and Install
git clone https://github.com/<your-username>/country-data-pipeline.git
cd country-data-pipeline
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure Credential
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-key.json"
export GCP_PROJECT_ID="your-project-id"

# Run the pipeline manually (without Airflow)
cd api
python load.py        # extract → transform → load to BigQuery staging

# Build the warehouse woth dbt
cd country_data
dbt deps
dbt build             # runs models + all data tests

#Data Quality & Testing
Quality is enforced at two layers:

Pipeline gate (Airflow): the validate task checks API row counts (expects ~250 countries) and fails the run before loading if the source looks wrong.
Warehouse tests (dbt): unique, not_null and relationships tests on surrogate keys and foreign keys guarantee referential integrity across the star schema.
Unit tests (pytest): extraction and load logic are tested with mocked API responses, including the empty-response / failure path.


## Some Analytics Insights
A set of SQL queries answer the travel-agency's business questions. Highlights:

Top currencies per region — e.g. the Euro dominates Europe, the West African CFA franc leads Africa, the US dollar leads the Americas.
Distribution of countries across regions — Africa has the most entities (~23.6%), Antarctica the fewest (~2%).
Largest / smallest countries by area per continent.
Multilingual countries — those with two or more official languages.
Calendar conventions — countries whose week does not start on Monday.
Currency, UN-membership and independence breakdowns for market analysis.

## Data Model
A classic star schema optimised for analytical queries:

fact_country — grain: one row per country. Metrics: population, area. Foreign keys to region and currency.
dim_region — continent / region / subregion.
dim_currency — currency code, name, symbol.
dim_language — one row per language per country (bridge-style).
dim_geography — country identity & descriptive attributes (names, capital, IDD, UN/independence flags).

## Tech Stack
LayerToolsLanguagePython 3.11, SQLExtractionrequests, pandasWarehouseGoogle BigQueryStorageGoogle Cloud StorageTransformationdbt (staging views + warehouse tables)OrchestrationApache Airflow 2.9.1 (Dockerized)SecretsGCP Secret ManagerTestingpytest, pytest-mock, dbt testsCI/CDGitHub ActionsLocal infraDocker Compose, PostgreSQL, pgAdmin
