--How many countries speaks French
SELECT count(officialName) As No_French_Speaking_Country FROM `country-data-project-485122.staging.country_data` 
WHERE "French" IN UNNEST(SPLIT(languages))