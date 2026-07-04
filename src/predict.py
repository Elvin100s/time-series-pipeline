"""
End-to-end prediction pipeline.

Fetches records from the Flask API, applies the same feature engineering
used at training time, loads the trained model, and produces forecasts.

Prerequisites:
    app.py running at http://127.0.0.1:5000
    best_model.pkl and feature_cols.pkl in the working directory

Run:  python predict.py
"""

import requests
import pandas as pd
import numpy as np
import joblib

API = "http://127.0.0.1:5000"


def fetch(start, end):
    print("[1/4] Fetching from API...")
    r = requests.get(
        API + "/api/sql/readings/range",
        params={"start": start, "end": end},
    )
    if r.status_code != 200:
        raise Exception("API error " + str(r.status_code))
    data = r.json()
    print("      {} records fetched".format(data["count"]))
    return data["data"]


def preprocess(records):
    print("[2/4] Preprocessing...")

    rows = []
    for rec in records:
        rows.append({
            "DateTime":            rec["timestamp"],
            "Temperature":         rec["temperature"],
            "Humidity":            rec["humidity"],
            "WindSpeed":           rec["wind_speed"],
            "GeneralDiffuseFlows": rec.get("general_diffuse", 0),
            "DiffuseFlows":        rec.get("diffuse_flows", 0),
            "Zone1":               rec["zones"].get("zone1", 0),
            "Zone2":               rec["zones"].get("zone2", 0),
            "Zone3":               rec["zones"].get("zone3", 0),
        })

    df = pd.DataFrame(rows)
    df["DateTime"] = pd.to_datetime(df["DateTime"])
    df = df.set_index("DateTime").sort_index()
    df["TotalConsumption"] = df["Zone1"] + df["Zone2"] + df["Zone3"]

    f = df.copy()

    f["Hour_sin"]  = np.sin(2 * np.pi * f.index.hour / 24)
    f["Hour_cos"]  = np.cos(2 * np.pi * f.index.hour / 24)
    f["Month_sin"] = np.sin(2 * np.pi * f.index.month / 12)
    f["Month_cos"] = np.cos(2 * np.pi * f.index.month / 12)
    f["DoW_sin"]   = np.sin(2 * np.pi * f.index.dayofweek / 7)
    f["DoW_cos"]   = np.cos(2 * np.pi * f.index.dayofweek / 7)
    f["IsWeekend"] = (f.index.dayofweek >= 5).astype(int)

    for lag in [1, 2, 3, 6, 12, 24, 48, 168]:
        f["Lag_{}h".format(lag)] = f["TotalConsumption"].shift(lag)

    # shift(1) before rolling prevents the current row's target leaking into its own feature
    for w in [6, 12, 24, 48, 168]:
        f["MA_{}h".format(w)]  = f["TotalConsumption"].shift(1).rolling(w).mean()
        f["Std_{}h".format(w)] = f["TotalConsumption"].shift(1).rolling(w).std()

    f["Temp_sq"]    = f["Temperature"] ** 2
    f["Temp_x_Hum"] = f["Temperature"] * f["Humidity"]

    f = f.dropna()
    print("      {} rows after feature engineering".format(len(f)))
    return f


def load_model():
    print("[3/4] Loading model...")
    model = joblib.load("best_model.pkl")
    cols  = joblib.load("feature_cols.pkl")
    print("      {} ({} features)".format(type(model).__name__, len(cols)))
    return model, cols


def predict(feat_df, model, cols):
    print("[4/4] Predicting...")
    preds = model.predict(feat_df[cols])

    res = pd.DataFrame({
        "timestamp": feat_df.index,
        "actual":    feat_df["TotalConsumption"].values,
        "predicted": preds,
        "error":     feat_df["TotalConsumption"].values - preds,
    })

    rmse = np.sqrt(np.mean(res["error"] ** 2))
    mae  = np.mean(np.abs(res["error"]))

    print()
    print("=" * 55)
    print("PREDICTION RESULTS")
    print("=" * 55)
    print("Records: {}".format(len(res)))
    print("RMSE:    {:.2f} kWh".format(rmse))
    print("MAE:     {:.2f} kWh".format(mae))
    print()
    print(res.head(10).to_string(index=False))
    return res


if __name__ == "__main__":
    recs = fetch("2017-12-01 00:00:00", "2017-12-15 23:00:00")
    feat = preprocess(recs)
    model, cols = load_model()
    results = predict(feat, model, cols)
    print()
    print("Pipeline complete.")
