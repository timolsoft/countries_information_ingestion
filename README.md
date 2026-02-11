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

## Data Architecture
<img width="631" height="251" alt="image" src="https://github.com/user-attachments/assets/4f875fcb-f724-431d-bc66-64fa80f79a86" />

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
#### Top 2 currencies in each region
he findings show the two most commonly used currencies in each global region based on the number of countries that use them. In Africa, the West African CFA franc is the most widely used currency, followed by the Central African CFA franc, indicating strong regional currency cooperation. In the Americas, the United States dollar is the dominant currency, with the Eastern Caribbean dollar also widely used among Caribbean countries. In the Antarctic region, the Euro and the British pound are each used by one territory, reflecting limited and specialized currency usage. In Asia, there is no dominant regional currency, as the Bangladeshi taka and Indian rupee each appear as top currencies but are used by only one country, showing high currency diversity. In Europe, the Euro is overwhelmingly the most widely used currency, demonstrating strong economic integration, while the British pound ranks second. In Oceania, the Australian dollar is the most commonly used currency, followed by the United States dollar, which is frequently used among smaller Pacific island nations. Overall, the results indicate that some regions share currencies extensively, while others maintain country-specific monetary systems.
<img width="422" height="255" alt="image" src="https://github.com/user-attachments/assets/dcd8c2d8-c451-49cb-b643-ac6422021dc4" />
#### Distribution of Countries across the regions
Africa has the highest number of countries or territories in the dataset, accounting for 59 countries, which represents 23.6% of the total. The Americas follow with 56 countries (22.4%), while Europe includes 53 countries (21.2%). Asia has 50 countries, making up 20% of the total, showing a fairly balanced distribution among these four major regions. Oceania contains 27 countries, representing 10.8%, which is noticeably lower than the other major regions. The Antarctic region has the fewest, with only 5 territories, accounting for 2% of the dataset. Overall, the distribution shows that most countries are concentrated in Africa, the Americas, Europe, and Asia, while Oceania and Antarctica contain significantly fewer geopolitical entities.
 <img width="359" height="131" alt="image" src="https://github.com/user-attachments/assets/79c1abca-1653-4883-8c67-bf0bd2d722aa" />
#### Least 2 countries with the lowest population for each continents
<img width="491" height="255" alt="image" src="https://github.com/user-attachments/assets/7ef4dc2b-08a8-4a3b-b0ed-79f4ea03450b" />

#### Top 5 countries with the largest Area
<img width="407" height="118" alt="image" src="https://github.com/user-attachments/assets/ed8304fa-b384-4e34-add8-982156038fcc" />
#### Countries with 2 or more official languages
 <img width="149" height="41" alt="image" src="https://github.com/user-attachments/assets/e0d38835-c4e8-4f69-98d9-7bbca93f43da" />
#### Number of Countries whose start of week are not Monday
<img width="184" height="38" alt="image" src="https://github.com/user-attachments/assets/53f0a43b-1476-4136-9b8f-617b9f03a412" />

## Tech Stack
* Python - Programming
* Requests API - Data Extraction
* BigQuery - Database/Data wharehouse
* Github - Version control
