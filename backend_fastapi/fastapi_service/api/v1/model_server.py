import logging

import pandas as pd
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

import os

logger = logging.getLogger()
router = APIRouter()


class NewsRequest(BaseModel):
    num: int


class PredictionRequest(BaseModel):
    dateFrom: str
    dateTo: str


@router.post("/predictions")
async def get_predictions(pred_request: PredictionRequest):
    dateFrom = pred_request.dateFrom
    dateTo = pred_request.dateTo

    df = pd.read_csv('data/model_pred.csv')
    df['date'] = pd.to_datetime(df['date'])

    dateFrom = datetime.strptime(dateFrom, '%Y-%m-%d')
    dateTo = datetime.strptime(dateTo, '%Y-%m-%d')

    df = df.loc[(df['date'] >= dateFrom) & (df['date'] <= dateTo)]

    dates = list(df['date'].dt.date)
    preds = list(df['pred'])

    return {dates[i]: preds[i] for i in range(len(dates))}


@router.post("/news")
async def predict_items(news_request: NewsRequest):
    num = news_request.num

    df = pd.read_csv('data/lenta_news.csv')
    df = df.loc[len(df) - num:]
    return {'title': df['title'], 'date': df['date'], 'url': df['url']}


