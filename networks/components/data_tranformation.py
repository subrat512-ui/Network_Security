import sys,os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from networks.entity.config import DataTranformationConfig
from networks.entity.artificats import DataValidationArtifact,DataTransformationArtifact
from networks.exception.exception import NetworkSecurityException
from networks.logging.logger import logging
from sklearn.pipeline import Pipeline
from networks.constants.training_pipeline import TARGET_COLUMN
from networks.constants.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS
from networks.utils.main_utils.utils import save_numpy_array,save_obj



class DataTransformation:
    def __init__(self,data_tranformation_config:DataTranformationConfig,data_validation_artifact:DataValidationArtifact):
        try:
            self.data_tranformation_config=data_tranformation_config
            self.data_validation_artifact=data_validation_artifact
        except  Exception as e:
            raise NetworkSecurityException(e,sys)
    

    @staticmethod
    def read(file_path: str):
        try:
            df=pd.read_csv(file_path)
            return df
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def generate_tranformed_object(self):
        try:
            imputer=KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            pipeline=Pipeline([("impoter",imputer)])
            return pipeline
        except Exception as e:
            raise NetworkSecurityException(e,sys)

        
    def initiate_data_tranformation(self):
        try:
            train_data=DataTransformation.read(self.data_validation_artifact.valid_train_file_path)
            test_data=DataTransformation.read(self.data_validation_artifact.valid_test_file_path)

            input_train_feature_data=train_data.drop(columns=TARGET_COLUMN)
            output_feature_train_data=train_data[TARGET_COLUMN]
            output_feature_train_data.replace({-1:0},inplace=True)

            input_test_feature_data=test_data.drop(columns=TARGET_COLUMN)
            output_feataue_test_data=test_data[TARGET_COLUMN]
            output_feataue_test_data.replace({-1:0},inplace=True)

            preprocessor=self.generate_tranformed_object()

            preprocessor_object=preprocessor.fit(input_train_feature_data)

            input_feature_train_transformed_data=preprocessor_object.transform(input_train_feature_data)

            input_feature_test_transformed_data=preprocessor_object.transform(input_test_feature_data)

            train_np=np.c_[input_feature_train_transformed_data,np.array(output_feature_train_data)]
            test_np=np.c_[input_feature_test_transformed_data,np.array(output_feataue_test_data)]


            save_numpy_array(file_path=self.data_tranformation_config.test_file_path,arr=test_np)

            save_numpy_array(file_path=self.data_tranformation_config.train_file_path,arr=train_np)

            save_obj(file_path=self.data_tranformation_config.data_transformed_object,obj=preprocessor_object)

            save_obj("final_model/preprocessor.pkl", preprocessor_object)

            data_tranformation_artifact=DataTransformationArtifact(transformed_object_file_path=self.data_tranformation_config.data_transformed_object,transformed_train_file_path=self.data_tranformation_config.train_file_path,transformed_test_file_path=self.data_tranformation_config.test_file_path)
            return data_tranformation_artifact


        except Exception as e:
            raise NetworkSecurityException(e,sys)
