import yaml
import sys
from networks.logging.logger import logging
from networks.exception.exception import NetworkSecurityException
import os
import numpy as np
import pickle

def read_yaml_file(file_path: str):
    try:
        with open(file_path,mode='rb') as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    

def write_yaml_file(file_path: str,content: object ,replace: bool=False):
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path),exist_ok=True)
        with open(file_path,mode='w') as file:
            yaml.dump(content,file)
    except  Exception as e:
        raise NetworkSecurityException(e,sys)
    

def save_numpy_array(file_path,arr):
    try:
        dir_name=os.path.dirname(file_path)
        os.makedirs(dir_name,exist_ok=True)
        with open(file_path,mode='wb') as file:
            np.save(file,arr)
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    

def save_obj(file_path,obj):
    try:
        dir_name=os.path.dirname(file_path)
        os.makedirs(dir_name,exist_ok=True)
        with open(file_path,mode='wb') as file:
            pickle.dump(file=file,obj=obj)
    except Exception as e:
        raise NetworkSecurityException(e,sys)
