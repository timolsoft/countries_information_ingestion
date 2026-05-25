with stg as (
    select * from {{ ref('stg_country_data') }}
),

split as (
    select
        countryId,
        trim(lang) as languageName
    from stg,
    unnest(split(languages, ',')) as lang
    where languages is not null
)

select
    row_number() over (order by countryId, languageName) as languageId,
    countryId,
    languageName
from split
