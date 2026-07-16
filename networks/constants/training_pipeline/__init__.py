
import os
import sys
import numpy as np
import pandas as pd
 
"""
Defining common constant variables for the whole training pipeline
"""
TARGET_COLUMN = "Result"
PIPELINE_NAME: str = "NetworkSecurity"
ARTIFACT_DIR: str = "Artifacts"
FILE_NAME: str = "phisingData.csv"
 
TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"
SCHEMA_FILE_PATH=os.path.join("data_schema","schema.yaml")
"""
Data Ingestion related constants
"""
DATA_INGESTION_COLLECTION_NAME: str = "networ_security"
DATA_INGESTION_DATABASE_NAME: str = "Manan"
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2
 
"""
Data validation related constant s
"""
DATA_VALIDATION_DIR_NAME="datavalidation"
DATA_VALIDATAION_VALID_DIR="validated"
DATA_VALIDATION_INVALID_DIR="invalid"
DATA_VALIDATION_DRIFT_REPORT_DIR="driftreport"
DATA_VALIDATION_DRIFT_REPORT_FILENAME="report.yaml"
