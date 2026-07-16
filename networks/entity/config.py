from datetime import datetime
import os
from networks.constants import training_pipeline


class TrainingPipelineConfig:
    def __init__(self, timestamp=datetime.now()):
        timestamp = timestamp.strftime("%m_%d_%Y_%H_%M_%S")
        self.pipeline_name = training_pipeline.PIPELINE_NAME
        self.artifact_name = training_pipeline.ARTIFACT_DIR
        # every run gets its own timestamped folder, e.g. Artifacts/07_08_2026_10_30_00
        self.artifact_dir = os.path.join(self.artifact_name, timestamp)
        self.timestamp: str = timestamp


class DataIngestionConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        # e.g. Artifacts/07_08_2026_10_30_00/data_ingestion
        self.data_ingestion_dir: str = os.path.join(
            training_pipeline_config.artifact_dir,
            training_pipeline.DATA_INGESTION_DIR_NAME,
        )

        # e.g. .../data_ingestion/feature_store/phisingData.csv
        self.feature_store_file_path: str = os.path.join(
            self.data_ingestion_dir,
            training_pipeline.DATA_INGESTION_FEATURE_STORE_DIR,
            training_pipeline.FILE_NAME,
        )

        # e.g. .../data_ingestion/ingested/train.csv
        self.training_file_path: str = os.path.join(
            self.data_ingestion_dir,
            training_pipeline.DATA_INGESTION_INGESTED_DIR,
            training_pipeline.TRAIN_FILE_NAME,
        )

        # e.g. .../data_ingestion/ingested/test.csv
        self.testing_file_path: str = os.path.join(
            self.data_ingestion_dir,
            training_pipeline.DATA_INGESTION_INGESTED_DIR,
            training_pipeline.TEST_FILE_NAME,
        )

        self.train_test_split_ratio: float = training_pipeline.DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO
        self.collection_name: str = training_pipeline.DATA_INGESTION_COLLECTION_NAME
        self.database_name: str = training_pipeline.DATA_INGESTION_DATABASE_NAME



class DataValidationConfig:
    def __init__(self,training_pipeline_config:TrainingPipelineConfig):
        self.data_validation_dir=os.path.join(training_pipeline_config.artifact_dir,training_pipeline.DATA_VALIDATION_DIR_NAME)
        self.valid_data_dir=os.path.join(self.data_validation_dir,training_pipeline.DATA_VALIDATAION_VALID_DIR)
        self.invalid_data_dir=os.path.join(self.data_validation_dir,training_pipeline.DATA_VALIDATION_INVALID_DIR)
        self.vaild_train_data_file_path=os.path.join(self.valid_data_dir,training_pipeline.TRAIN_FILE_NAME)
        self.vaild_test_data_file_path=os.path.join(self.valid_data_dir,training_pipeline.TEST_FILE_NAME)
        self.invaild_train_data_file_path=os.path.join(self.invalid_data_dir,training_pipeline.TRAIN_FILE_NAME)
        self.invaild_test_data_file_path=os.path.join(self.invalid_data_dir,training_pipeline.TEST_FILE_NAME)
        self.drift_report_dir=os.path.join(self.data_validation_dir,training_pipeline.DATA_VALIDATION_DRIFT_REPORT_DIR,training_pipeline.DATA_VALIDATION_DRIFT_REPORT_FILENAME)




