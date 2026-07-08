import os
import sys
import pymongo
import pandas as pd
import json
from dotenv import load_dotenv
from networks.exception.exception import NetworkSecurityException
from networks.logging.logger import logging
load_dotenv()

MONGO_DB_URL=os.getenv("MONGO_DB_URI")
import certifi
ca=certifi.where()

class ETL_Pipeline():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    def csv_to_json(self):
        try:
            data=pd.read_csv("/Users/subrat/Desktop/Network_Security/Network_Data/phisingData.csv")
            data.reset_index(drop=True,inplace=True)
            records=list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    def data_into_mongodb(self,database,collection,records):
        try:
            mongo_client=pymongo.MongoClient(MONGO_DB_URL)
            db=mongo_client[database]
            col=db[collection]
            col.insert_many(records)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
if __name__=="__main__":
    database="Manan"
    collection="networ_security"
    network=ETL_Pipeline()
    records=network.csv_to_json()
    print(records)
    no_of_records=network.data_into_mongodb(database,collection,records)
    print(no_of_records)








