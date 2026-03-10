from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random

app = FastAPI(title="Market Recommender Model Service")

class PredictionRequest(BaseModel):
    commodity: str
    lat: float
    lon: float

# Using mock prediction logic since models aren't provided yet
def mock_predict(commodity: str, lat: float, lon: float):
    markets = ["Pune APMC", "Khadki Cantonment", "Pimpri Chinchwad", "Moshi"]
    
    # Just generating some dummy predicted values
    base_prices = {
        "onion": 25.0,
        "potato": 20.0,
        "tomato": 35.0
    }
    
    if commodity not in base_prices:
        raise ValueError(f"Model for commodity '{commodity}' not found.")
        
    best_market = random.choice(markets)
    predicted_price = round(base_prices[commodity] + random.uniform(-5.0, 5.0), 2)
    
    return {
        "best_market": best_market,
        "predicted_price": predicted_price
    }

@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        result = mock_predict(request.commodity, request.lat, request.lon)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal model error")

@app.get("/health")
def health_check():
    return {"status": "ok"}
