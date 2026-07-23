import sklearn
import numpy as np
import os, sys
import pandas as pd
from networks.entity.config import ModelTrainerConfig
from networks.entity.artificats import DataTransformationArtifact, ModelTrainerArtifact
from networks.exception.exception import NetworkSecurityException
from networks.logging.logger import logging
from networks.utils.main_utils.utils import load_numpy_array, load_obj, evaluate, save_obj
from networks.constants import training_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier, GradientBoostingClassifier
from networks.utils.ml_utils.metric.classification_metric import classification_metric
from networks.utils.ml_utils.model_util.estimator import NetworkModel


class ModelTrainer:
    def __init__(self, data_tranformation_artifact: DataTransformationArtifact, model_trainer_config: ModelTrainerConfig):
        try:
            self.data_tranformation_artifact = data_tranformation_artifact
            self.model_trainer_config = model_trainer_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def train_models(self, X_train, Y_train, X_test, Y_test):
        models = {
            "Random Forest": RandomForestClassifier(verbose=1),
            "Decision Tree": DecisionTreeClassifier(),
            "Gradient Boosting": GradientBoostingClassifier(verbose=1),
            "Logistic Regression": LogisticRegression(),
            "AdaBoost": AdaBoostClassifier(),
        }

        # trimmed grids — enough to explore, not so much it takes forever
        params = {
            "Decision Tree": {
                'criterion': ['gini', 'entropy', 'log_loss'],
                'max_features': ['sqrt', 'log2'],
            },
            "Random Forest": {
                'n_estimators': [32, 128, 256],
                'max_features': ['sqrt', 'log2'],
            },
            "Gradient Boosting": {
                'learning_rate': [.1, .01],
                'subsample': [0.7, 0.85],
                'n_estimators': [32, 128],
            },
            "Logistic Regression": {},
            "AdaBoost": {
                'learning_rate': [.1, .01],
                'n_estimators': [32, 128],
            }
        }

        report = evaluate(X_train=X_train, Y_train=Y_train, X_test=X_test, Y_test=Y_test,
                           models=models, param=params)

        best_model_name = max(report, key=report.get)
        best_model_score = report[best_model_name]
        best_model = models[best_model_name]

        logging.info(f"Best model: {best_model_name} with test accuracy: {best_model_score}")

        y_pred_train = best_model.predict(X_train)
        classification_train_artifact = classification_metric(Y_train, y_pred_train)

        y_pred_test = best_model.predict(X_test)
        classification_test_artifact = classification_metric(Y_test, y_pred_test)

        train_score = classification_train_artifact.f1_score
        test_score = classification_test_artifact.f1_score

        # guardrails using the constants that were previously unused
        if best_model_score < training_pipeline.MODEL_ACCURACY_THRESHOLD:
            raise NetworkSecurityException(
                f"No model met the minimum accuracy threshold "
                f"({best_model_score:.4f} < {training_pipeline.MODEL_ACCURACY_THRESHOLD})",
                sys
            )

        score_diff = abs(train_score - test_score)
        if score_diff > training_pipeline.MODEL_ACCURACY_TRAIN_TEST_DIFFERENCE:
            raise NetworkSecurityException(
                f"Model is overfitting: train/test score gap ({score_diff:.4f}) "
                f"exceeds allowed difference ({training_pipeline.MODEL_ACCURACY_TRAIN_TEST_DIFFERENCE})",
                sys
            )
        
        save_obj(file_path='/Users/subrat/Desktop/Network_Security/final_model/model.pkl',obj=best_model)

        return [classification_test_artifact, classification_train_artifact, best_model]

    def initiate_model_trainer(self):
        try:
            train_np = load_numpy_array(self.data_tranformation_artifact.transformed_train_file_path)
            test_np = load_numpy_array(self.data_tranformation_artifact.transformed_test_file_path)

            X_train = train_np[:, :-1]
            Y_train = train_np[:, -1]
            X_test = test_np[:, :-1]
            Y_test = test_np[:, -1]

            train_result = self.train_models(X_train=X_train, Y_train=Y_train, X_test=X_test, Y_test=Y_test)
            preprocessor = load_obj(self.data_tranformation_artifact.transformed_object_file_path)

            model = train_result[2]

            final_model = NetworkModel(preproceesor=preprocessor, model=model)

            save_obj(file_path=self.model_trainer_config.trained_model_file, obj=final_model)

            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file,
                test_data_score=train_result[0],
                train_data_score=train_result[1],
            )
            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)