--Top 5 countries with the lowest Area
  SELECT commonName, area
  FROM country-data-project-485122.staging.country_data
  ORDER BY area ASC
  LIMIT 5