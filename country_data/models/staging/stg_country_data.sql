with source as (
    select * from {{ source('staging', 'country_data') }}
),

cleaned as (
    select
        countryId,
        commonName,
        officialName,
        startOfWeek,
        independent,
        unMember,
        nullif(trim(currencyCode), '')   as currencyCode,
        nullif(trim(currencyName), '')   as currencyName,
        nullif(trim(currencySymbol), '') as currencySymbol,
        nullif(trim(idd), '')            as idd,
        nullif(trim(capital), '')        as capital,
        nullif(trim(region), '')         as region,
        nullif(trim(subregion), '')      as subregion,
        nullif(trim(languages), '')      as languages,
        area,
        population,
        nullif(trim(continents), '')     as continents
    from source
    where commonName is not null
)

select * from cleaned
