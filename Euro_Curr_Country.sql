---How many country official currency is Euro
SELECT count(officialName) As Euro_Country
FROM country-data-project-485122.staging.country_data
WHERE currencyName = "Euro";