import pandas as pd
from moexalgo import Ticker


def get_stocks_info(ticker: str, date_from: str, date_to: str, period: str) -> pd.DataFrame:
    ticker = Ticker(ticker)
    info = pd.DataFrame(ticker.candles(date=date_from, till_date=date_to, period=period))
    return info
