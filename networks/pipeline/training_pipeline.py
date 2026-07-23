import os
import sys

from networks.exception.exception import NetworkSecurityException
from networks.logging.logger import logging

from networks.entity.config import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTranformationConfig,
    ModelTrainerConfig,
)

from networks.components.data_ingestion import DataIngestion
from networks.components.data_validation import DataValaidation
from networks.components.data_tranformation import DataTransformation
from networks.components.model_trainer import ModelTrainer


class TrainingPipeline():
    def __init__(self, training_pipeline_config: TrainingPipelineConfig = None):
        try:
            if training_pipeline_config is None:
                training_pipeline_config = TrainingPipelineConfig()
            self.training_pipeline_config = training_pipeline_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def start_data_ingestion(self):
        try:
            logging.info("Initiating data ingestion config")
            data_ingestion_config = DataIngestionConfig(self.training_pipeline_config)

            logging.info("Starting data ingestion")
            data_ingestion = DataIngestion(data_ingestion_config)

            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info("Data ingestion completed")
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def start_data_validation(self):
        try:
            data_ingestion_artifact = self.start_data_ingestion()

            logging.info("Initiating data validation config")
            data_validation_config = DataValidationConfig(self.training_pipeline_config)

            logging.info("Starting data validation")
            data_validation = DataValaidation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_config=data_validation_config,
            )

            data_validation_artifact = data_validation.intialise_data_validation()
            logging.info("Data validation completed")
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def start_data_tranformation(self):
        try:
            data_validation_artifact = self.start_data_validation()

            logging.info("Initiating data transformation config")
            data_tranformation_config = DataTranformationConfig(
                training_pipeline_config=self.training_pipeline_config
            )

            logging.info("Starting data transformation")
            data_tranformation = DataTransformation(
                data_tranformation_config=data_tranformation_config,
                data_validation_artifact=data_validation_artifact,
            )

            data_tranformation_artifact = data_tranformation.initiate_data_tranformation()
            logging.info("Data transformation completed")
            return data_tranformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def start_model_trainer(self):
        try:
            data_tranformation_artifact = self.start_data_tranformation()

            logging.info("Initiating model trainer config")
            model_trainer_config = ModelTrainerConfig(self.training_pipeline_config)

            logging.info("Starting model training")
            model_trainer = ModelTrainer(
                model_trainer_config=model_trainer_config,
                data_tranformation_artifact=data_tranformation_artifact,
            )

            model_trainer_artifact = model_trainer.initiate_model_trainer()
            logging.info("Model training completed")
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def run_pipeline(self):
        try:
            model_trainer_artifact = self.start_model_trainer()
            logging.info("Training pipeline completed successfully")
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)


if __name__ == "__main__":
    training_pipeline = TrainingPipeline()
    artifact = training_pipeline.run_pipeline()
    print(artifact)