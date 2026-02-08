--Top 2 countries with the largest Area for each continent
SELECT  continents,commonName, area
FROM (
SELECT continents,commonName,  area,
RANK() OVER (PARTITION BY continents ORDER BY area DESC) Area_Rank
FROM country-data-project-485122.staging.country_data
)
WHERE Area_Rank <=2
