--How many country whose start of the week is not Monday
SELECT COUNT(officialName) AS startOfWeek
FROM `country-data-project-485122.staging.country_data`
WHERE startOfWeek != "monday";