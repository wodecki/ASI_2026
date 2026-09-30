import os
from fastapi import FastAPI, HTTPException
import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

app = FastAPI()

predictor = None
train_data = None


@app.on_event("startup")
async def startup_event():
    global predictor, train_data

    predictor = TimeSeriesPredictor.load("autogluon-iowa-daily")

    df = pd.read_csv("data/iowa_sales.csv")
    df['date'] = pd.to_datetime(df['date'])
    train_data = TimeSeriesDataFrame.from_data_frame(
        df,
        id_column="item_name",
        timestamp_column="date"
    )


@app.get("/")
async def root():
    return {
        "status": "running",
        "message": "Iowa Sales Predictor API"
    }


@app.get("/items")
async def get_items():
    if train_data is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    items = train_data.index.get_level_values('item_id').unique().tolist()
    return {"items": items}


@app.get("/predict/{item_name}")
async def predict(item_name: str):
    if predictor is None or train_data is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    predictions = predictor.predict(train_data)

    if item_name not in predictions.index.get_level_values(0):
        raise HTTPException(status_code=404, detail=f"Item '{item_name}' not found")

    item_predictions = predictions.loc[item_name]

    formatted_predictions = [
        {
            'timestamp': str(index),
            'date': index.strftime('%Y-%m-%d'),
            'mean': float(row['mean'])
        }
        for index, row in item_predictions.iterrows()
    ]

    return {
        'item': item_name,
        'predictions': formatted_predictions
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8003"))
    uvicorn.run(app, host="0.0.0.0", port=port)
