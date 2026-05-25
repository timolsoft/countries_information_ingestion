with stg as (
    select * from {{ ref('stg_country_data') }}
)

select
    countryId,
    commonName,
    officialName,
    capital,
    independent,
    unMember,
    startOfWeek,
    idd
from stg
