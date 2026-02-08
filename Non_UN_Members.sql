--How many countries are not a United Nation member
select COUNT(officialName ) AS Non_UN_Members
from `country-data-project-485122.staging.country_data`
where unNumber = FALSE