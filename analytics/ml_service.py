import numpy as np
from typing import List, Dict, Optional
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import warnings

warnings.filterwarnings("ignore")


def encode_categorical(data: List[Dict], field: str) -> tuple[List, LabelEncoder]:
    le = LabelEncoder()
    values = [row.get(field, "") or "" for row in data]
    encoded = le.fit_transform(values)
    return encoded, le


def prepare_features(data: List[Dict]) -> tuple:
    if len(data) < 2:
        return None, None, None, None

    years = np.array([row["year"] for row in data]).reshape(-1, 1)
    allotments = np.array([row["allotment_count"] for row in data])
    cutoffs = np.array([row["avg_cutoff"] for row in data])

    region_encoded, _ = encode_categorical(data, "region")
    college_type_encoded, _ = encode_categorical(data, "college_type")

    X = np.column_stack([years.flatten(), region_encoded, college_type_encoded, cutoffs])
    y_demand = allotments
    y_cutoff = cutoffs

    return X, y_demand, y_cutoff, years


def predict_demand(data: List[Dict], branch_code: str, branch_name: str) -> Dict:
    if len(data) < 2:
        last = data[-1] if data else {}
        return {
            "branch_code": branch_code,
            "branch_name": branch_name,
            "predicted_year": (last.get("year", 2024) + 1),
            "predicted_demand": float(last.get("allotment_count", 0)),
            "predicted_cutoff": float(last.get("avg_cutoff", 0.0)),
            "popularity_score": 50.0,
            "growth_prediction": 0.0,
            "model_used": "baseline",
            "confidence": 0.0,
        }

    X, y_demand, y_cutoff, years = prepare_features(data)

    next_year = int(years.max()) + 1
    last_region = encode_categorical(data, "region")[0][-1]
    last_ct = encode_categorical(data, "college_type")[0][-1]
    last_cutoff = float(data[-1]["avg_cutoff"])

    X_next = np.array([[next_year, last_region, last_ct, last_cutoff]])

    model_used = "linear_regression"
    confidence = 0.0

    if len(data) >= 5:
        rf = RandomForestRegressor(n_estimators=50, random_state=42)
        rf.fit(X, y_demand)
        pred_demand = float(rf.predict(X_next)[0])

        rf_cutoff = RandomForestRegressor(n_estimators=50, random_state=42)
        rf_cutoff.fit(X, y_cutoff)
        pred_cutoff = float(rf_cutoff.predict(X_next)[0])

        if len(data) > 5:
            split = max(2, int(len(data) * 0.8))
            rf_eval = RandomForestRegressor(n_estimators=50, random_state=42)
            rf_eval.fit(X[:split], y_demand[:split])
            score = r2_score(y_demand[split:], rf_eval.predict(X[split:]))
            confidence = max(0.0, min(1.0, float(score))) * 100
        else:
            confidence = 60.0

        model_used = "random_forest"
    else:
        lr = LinearRegression()
        lr.fit(X, y_demand)
        pred_demand = float(lr.predict(X_next)[0])

        lr_cutoff = LinearRegression()
        lr_cutoff.fit(X, y_cutoff)
        pred_cutoff = float(lr_cutoff.predict(X_next)[0])

        confidence = 40.0
        model_used = "linear_regression"

    pred_demand = max(0.0, pred_demand)
    pred_cutoff = max(0.0, min(200.0, pred_cutoff))

    last_demand = float(data[-1]["allotment_count"])
    growth_prediction = ((pred_demand - last_demand) / max(last_demand, 1)) * 100

    max_demand = max(row["allotment_count"] for row in data)
    popularity_score = (pred_demand / max(max_demand, 1)) * 100

    return {
        "branch_code": branch_code,
        "branch_name": branch_name,
        "predicted_year": next_year,
        "predicted_demand": round(pred_demand, 2),
        "predicted_cutoff": round(pred_cutoff, 2),
        "popularity_score": round(popularity_score, 2),
        "growth_prediction": round(growth_prediction, 2),
        "model_used": model_used,
        "confidence": round(confidence, 2),
    }
