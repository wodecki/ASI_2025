"""
FastAPI backend for Iowa alcohol sales prediction.

Educational Purpose:
- Demonstrates model-as-a-service pattern
- Shows efficient resource loading (startup, not per-request)
- Implements RESTful API design with proper error handling
"""

import os
import logging
from fastapi import FastAPI, HTTPException
import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

# Configure logging for observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Iowa Sales Predictor",
    description="Time series forecasting API for Iowa alcohol sales",
    version="1.0.0"
)

# Global variables for model and preprocessed data
predictor = None
train_data = None


@app.on_event("startup")
async def startup_event():
    """
    Load model and data at startup (not per-request).

    Educational Note:
    - This pattern improves performance by loading resources once
    - Models and data persist in memory across requests
    - Reduces latency and avoids redundant I/O operations
    """
    global predictor, train_data

    # Validate model directory exists
    model_path = "autogluon-iowa-daily"
    if not os.path.exists(model_path):
        logger.error("=" * 60)
        logger.error("ERROR: Model not found!")
        logger.error("=" * 60)
        logger.error(f"Expected location: {model_path}")
        logger.error("")
        logger.error("You need to train the model first:")
        logger.error("  uv run python '1. train.py'")
        logger.error("")
        logger.error("This will create the autogluon-iowa-daily/ directory.")
        logger.error("=" * 60)
        raise RuntimeError(f"Model directory not found: {model_path}")

    # Validate data file exists
    data_path = "data/iowa_sales.csv"
    if not os.path.exists(data_path):
        logger.error("=" * 60)
        logger.error("ERROR: Data file not found!")
        logger.error("=" * 60)
        logger.error(f"Expected location: {data_path}")
        logger.error("")
        logger.error("Make sure data/iowa_sales.csv exists in the backend directory.")
        logger.error("=" * 60)
        raise RuntimeError(f"Data file not found: {data_path}")

    logger.info("Loading AutoGluon predictor...")
    predictor = TimeSeriesPredictor.load(model_path)
    logger.info(f"✓ Predictor loaded successfully")

    logger.info("Loading and preprocessing training data...")
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    train_data = TimeSeriesDataFrame.from_data_frame(
        df,
        id_column="item_name",
        timestamp_column="date"
    )
    logger.info(f"✓ Data loaded: {len(df)} records, {df['item_name'].nunique()} unique items")
    logger.info("=" * 60)
    logger.info("Backend ready! API available at http://localhost:8003")
    logger.info("=" * 60)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "message": "Iowa Sales Predictor API",
        "endpoints": {
            "predict": "/predict/{item_name}",
            "items": "/items"
        }
    }


@app.get("/items")
async def get_items():
    """
    Return list of available items for prediction.

    Educational Note:
    - Provides API discoverability
    - Helps frontend build dynamic UI components
    """
    if train_data is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    items = train_data.index.get_level_values('item_id').unique().tolist()
    return {"items": items}


@app.get("/predict/{item_name}")
async def predict(item_name: str):
    """
    Generate 7-day sales forecast for specified item.

    Educational Note:
    - Uses path parameter for RESTful resource access
    - Returns structured JSON response with predictions
    - Implements proper HTTP error codes (404, 503)

    Args:
        item_name: Alcohol product name (e.g., "BLACK VELVET")

    Returns:
        JSON with predictions list containing timestamp and mean forecast
    """
    if predictor is None or train_data is None:
        raise HTTPException(
            status_code=503,
            detail="Service initializing. Please try again in a few seconds."
        )

    logger.info(f"Generating predictions for: {item_name}")

    # Generate predictions for all items (AutoGluon requirement)
    predictions = predictor.predict(train_data)

    # Extract predictions for requested item
    if item_name not in predictions.index.get_level_values(0):
        available_items = predictions.index.get_level_values(0).unique().tolist()
        raise HTTPException(
            status_code=404,
            detail=f"Item '{item_name}' not found. Available items: {available_items}"
        )

    item_predictions = predictions.loc[item_name]

    # Format predictions as list of dicts for JSON response
    formatted_predictions = [
        {
            'timestamp': str(index),
            'date': index.strftime('%Y-%m-%d'),
            'mean': float(row['mean'])  # Ensure JSON serializable
        }
        for index, row in item_predictions.iterrows()
    ]

    logger.info(f"Returning {len(formatted_predictions)} predictions for {item_name}")

    return {
        'item': item_name,
        'predictions': formatted_predictions,
        'forecast_horizon': len(formatted_predictions)
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8003"))
    uvicorn.run(app, host="0.0.0.0", port=port)
