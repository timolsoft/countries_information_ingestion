with stg as (
    select * from {{ ref('stg_country_data') }}
),

dim_region as (
    select * from {{ ref('dim_region') }}
),

dim_currency as (
    select * from {{ ref('dim_currency') }}
)

select
    s.countryId,
    r.regionId,
    c.currencyId,
    s.population,
    s.area
from stg s
left join dim_region r
    on s.region = r.region
    and coalesce(s.subregion, '') = coalesce(r.subregion, '')
left join dim_currency c
    on s.currencyCode = c.currencyCode
