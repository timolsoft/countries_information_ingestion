import pandas as pd
import requests
import logging
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
BASE_URL = "https://restcountries.com/v3.1/all"
 
 
def extract_country_field1() -> pd.DataFrame:
    """
    Fetches core country metadata from the REST Countries API.
    Returns an empty DataFrame on failure rather than crashing the pipeline.
    """
    fields = "name,independent,unMember,startOfWeek,currencies,idd,capital,languages,region,subregion"
 
    try:
        response = requests.get(f"{BASE_URL}?fields={fields}", timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch field1 data: %s", e)
        return pd.DataFrame()
 
    country_list = []
 
    for row in data:
        # --- currency (optional field) ---
        currency_code = None
        currency_name = None
        currency_symbol = None
        currencies = row.get("currencies", {})
        if currencies:
            code = next(iter(currencies))
            currency_code = code
            currency_name = currencies[code].get("name")
            currency_symbol = currencies[code].get("symbol")
 
        # --- idd (optional suffixes) ---
        idd = row.get("idd", {})
        idd_root = idd.get("root", "")
        idd_suffixes = idd.get("suffixes", [])
        # If there's exactly one suffix, concatenate; otherwise store root only
        if len(idd_suffixes) == 1:
            idd_combined = idd_root + idd_suffixes[0]
        else:
            idd_combined = idd_root
 
        # --- languages (optional field) ---
        languages = row.get("languages", {})
        lang = ", ".join(languages.values()) if languages else None
 
        country_list.append({
            "startOfWeek":    row.get("startOfWeek"),
            "commonName":     row["name"]["common"],
            "officialName":   row["name"]["official"],
            "independent":    row.get("independent"),
            "unMember":       row.get("unMember"),
            "currencyCode":   currency_code,
            "currencyName":   currency_name,
            "currencySymbol": currency_symbol,
            "idd":            idd_combined,
            "capital":        row.get("capital", [None])[0] if row.get("capital") else None,
            "region":         row.get("region"),
            "subregion":      row.get("subregion"),
            "languages":      lang,
        })
 
    return pd.DataFrame(country_list)
 
 
def extract_country_field2() -> pd.DataFrame:
    """
    Fetches area, population, and continent data from the REST Countries API.
    Returns an empty DataFrame on failure rather than crashing the pipeline.
    """
    fields = "name,area,population,continents"
 
    try:
        response = requests.get(f"{BASE_URL}?fields={fields}", timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch field2 data: %s", e)
        return pd.DataFrame()
 
    part_2 = []
 
    for row in data:
        continents = row.get("continents", [])
        part_2.append({
            "nameCommon":  row["name"]["common"],
            "area":        row.get("area"),
            "population":  row.get("population"),
            "continents":  continents[0] if len(continents) == 1 else ", ".join(continents),
        })
 
    return pd.DataFrame(part_2)