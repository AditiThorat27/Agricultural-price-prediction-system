import logging
from pathlib import Path
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Market Recommender Model Service")

SERVICE_DIR = Path(__file__).resolve().parent


class PredictionRequest(BaseModel):
    commodity: str
    lat: float
    lon: float


def _resolve_model_dir() -> Path:
    """Return the models directory, supporting both local and Docker layouts."""
    # Docker: models mounted as a sibling dir inside /app
    docker_path = SERVICE_DIR / "models"
    if docker_path.is_dir():
        return docker_path
    # Local development: models sit next to model_service/ in the repo root
    return SERVICE_DIR.parent / "models"


def load_models():
    """Load all commodity models at startup."""
    base_dir = _resolve_model_dir()
    model_names = ["onion", "potato", "tomato"]

    models = {}
    for name in model_names:
        path = base_dir / name / f"{name}_model.pkl"
        try:
            models[name] = joblib.load(path)
            logger.info("Loaded model for %s from %s", name, path)
        except Exception as exc:
            raise RuntimeError(f"Failed to load model for {name} from {path}") from exc

    return models


commodity_models = load_models()


def _get_feature_names(model) -> list[str]:
    if hasattr(model, "feature_name"):
        return list(model.feature_name())
    return list(model.feature_name_)


def _get_pandas_categories(model) -> list[list[str]]:
    categories = getattr(model, "pandas_categorical", None)
    if categories:
        return categories

    booster = getattr(model, "booster_", None)
    return getattr(booster, "pandas_categorical", []) or []


def _build_placeholder_features(commodity: str, model, lat: float, lon: float) -> pd.DataFrame:
    feature_names = _get_feature_names(model)
    features = pd.DataFrame(np.zeros((1, len(feature_names))), columns=feature_names)

    today = datetime.utcnow()
    day_of_year = today.timetuple().tm_yday
    base_price = {
        "onion": 25.0,
        "potato": 20.0,
        "tomato": 35.0,
    }[commodity]

    placeholder_values = {
        "min_price": base_price - 5.0,
        "Min_Price": base_price - 5.0,
        "max_price": base_price + 5.0,
        "Max_Price": base_price + 5.0,
        "modal_price": base_price,
        "price_spread": 10.0,
        "is_real_trade": 0,
        "day_of_week": today.weekday(),
        "month": today.month,
        "day_of_year": day_of_year,
        "is_weekend": int(today.weekday() >= 5),
        "is_holiday": 0,
        "price_lag_1": base_price,
        "price_lag_2": base_price,
        "price_lag_3": base_price,
        "price_lag_7": base_price,
        "price_lag_14": base_price,
        "price_roll_mean_3": base_price,
        "price_roll_mean_7": base_price,
        "price_roll_mean_30": base_price,
        "price_roll_std_7": 0.0,
        "price_roll_std_30": 0.0,
        "price_expanding_mean": base_price,
        "price_expanding_max": base_price,
        "sin_365": np.sin(2 * np.pi * day_of_year / 365.0),
        "cos_365": np.cos(2 * np.pi * day_of_year / 365.0),
        "sin_365_1": np.sin(2 * np.pi * day_of_year / 365.0),
        "cos_365_1": np.cos(2 * np.pi * day_of_year / 365.0),
        "sin_365_2": np.sin(4 * np.pi * day_of_year / 365.0),
        "cos_365_2": np.cos(4 * np.pi * day_of_year / 365.0),
        "temp_mean_lag1": 28.0,
        "temperature": 28.0,
        "temp_7d_avg": 28.0,
        "rainfall_lag1": 0.0,
        "rainfall_7d_sum": 0.0,
        "rainfall_30d_sum": 0.0,
    }

    for column, value in placeholder_values.items():
        if column in features.columns:
            features.at[0, column] = value

    pandas_categories = _get_pandas_categories(model)
    categorical_columns = [
        column for column in feature_names if column in {"mandi_name", "district", "state", "variety"}
    ]
    categorical_defaults = {
        "mandi_name": "Pune",
        "district": "Pune",
        "state": "Maharashtra",
        "variety": "Local",
    }

    for index, column in enumerate(categorical_columns):
        categories = pandas_categories[index] if index < len(pandas_categories) else []
        default_value = categorical_defaults.get(column)
        if categories and default_value not in categories:
            default_value = categories[0]
        if categories:
            features[column] = pd.Categorical([default_value], categories=categories)

    return features


def predict_price(commodity: str, lat: float, lon: float) -> dict:
    """Run inference for a commodity and return the prediction result."""
    model = commodity_models.get(commodity)
    if model is None:
        raise ValueError(f"Model for commodity '{commodity}' not found.")

    features = _build_placeholder_features(commodity, model, lat, lon)
    price = model.predict(features)[0]

    return {
        "best_market": "Pune APMC",
        "predicted_price": float(price),
    }


@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        return predict_price(request.commodity, request.lat, request.lon)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Model inference failed for commodity %s", request.commodity)
        raise HTTPException(status_code=500, detail="Internal model error") from exc


@app.get("/models")
def list_models():
    return {"available_models": sorted(commodity_models.keys())}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "models_loaded": sorted(commodity_models.keys()),
    }
