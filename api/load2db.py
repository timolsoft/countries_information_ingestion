from pathlib import Path
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from extract import extract_country_field1, extract_country_field2
import pandas as pd
import psycopg2


conn = psycopg2.connect(
    dbname="mydb",
    user="user",
    password="mypassword",
    host="127.0.0.1",
    port=55432,
)

cursor = conn.cursor()

data1= extract_country_field1()
data2= extract_country_field2()

#mergeing dataframes
countryData = pd.merge(data1, data2, left_on='commonName', right_on='nameCommon', how='inner')
countryData.drop(columns=['nameCommon'], inplace=True)

#cleaning columns
countryData['currencyCode'] = countryData['currencyCode'].astype(str).str.strip("[]").str.strip("'")
countryData['capital']=countryData['capital'].astype(str).str.strip("[]").str.strip("'").str.strip('"')
countryData['continents']=countryData['continents'].astype(str).str.strip("[]").str.strip("'")
countryData['iddSuffixes']=countryData['iddSuffixes'].astype(str).str.strip("[]").str.strip("'")
#concatenante iddroot and suffixes
countryData['idd'] = countryData['iddRoot'] + countryData['iddSuffixes']
countryData.drop(columns=['iddRoot','iddSuffixes'], inplace=True)
countryData["countryId"] = countryData.index + 1
print(countryData.head())

#check data quality
for col in countryData.columns:
    null_count = countryData[col].isnull().sum()
    duplicate_count = countryData[col].duplicated().sum()
    print(f"Column '{col}' has {null_count} null values and {duplicate_count} duplicates.")
      
# create table in database
create_query_file = open("create_countryData.sql", "r")
create_query = create_query_file.read()
cursor.execute(create_query)

conn.commit()

#load data to database

mydata =countryData.intertuples(index=False, name=None)
load_data_query = open("populate_db.sql", "r")
cursor.executemany(load_data_query.read(), mydata)
conn.commit()
cursor.close()
















