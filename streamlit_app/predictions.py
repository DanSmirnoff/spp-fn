import pandas as pd
import requests
from datetime import datetime


def get_predictions(dateFrom: datetime.date, dateTo: datetime.date):
    url = "http://127.0.0.1:8000/api/v1/predictions"
    response = requests.post(url, json={"dateFrom": str(dateFrom), "dateTo": str(dateTo)})
    d = dict(response.json())
    return pd.DataFrame({'date': d.keys(), 'prediction': d.values()})
