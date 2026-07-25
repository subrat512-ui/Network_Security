import os,sys
from fastapi.responses import RedirectResponse
import pymongo
from networks.pipeline.training_pipeline import TrainingPipeline
from networks.exception.exception import NetworkSecurityException
from networks.logging.logger import logging
from networks.entity.config import TrainingPipelineConfig
import certifi
ca=certifi.where()
from dotenv import  load_dotenv
load_dotenv()
mongo_db_url=os.getenv("MONGO_DB_URI")
from networks.utils.main_utils.utils import load_obj
from fastapi import FastAPI,UploadFile,Request,File
import pandas as pd
from uvicorn import run as app_run
from networks.utils.ml_utils.model_util.estimator import NetworkModel
from networks.constants.training_pipeline import DATA_INGESTION_COLLECTION_NAME,DATA_INGESTION_DATABASE_NAME
client=pymongo.MongoClient(mongo_db_url)

database=client[DATA_INGESTION_DATABASE_NAME]
collection=database[DATA_INGESTION_COLLECTION_NAME]

app=FastAPI()
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templates")



@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")



@app.get('/train')
async def train():
    try:
        training_pipeline_config=TrainingPipelineConfig()
        pipeline=TrainingPipeline(training_pipeline_config=training_pipeline_config)
        pipeline.run_pipeline()
        return "Training is successfull"
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    

@app.post('/predict')
async def predict_data(request:Request,file:UploadFile=File(...)):
    try:
        # Read CSV normally (no index_col) so feature columns are not consumed as index
        df=pd.read_csv(file.file)

        # Drop the pandas index artifact if it slipped through (saved without index=False)
        if 'Unnamed: 0' in df.columns:
            df = df.drop(columns=['Unnamed: 0'])

        print("Uploaded CSV columns:", list(df.columns))

        preprocesser=load_obj(file_path="final_model/preprocessor.pkl")
        model=load_obj(file_path="final_model/model.pkl")
        network_model=NetworkModel(preproceesor=preprocesser,model=model)
        print(df.iloc[0])

        # Align columns to what the preprocessor was trained on
        expected_features = list(preprocesser.feature_names_in_)
        missing = [c for c in expected_features if c not in df.columns]
        if missing:
            # Raise a plain exception so the outer except handler wraps it
            # (NetworkSecurityException uses sys.exc_info() which only works inside an except block)
            raise ValueError(
                f"Uploaded CSV is missing required feature columns: {missing}. "
                f"Expected columns: {expected_features}"
            )
        df = df[expected_features]

        y_pred=network_model.predict(df)
        print(y_pred)
        df["predicted column"]=y_pred
        os.makedirs("predicted_data", exist_ok=True)
        df.to_csv("predicted_data/output.csv", index=False)
        table_html = df.to_html(classes='table table-striped')
        print(table_html)
        return templates.TemplateResponse(request, "table.html", {"table": table_html})

    except Exception as e:
        # Defensive: if exc_info() returns no traceback (e.g. re-raised), still surface the error
        try:
            raise NetworkSecurityException(e, sys)
        except AttributeError:
            raise NetworkSecurityException(str(e), sys) from e


if __name__=="__main__":

    app_run(app,host="0.0.0.0",port=8000)