# Formative 1: Time Series Data Pipeline — Power Consumption of Tétouan City

**Team:** Elvin Cyubahiro, Samuel Rurangamirwa, Heroine Mutumwinka, Singizwa Homere

**Course:** <!-- TODO: Add course name -->

**Submission Date:** <!-- TODO: Add submission date -->

---

## Dataset

<!-- TODO: Add dataset description and link -->

This project uses a time series dataset of power consumption for the city of Tétouan, Morocco. The data includes measurements from three distribution zones and various environmental factors.

<!-- Provide source link once confirmed -->

---

## Repository Structure

```
time-series-pipeline/
├── README.md
├── .gitignore
├── Group1_Formative_1_pipeline_notebook.ipynb  ← combined final notebook (Elvin pushes)
│
├── notebooks/
│   ├── 01_eda_preprocessing_homere.ipynb    ← Homere pushes
│   ├── 02_modeling_elvin.ipynb              ← Elvin pushes
│   ├── 03_databases_heroine.ipynb           ← Heroine pushes
│   └── 04_api_and_pipeline_samuel.ipynb     ← Samuel pushes
│
├── src/
│   ├── app.py                          ← Samuel pushes (Flask API)
│   └── predict.py                      ← Samuel pushes (forecast script)
│
├── models/
│   ├── best_model.pkl                  ← Elvin pushes
│   └── feature_cols.pkl                ← Elvin pushes
│
└── docs/
    └── erd.png                         ← Heroine pushes (dbdiagram export)
```

---

## How to Reproduce

### Prerequisites

<!-- TODO: List Python version and required libraries -->

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
   pip install -r requirements.txt
   ```

4. Launch Jupyter:
   ```bash
   jupyter notebook notebooks/
   ```

<!-- TODO: Add any additional reproduction steps -->

---

## Per-Member Contributions

| Member | Contribution |
|---|---|
| Elvin Cyubahiro | <!-- TODO --> |
| Samuel Rurangamirwa | <!-- TODO --> |
| Heroine Mutumwinka | <!-- TODO --> |
| Singizwa Homere | <!-- TODO --> |

---

<!-- License info if applicable -->
