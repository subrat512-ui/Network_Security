from networks.entity.config import DataValidationConfig,TrainingPipelineConfig
from networks.logging.logger import logging
from networks.exception.exception import NetworkSecurityException
from networks.entity.artificats import DataIngestionArtifact,DataValidationArtifact
from networks.constants.training_pipeline import SCHEMA_FILE_PATH
import os,sys
from scipy.stats import ks_2samp
from networks.utils.main_utils import utils
import pandas as pd

class DataValaidation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,data_validation_config:DataValidationConfig):
        try:
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_config=data_validation_config
            self.schema=utils.read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    @staticmethod
    def read(file_path):
        try:
            df=pd.read_csv(file_path)
            return df
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def validate_columns(self,df:pd.DataFrame):
        try:
            no_of_column=len(self.schema["columns"])
            logging.info(f"no. of columns in schema{no_of_column}\n")
            logging.info(f"no. of columns in data frame{len(df.columns)}")
            if(len(df.columns)==no_of_column):
                return True
            return False
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    def test_data_drift(self,base_df,current_df,threshold=0.05):
        try:
            status=False
            report={}
            for column in base_df.columns:
                d1=base_df[column]
                d2=current_df[column]
                is_same_dist=ks_2samp(d1,d2)
                if threshold<=is_same_dist.pvalue:
                    is_found=False
                else:
                    is_found=True
                    status=True
                report.update({column:{
                    "p_score":float(is_same_dist.pvalue),
                    "drift_status":is_found
                }})
            drift_report_file_path=os.path.join(self.data_validation_config.drift_report_dir)
            dir_name=os.path.dirname(drift_report_file_path)
            os.makedirs(dir_name,exist_ok=True)
            utils.write_yaml_file(drift_report_file_path,report)
            return status
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    def intialise_data_validation(self):
        try:
            train_file_path=self.data_ingestion_artifact.train_file_path
            test_file_path=self.data_ingestion_artifact.test_file_path

            train_data=DataValaidation.read(train_file_path)
            test_data=DataValaidation.read(test_file_path)

            status=self.validate_columns(train_data)
            if not status:
                print("Training data dosen't has required no. of columns")
            status=self.validate_columns(test_data)
            if not status:
                print("Testing data dosen't has required no. of columns")
            
            status=self.test_data_drift(base_df=test_data,current_df=train_data)
            valid_train_data=os.path.join(self.data_validation_config.vaild_train_data_file_path)
            dir_name=os.path.dirname(valid_train_data)
            os.makedirs(dir_name,exist_ok=True)
            train_data.to_csv(valid_train_data)
            valid_test_data=os.path.join(self.data_validation_config.vaild_test_data_file_path)
            dir_name=os.path.dirname(valid_test_data)
            os.makedirs(dir_name,exist_ok=True)
            test_data.to_csv(valid_test_data)

            data_validation_artifact=DataValidationArtifact(validation_status=not status,valid_train_file_path=self.data_validation_config.vaild_train_data_file_path,valid_test_file_path=self.data_validation_config.vaild_test_data_file_path,invalid_train_file_path=self.data_validation_config.invaild_train_data_file_path,invalid_test_file_path=self.data_validation_config.invaild_test_data_file_path,drift_report_file_path=self.data_validation_config.drift_report_dir)
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)

        
        



