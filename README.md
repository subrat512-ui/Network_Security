# 🛡️ Network Security — Phishing URL Detection

An end-to-end **machine learning pipeline** that detects phishing URLs. It pulls training data from MongoDB, validates and transforms it, trains and evaluates several classifiers, and exposes the best model behind a **FastAPI** service for real-time predictions via CSV upload.

The dataset is the [UCI Phishing Websites](https://archive.ics.uci.edu/ml/datasets/phishing+websites) dataset (`phisingData.csv`) — 30 URL-derived numeric features per sample, with a binary `Result` label (phishing / legitimate).

---

## 📑 Table of Contents

- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Pipeline Stages](#-pipeline-stages)
  - [1. Data Ingestion](#1-data-ingestion)
  - [2. Data Validation](#2-data-validation)
  - [3. Data Transformation](#3-data-transformation)
  - [4. Model Training](#4-model-training)
- [API](#-api)
- [Configuration](#-configuration)
- [Setup & Run](#-setup--run)
- [Usage](#-usage)
- [Artifacts & Outputs](#-artifacts--outputs)

---

## 🏗️ Architecture

```
                ┌──────────────────────┐
                │  MongoDB Atlas       │
                │  (raw phishing data) │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │  Data Ingestion      │  feature store + train/test split
                └──────────┬───────────┘
                           ▼
                ┌──────────────────────┐
                │  Data Validation     │  schema check + drift report
                └──────────┬───────────┘
                           ▼
                ┌──────────────────────┐
                │  Data Transformation │  KNN imputation → numpy arrays
                └──────────┬───────────┘
                           ▼
                ┌──────────────────────┐
                │  Model Trainer       │  5 classifiers, hyper-param search
                │  (best → final.pkl)  │  accuracy & overfit guardrails
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │  FastAPI (app.py)    │  /train, /predict endpoints
                └──────────────────────┘
```

Every run creates a **timestamped artifact folder** under `Artifacts/`, so historical runs never overwrite each other.

---

## 🧰 Tech Stack

- **Python 3.10**
- **MongoDB** (via `pymongo`) — raw data source
- **pandas / numpy** — data wrangling
- **scikit-learn** — preprocessing (`KNNImputer`) + 5 classifiers
- **FastAPI + Uvicorn** — HTTP API + auto-reload
- **Jinja2** — HTML templating for the prediction response
- **python-dotenv, certifi** — secrets / TLS

---

## 📂 Project Structure

```
Network_Security/
├── app.py                              # FastAPI entrypoint (training & prediction)
├── push_data.py                        # Pushes phisingData.csv → MongoDB
├── requirements.txt
├── Dockerfile
├── data_schema/
│   └── schema.yaml                     # Expected column contract
├── final_model/
│   ├── preprocessor.pkl                # KNN-imputer pipeline
│   └── model.pkl                       # Trained classifier
├── logs/                               # Rotating log files
├── network/                            # Local venv (not tracked)
├── networks/
│   ├── components/                     # Pipeline stages
│   │   ├── data_ingestion.py
│   │   ├── data_validation.py
│   │   ├── data_tranformation.py
│   │   └── model_trainer.py
│   ├── pipeline/
│   │   └── training_pipeline.py        # Orchestrates the 4 stages
│   ├── entity/
│   │   ├── config.py                   # *Config dataclasses
│   │   └── artificats.py               # *Artifact dataclasses
│   ├── constants/
│   │   └── training_pipeline/__init__.py
│   ├── cloud/
│   │   └── data_sync.py
│   ├── exception/exception.py          # NetworkSecurityException
│   ├── logging/logger.py
│   └── utils/
│       ├── main_utils/utils.py         # load_obj, save_obj, evaluate
│       └── ml_utils/
│           ├── metric/classification_metric.py
│           └── model_util/estimator.py # NetworkModel(preprocessor, model)
├── Network_Data/
│   └── phisingData.csv                 # Source dataset
├── Notebooks/                          # EDA notebooks
├── templates/
│   └── table.html                      # Jinja2 result page
├── predict.csv                         # Sample input for /predict
└── predicted_data/                     # CSV output of /predict
```

---

## ⚙️ Pipeline Stages

### 1. Data Ingestion
- Connects to MongoDB (`MONGO_DB_URI` env var → `Manan.networ_security`).
- Pulls every document, drops the Mongo `_id`, and replaces `"na"` → `NaN`.
- Saves the full DataFrame to `feature_store/phisingData.csv`.
- Performs an **80/20 train-test split** and persists both files.

**Artifact:** `DataIngestionArtifact(train_file_path, test_file_path)`

### 2. Data Validation
- Reads `data_schema/schema.yaml` and asserts the column count matches the train/test frames.
- Runs a **two-sample Kolmogorov–Smirnov test** between train and test for every column, producing a drift report (`report.yaml`). If p-value < 0.05, drift is flagged.
- Writes the (validated) train/test CSVs to the validated folder.

**Artifact:** `DataValidationArtifact(validation_status, valid_*, invalid_*, drift_report_file_path)`

### 3. Data Transformation
- Drops the `Result` column (target) and remaps `-1 → 0` so the label becomes binary `0/1`.
- Fits a **`KNNImputer(n_neighbors=3, weights='uniform')`** on the training features and applies it to both splits.
- Persists the fitted preprocessor as a pickle (`preprocessing.pkl` and `final_model/preprocessor.pkl`).
- Saves transformed data as `.npy` files for fast loading.

**Artifact:** `DataTransformationArtifact(transformed_object_file_path, transformed_train_file_path, transformed_test_file_path)`

### 4. Model Training
Trains and evaluates **5 classifiers** with a small grid search each:

| Model | Hyper-parameters explored |
|---|---|
| **Random Forest** | `n_estimators ∈ {32, 128, 256}`, `max_features ∈ {sqrt, log2}` |
| **Decision Tree** | `criterion ∈ {gini, entropy, log_loss}`, `max_features ∈ {sqrt, log2}` |
| **Gradient Boosting** | `learning_rate ∈ {.1, .01}`, `subsample ∈ {0.7, 0.85}`, `n_estimators ∈ {32, 128}` |
| **Logistic Regression** | (default) |
| **AdaBoost** | `learning_rate ∈ {.1, .01}`, `n_estimators ∈ {32, 128}` |

For each model it computes F1, precision, recall on the test set, picks the best by test F1, then enforces two **guardrails** (constants in `networks/constants/training_pipeline/__init__.py`):
- `MODEL_ACCURACY_THRESHOLD = 0.6` — pipeline fails if the best test score is below this.
- `MODEL_ACCURACY_TRAIN_TEST_DIFFERENCE = 0.05` — pipeline fails if train/test gap exceeds this (overfit guard).

The best model is serialized to `final_model/model.pkl` and wrapped in a `NetworkModel(preprocessor, model)` for the API.

**Artifact:** `ModelTrainerArtifact(trained_model_file_path, train_data_score, test_data_score)`

---

## 🌐 API

`app.py` exposes two endpoints, served by **Uvicorn** at `http://127.0.0.1:8000`.

### `GET /`
Redirects to `/docs` (Swagger UI).

### `GET /train`
Runs the full training pipeline (ingest → validate → transform → train). Returns `"Training is successfull"`.

### `POST /predict`
Multipart upload of a CSV file (`file=...`). Expected columns = the 30 training features (no `Result` required).

The endpoint:
1. Reads the CSV with `pandas.read_csv` (auto-drops a stray `Unnamed: 0` index column).
2. Loads the saved preprocessor & model.
3. Validates that every expected feature is present; otherwise returns a clear error listing the missing columns.
4. Reorders columns to match the preprocessor's training order and runs the prediction.
5. Adds a `predicted column` to the DataFrame, saves it to `predicted_data/output.csv`, and renders the results in `templates/table.html`.

`predict.csv` at the repo root is a working sample input.

---

## 🔧 Configuration

All tunable constants live in **`networks/constants/training_pipeline/__init__.py`**:

| Constant | Default | Purpose |
|---|---|---|
| `TARGET_COLUMN` | `"Result"` | Label column |
| `DATA_INGESTION_DATABASE_NAME` | `"Manan"` | MongoDB DB |
| `DATA_INGESTION_COLLECTION_NAME` | `"networ_security"` | MongoDB collection |
| `DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO` | `0.2` | Test fraction |
| `DATA_TRANSFORMATION_IMPUTER_PARAMS` | `n_neighbors=3, weights='uniform'` | KNN imputer config |
| `MODEL_ACCURACY_THRESHOLD` | `0.6` | Minimum acceptable test F1 |
| `MODEL_ACCURACY_TRAIN_TEST_DIFFERENCE` | `0.05` | Max train/test gap |

Secrets are read from a `.env` file at the project root:

```env
MONGO_DB_URI=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net
```

---

## 🚀 Setup & Run

```bash
# 1. Create venv & install deps
python -m venv network
source network/bin/activate          # Windows: network\Scripts\activate
pip install -r requirements.txt
pip install -e .

# 2. Add your MongoDB URI to .env
echo "MONGO_DB_URI=..." > .env

# 3. (One-time) push phisingData.csv → MongoDB
python push_data.py

# 4. Start the API (auto-reloads on file changes)
uvicorn app:app --reload
# → http://127.0.0.1:8000/docs
```

Or with Docker:

```bash
docker build -t network-security .
docker run -p 8000:8000 --env-file .env network-security
```

---

## 📌 Usage

**Train** (open the Swagger UI → `GET /train` → *Execute*):
```bash
curl http://127.0.0.1:8000/train
```

**Predict** with a CSV:
```bash
curl -X POST http://127.0.0.1:8000/predict \
     -F "file=@predict.csv"
```
The response is an HTML table with the input features and the new `predicted column`. A copy is also written to `predicted_data/output.csv`.

---

## 📦 Artifacts & Outputs

After a training run you'll see something like:

```
Artifacts/07_25_2026_14_30_00/
├── data_ingestion/
│   ├── feature_store/phisingData.csv
│   └── ingested/{train.csv, test.csv}
├── datavalidation/
│   ├── validated/{train.csv, test.csv}
│   ├── invalid/{train.csv, test.csv}
│   └── driftreport/report.yaml
├── data_transformation/
│   ├── transformed/{train.npy, test.npy}
│   └── transformed_object/preprocessing.pkl
└── model_trainer/trained_model/model.pkl
```

The two pickles that the API needs are mirrored to **`final_model/`** for convenience:
- `final_model/preprocessor.pkl`
- `final_model/model.pkl`

---

## 🪲 Custom Exception

`NetworkSecurityException` (in `networks/exception/exception.py`) captures the originating `Exception`, the **filename** and the **line number** from `sys.exc_info()`, so every error log has a precise location.

---

## 📜 License & Credits

- Dataset: UCI Machine Learning Repository — *Phishing Websites*.
- Built as a hands-on MLOps project: modular pipeline, schema-driven validation, model guardrails, containerized inference.
