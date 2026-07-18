from networks.exception.exception import NetworkSecurityException
from networks.logging.logger import logging
from networks.components.data_ingestion import DataIngestion
from networks.components.data_validation import DataValaidation
from networks.components.data_tranformation import DataTransformation
from networks.entity.config import TrainingPipelineConfig,DataIngestionConfig,DataValidationConfig,DataTranformationConfig
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
        data_validation_config=DataValidationConfig(training_pipeline_config)
        data_validation=DataValaidation(data_validation_config=data_validation_config,data_ingestion_artifact=artifact)
        validation_artifact=data_validation.intialise_data_validation()
        data_tranformation_config=DataTranformationConfig(training_pipeline_config=training_pipeline_config)
        data_tranformation=DataTransformation(data_tranformation_config=data_tranformation_config,data_validation_artifact=validation_artifact)
        data_tranformation_artifact=data_tranformation.initiate_data_tranformation()

    except Exception as e:
        raise NetworkSecurityException(e,sys)