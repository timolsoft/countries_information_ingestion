--How many countries speaks english
SELECT COUNT(officialName) 
FROM `country-data-project-485122.staging.country_data` 
WHERE "English" IN UNNEST(SPLIT(languages,','))