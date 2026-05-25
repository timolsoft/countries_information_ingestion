with stg as (
    select * from {{ ref('stg_country_data') }}
),

-- Count how many countries use each currency name
-- to pick the most common one per currency code
currency_ranked as (
    select
        currencyCode,
        currencyName,
        currencySymbol,
        count(*) as usage_count,
        row_number() over (
            partition by currencyCode
            order by count(*) desc
        ) as rn
    from stg
    where currencyCode is not null
    group by currencyCode, currencyName, currencySymbol
)

select
    row_number() over (order by currencyCode) as currencyId,
    currencyCode,
    currencyName,
    currencySymbol
from currency_ranked
where rn = 1
