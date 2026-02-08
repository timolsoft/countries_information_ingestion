--How many distinct continent and how many country from each
SELECT continents, COUNT(commonName) as No_of_Countries
FROM `country-data-project-485122.staging.country_data`
GROUP BY continents
ORDER BY continents;