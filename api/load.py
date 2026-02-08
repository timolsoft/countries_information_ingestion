from extract import extract_country_field1, extract_country_field2
import pandas as pd
from google.cloud import storage
import os
from google.cloud import bigquery
from google.api_core.exceptions import Conflict
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "country-data-project-key.json"

project_id = "country-data-project-485122"
bucket_name = "country-bucket-02" 
    

storage_client= storage.Client()
bucket = storage_client.bucket(bucket_name)
bucket.location = "US"
if not bucket.exists():
    bucket.create(project=project_id, location="US")

    print(f"Bucket {bucket.name} created")
else:
    print(f"Bucket {bucket.name} already exists")

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

for col in countryData.columns:
    null_count = countryData[col].isnull().sum()
    duplicate_count = countryData[col].duplicated().sum()
    print(f"Column '{col}' has {null_count} null values")
client = bigquery.Client()
project_id = client.project
dataset_id = f"{project_id}.staging"
table_id = f"{dataset_id}.country_data"

dataset = bigquery.Dataset(dataset_id)
dataset.location = "US"

try: 
    client.create_dataset(dataset)
    print(f"Dataset {dataset_id} created.")
except Conflict:
    pass

job = client.load_table_from_dataframe(
    countryData, table_id,     
    job_config=bigquery.LoadJobConfig(
        autodetect=True,               
        write_disposition="WRITE_APPEND"  
    )
)
job.result()
print(f"Loaded {job.output_rows} rows into {table_id}.")




