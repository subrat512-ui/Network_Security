from networks.exception.exception import NetworkSecurityException
from networks.entity.config import DataIngestionConfig
from networks.logging.logger import logging
from networks.entity.artificats import DataIngestionArtifact
from dotenv import load_dotenv
import pymongo
import pandas as pd
import numpy as np
import sys
import os
load_dotenv()
from sklearn import model_selection
MONFO_DB_URL=os.getenv("MONGO_DB_URI")

class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            self.data_ingestion_config=data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    
    def export_data(self):
        try:
            database=self.data_ingestion_config.database_name
            collection=self.data_ingestion_config.collection_name
            print(f"Database: {database}")
            print(f"Collection: {collection}")
            logging.info("Settting up mongoclient")
            self.mongo_client=pymongo.MongoClient(MONFO_DB_URL)
            records=self.mongo_client[database][collection]
            print("Document count:", records.count_documents({}))
            df=pd.DataFrame(list(records.find()))
            print("DataFrame shape:", df.shape)
            print(df.head())

            if "_id" in df.columns.to_list():
                df.drop(columns="_id",inplace=True,axis=1)
            df.replace({"na":np.nan},inplace=True)
            return df
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def export_data_to_feature_store(self,dataframe:pd.DataFrame):
        try:
            feature_store_path=self.data_ingestion_config.feature_store_file_path
            dir_path=os.path.dirname(feature_store_path)
            os.makedirs(dir_path,exist_ok=True)
            logging.info("saving data in feature store")
            dataframe.to_csv(feature_store_path,index=False,header=True)
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def split_train_test(self,dataframe:pd.DataFrame):
        try:
            train_data,test_data=model_selection.train_test_split(dataframe,test_size=self.data_ingestion_config.train_test_split_ratio)
            logging.info("Performed Train test split")
            train_file_path = self.data_ingestion_config.training_file_path
            test_file_path = self.data_ingestion_config.testing_file_path

            # Create directories if they don't exist
            os.makedirs(os.path.dirname(train_file_path), exist_ok=True)
            os.makedirs(os.path.dirname(test_file_path), exist_ok=True)

            logging.info("Saving training and test data")

            train_data.to_csv(train_file_path, index=False, header=True)
            test_data.to_csv(test_file_path, index=False, header=True)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def initiate_data_ingestion(self):
        try:
            dataframe=self.export_data()
            self.export_data_to_feature_store(dataframe)
            self.split_train_test(dataframe)

            data_ingestion_artifact=DataIngestionArtifact(train_file_path=self.data_ingestion_config.training_file_path,test_file_path=self.data_ingestion_config.testing_file_path)
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)


