import logging

import pandas as pd
from datetime import datetime
from fastapi import APIRouter

logger = logging.getLogger()
router = APIRouter()


@router.post("/predict_item")
async def get_predictions(dateFrom: str, dateTo: str):
    df = pd.read_csv('backend_fastapi/data/model_pred.csv')
    dateFrom = datetime.strptime(dateFrom, '%Y-%m-%d')
    dateTo = datetime.strptime(dateTo, '%Y-%m-%d')
    df = df.loc[(df['date'].dt.date >= dateFrom) & (df['date'].dt.date <= dateTo)]
    return {'date': df['date'], 'prediction': df['pred']}


@router.post("/news")
async def predict_items(num: int):
    df = pd.read_csv('backend_fastapi/data/lenta_news.csv')
    df = df.loc[len(df) - num:]
    return {'title': df['title'], 'date': df['date'], 'url': df['url']}
