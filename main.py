from networks.exception.exception import NetworkSecurityException
from networks.logging.logger import logging
from networks.components.data_ingestion import DataIngestion
from networks.entity.config import TrainingPipelineConfig,DataIngestionConfig
import sys



if __name__=="__main__":
    try:
        logging.info("Initiating training_pipeline_config")
        training_pipeline_config=TrainingPipelineConfig()
        logging.info("initiing data ingestion config")
        data_ingestion_config=DataIngestionConfig(training_pipeline_config)
        logging.info("initiating data ingestion")
        data_ingestion=DataIngestion(data_ingestion_config)
        logging.info("creating artifact instance")
        artifact=data_ingestion.initiate_data_ingestion()
        logging.info("executed data ingestion")
    except Exception as e:
        raise NetworkSecurityException(e,sys)