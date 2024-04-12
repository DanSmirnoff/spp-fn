import pandas as pd
from moexalgo import Ticker
from datetime import datetime, timedelta


def get_stocks_info(ticker: str, dateFrom: datetime.date, dateTo: datetime.date, period: str):
    ticker = Ticker(ticker)
    df_per = pd.DataFrame(ticker.candles(date=dateFrom, till_date=dateTo, period=period))
    df_per['date'] = df_per['begin'].dt.date

    return df_per
