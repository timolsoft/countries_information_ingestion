--How many country have more than 1 official language
SELECT COUNT(officialName)
FROM `country-data-project-485122.staging.country_data` 
WHERE ARRAY_LENGTH(SPLIT(languages,','))> 1;