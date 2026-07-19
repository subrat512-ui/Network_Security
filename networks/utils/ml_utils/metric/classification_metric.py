import os,sys
from networks.exception.exception import NetworkSecurityException
from sklearn.metrics import f1_score,precision_score,recall_score
from networks.entity.artificats import ClassificationScoreArtifact


def classification_metric(y_true,y_pred):
    try:
        model_f1_score=f1_score(y_true,y_pred)
        model_precision=precision_score(y_true,y_pred)
        mode_recall=recall_score(y_true,y_pred)

        classification_score_artiafact=ClassificationScoreArtifact(f1_score=model_f1_score,precision=model_precision,recall=mode_recall)
        return classification_score_artiafact
    except Exception as e:
        raise NetworkSecurityException(e,sys)