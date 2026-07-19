
import os,sys
from networks.exception.exception import NetworkSecurityException

class NetworkModel:
    def __init__(self,preproceesor,model):
        try:
            self.preprocessor=preproceesor
            self.model=model
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def predict(self,x):
        try:
            x_transform=self.preprocessor.transform(x)
            y_hat=self.model.predict(x_tranform)
            return y_hat
        except Exception as e:
            raise NetworkSecurityException(e,sys)