with stg as (
    select * from {{ ref('stg_country_data') }}
),

region_ranked as (
    select
        continents,
        region,
        subregion,
        count(*) as usage_count,
        row_number() over (
            partition by region, coalesce(subregion, '')
            order by count(*) desc
        ) as rn
    from stg
    where region is not null
    group by continents, region, subregion
)

select
    row_number() over (order by region, subregion) as regionId,
    continents                                      as continent,
    region,
    subregion
from region_ranked
where rn = 1
