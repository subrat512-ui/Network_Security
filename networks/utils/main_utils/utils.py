import yaml
import sys
from networks.logging.logger import logging
from networks.exception.exception import NetworkSecurityException
import os
import numpy as np
import pickle
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import accuracy_score

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
    


def load_obj(file_path):
    try:
        if not os.path.exists(file_path):
            raise Exception(f"file not found {file_path}")
        with open(file_path,mode='rb') as file_obj:
            return pickle.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    



def load_numpy_array(file_path):
    try:
        if not os.path.exists(file_path):
            raise Exception(f"file not found {file_path}")
        with open(file_path,mode='rb') as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    


def evaluate(X_train, Y_train, X_test, Y_test, models, param):
    try:
        report = {}
        for name, model in models.items():
            para = param[name]

            # RandomizedSearchCV samples a fixed number of combos instead of all of them,
            # and n_jobs=-1 uses all CPU cores instead of just one
            n_iter = min(10, sum(len(v) for v in para.values()) or 1) if para else 1
            rs = RandomizedSearchCV(
                model, para, cv=3, n_iter=n_iter,
                n_jobs=1, random_state=42
            )
            rs.fit(X_train, Y_train)

            model.set_params(**rs.best_params_)
            model.fit(X_train, Y_train)

            y_test_pred = model.predict(X_test)
            score=accuracy_score(Y_test, y_test_pred)

            report[name] = score   # keyed by name now, not the model object
        return report

    except Exception as e:
        raise NetworkSecurityException(e, sys)