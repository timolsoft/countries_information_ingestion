import pandas as pd
import requests


#response = requests.get(f"{url}?fields={field1}")


def extract_country_field1():
    field1 = "name,independent,unMember,startOfWeek,currencies,idd,capital,languages,region,subregion"
    url = "https://restcountries.com/v3.1/all"
    response = requests.get(f"{url}?fields={field1}")
    data = response.json()
    country_list=[]
    for row in data:
        startOfWeek = row['startOfWeek']
        commonName =row['name']['common']
        officialName =row['name']['official']
        independent =row['independent']
        unNumber =row['unMember']
        currencyName = None
        if row.get('currencies') and next(iter(row['currencies']), None):
            currencyCode = [next(iter(row['currencies']))]
            currencyName = row['currencies'][next(iter(row['currencies']))]['name']
            currencySymbol = row['currencies'][next(iter(row['currencies']))]['symbol']
        iddRoot =row['idd']['root']
        iddSuffixes=row['idd']['suffixes']
        capital=row['capital']
        region=row['region']
        subregion=row['subregion']
        languages = None
        if row.get('languages'):
            languages = list(row['languages'].values())
            lang = ', '.join(languages)
        mylist= {'startOfWeek':startOfWeek, 'commonName':commonName, 'officialName':officialName, 'independent':independent, 'unNumber':unNumber, 'currencyCode':currencyCode, 'currencyName':currencyName,'currencySymbol':currencySymbol, 'iddRoot':iddRoot, 'iddSuffixes':iddSuffixes, 'capital':capital, 'region':region, 'subregion':subregion, 'languages':lang}
        country_list.append(mylist)
    country_list_df = pd.DataFrame(country_list)
    return country_list_df
    

def extract_country_field2(): 
    url = "https://restcountries.com/v3.1/all"
    field2 ="name,area,population,continents"
    response = requests.get(f"{url}?fields={field2}")
    data2 = response.json()
    part_2=[]
    for rows in data2:
        nameCommon=rows['name']['common']
        area=rows['area']
        population=rows['population']
        continents=rows['continents']
        mylist={'nameCommon':nameCommon, 'area':area, 'population':population, 'continents':continents}
        part_2.append(mylist)
    country_list_df = pd.DataFrame(part_2)
    return country_list_df

    

    

