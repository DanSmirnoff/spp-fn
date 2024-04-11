import logging

import pandas as pd
from catboost import CatBoostRegressor
from backend_fastapi.fastapi_service.services import DataLoader

logger = logging.getLogger(__name__)


def infer_model(df: pd.DataFrame) -> bool:
    """
    receives dataframe with dates
    makes predictions and updates model_pred.csv
    :param df:
    :return:
    """
    model = CatBoostRegressor()
    model.load_model('backend_fastapi/data/catboost_model')

    dates = df['date']
    df = df.drop(columns=['date'])
    y_pred = model.predict(df)

    df_pred = pd.DataFrame({'date': dates, 'y_pred': y_pred})

    df_old = pd.read_csv('backend_fastapi/data/model_pred.csv')
    df = pd.concat([df_old, df_pred])
    df = df.drop_duplicates(subset=['date'])

    df.to_csv('backend_fastapi/data/model_pred.csv', index=False)

    return True

