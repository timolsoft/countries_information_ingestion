--How many country has not yet gain independence
SELECT COUNT(officialName)
FROM `country-data-project-485122.staging.country_data`
WHERE independent = FALSE;