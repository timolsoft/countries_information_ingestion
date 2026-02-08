--How many country is from West europe
SELECT count(countryID) As countryInWesternEurope
FROM country-data-project-485122.staging.country_data
WHERE subregion = "Western Europe"
