--Top 5 countries with the largest Area
  SELECT commonName, area
  FROM country-data-project-485122.staging.country_data
  ORDER BY area DESC
  LIMIT 5