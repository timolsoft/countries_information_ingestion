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
The following transformations were applied to the dataset to clean and standardize the country information:
Several columns contained list-like string values with brackets and quotes. These were converted to clean string values by removing unnecessary characters.
* currencyCode was converted to string and removed brackets and single quotes.
* capital was converted to string and removed brackets, single quotes, and double quotes.
* continents was converted to string and removed brackets and single quotes.
* iddSuffixes was converted to string and removed brackets and single quotes.
* concatenate iddRoot and iddSuffixes into a single column called idd.
* dropped the original iddRoot and iddSuffixes columns after concatenation.
* Created a new column countryId using the dataframe index, starting from 1.

## Some Analytics Insights
Top 2 currencies in each region
he findings show the two most commonly used currencies in each global region based on the number of countries that use them. In Africa, the West African CFA franc is the most widely used currency, followed by the Central African CFA franc, indicating strong regional currency cooperation. In the Americas, the United States dollar is the dominant currency, with the Eastern Caribbean dollar also widely used among Caribbean countries. In the Antarctic region, the Euro and the British pound are each used by one territory, reflecting limited and specialized currency usage. In Asia, there is no dominant regional currency, as the Bangladeshi taka and Indian rupee each appear as top currencies but are used by only one country, showing high currency diversity. In Europe, the Euro is overwhelmingly the most widely used currency, demonstrating strong economic integration, while the British pound ranks second. In Oceania, the Australian dollar is the most commonly used currency, followed by the United States dollar, which is frequently used among smaller Pacific island nations. Overall, the results indicate that some regions share currencies extensively, while others maintain country-specific monetary systems.
<img width="422" height="255" alt="image" src="https://github.com/user-attachments/assets/dcd8c2d8-c451-49cb-b643-ac6422021dc4" />

  
## Tech Stack
* Python - Programming
* Requests API - Data Extraction
* BigQuery - Database/Data wharehouse
* Github - Version control
