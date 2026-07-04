# Formative 1: Time Series Data Pipeline — Power Consumption of Tétouan City, Morocco

**Team:** Elvin Cyubahiro, Samuel Rurangamirwa, Heroine Mutumwinka, Singizwa Homere

**Course:** Machine Learning Pipeline

**Submission Date:** 5th July 2026


## Dataset

This project uses a **time series dataset of power consumption for the city of Tétouan, Morocco**. The data contains **52,416 observations** recorded at **10-minute intervals throughout 2017** across three distribution zones:

- **Quads**
- **Smir**
- **Boussafou**

The dataset also includes weather variables and solar diffuse flow.

Source: [Kaggle / UCI Machine Learning Repository — Power Consumption of Tétouan City](https://www.kaggle.com/datasets/fedesoriano/tetouan-city-power-consumption)

<!-- Provide source link once confirmed -->
## Task 1: EDA & Preprocessing (Singizwa)
(Add README documenting Task 1 EDA methodology and dataset source)

This notebook (`SINGIZWA_Homere_Group_1_Formative_1_pipeline.ipynb`) performs
exploratory data analysis on the Tétouan City power consumption dataset:
- Time range, frequency, and missing value analysis
- Statistical distributions and outlier interpretation
- 5 analytical questions including lag features and moving averages
---

## Repository Structure

```
time-series-pipeline/
├── README.md
├── .gitignore
├── Group1_Formative_1_pipeline_notebook.ipynb  ← combined final notebook
│
├── notebooks/
│   ├── 01_eda_preprocessing_homere.ipynb
│   ├── 02_modeling_elvin.ipynb
│   ├── 03_databases_heroine.ipynb
│   └── 04_api_and_pipeline_samuel.ipynb
│
├── src/
│   ├── app.py                          ← Flask API
│   └── predict.py                      ← forecast script
│
├── models/
│   ├── best_model.pkl
│   └── feature_cols.pkl
│
└── docs/
    └── erd.png                         ← database ER diagram
```

---

## How to Reproduce

### Prerequisites

- Python 3.9+
- Jupyter Notebook or JupyterLab
- Required libraries: `pandas`, `numpy`, `matplotlib`, `seaborn`, `scikit-learn`, `xgboost`, `flask`, `mysql-connector-python`, `pymongo`, `joblib`

### Setup

1. Clone this repository:
   ```bash
   git clone <repo-url>
   cd time-series-pipeline
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install pandas numpy matplotlib seaborn scikit-learn xgboost flask mysql-connector-python pymongo joblib
   ```

4. Launch Jupyter and open the desired notebook:
   ```bash
   jupyter notebook notebooks/
   ```

> **Note:** The databases notebook (`03_databases_Heroine (2).ipynb`) requires `MYSQL_*` and `MONGO_URI` secrets to be set (e.g., via Colab secrets or environment variables).

---

## Per-Member Contributions

| Member | Contribution |
|---|---|
| **Elvin Cyubahiro** | Feature engineering (cyclical encodings, multi-horizon lags, leakage-corrected rolling statistics), TimeSeriesSplit cross-validation, XGBoost & Random Forest hyperparameter tuning, model serialization |
| **Samuel Rurangamirwa** | Flask REST API (CRUD & time-series endpoints), pipeline orchestration, prediction script |
| **Heroine Mutumwinka** | MySQL schema design, data seeding, SQL queries; MongoDB collection design, document insertion, aggregation queries; database ER diagram |
| **Singizwa Homere** | Exploratory Data Analysis (EDA), data preprocessing and cleaning, feature exploration, dataset visualization |

---

## Pipeline Overview

This project implements an end-to-end time series data pipeline:

1. **EDA & Preprocessing** (Singizwa) — Data cleaning, exploratory analysis, visualisation
2. **Modeling** (Elvin) — Feature engineering, cross-validation, hyperparameter tuning (XGBoost, Random Forest)
3. **Databases** (Heroine) — MySQL relational storage & MongoDB document storage with aggregation queries
4. **API & Pipeline** (Samuel) — Flask REST API serving predictions and pipeline orchestration

---

## License

This project is submitted as part of the Formative 1 assessment for the Machine Learning Pipeline course — Group 1.

