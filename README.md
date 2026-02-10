# Countries Information Ingestion Project
## Project Overview

This project focuses on building a robust data pipeline that integrates country-level data from a public REST API. The dataset is transformed and stored to support travel destination recommendations based on attributes such as language, region, currency, population, and more.

The pipeline extracts, transforms, and loads global country data while generating valuable analytical insights that help the business understand travel trends and regional characteristics.
## Business Objectives
Travel agencies rely on accurate geographical and cultural information to recommend travel destinations tailored to customer preferences. This project enables the agency to:
* Recommend destinations based on language compatibility
* Provide insights based on region and continent preferences
* Analyze travel cost implications using currency information
* Identify emerging travel markets using population and independence data

## Data Source
The data is sourced from a REST API https://restcountries.com/v3.1/all

# Data Cleaning and Transformation
Several Data Cleaning and transformations were applied to ensure usability and data quality:
* Flattened nested JSON structures
* Concatenated IDD Root and Suffix to form country calling codes
* Normalized multi-value fields such as languages and continents
* Handled missing/null values
* Standardized column naming conventions
* Converted list-based attributes into analytical-friendly format

## Tech Stack
* Python - Programming
* Requests API - Data Extraction
* BigQuery - Data wharehouse
* Github - Version control
