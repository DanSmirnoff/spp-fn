import os
import re
import pandas as pd
import moexalgo
from .parsers import LentaRuParser
from datetime import datetime, timedelta


def parse_lenta(dateFrom: str, dateTo: str) -> bool:
    """
    parse lenta.ru and update lenta_news.csv
    """

    def extract_date_from_url(url: str):
        pattern = r'/(\d{4})/(\d{2})/(\d{2})/'

        match = re.search(pattern, url)

        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            return datetime(year, month, day).date()
        return None

    news_param_dict = {
        'query': '',
        'from': '0',
        'size': '1000',
        'dateFrom': dateFrom,
        'dateTo': dateTo,
        'sort': '3',
        'title_only': '0',
        'type': '0',
        'bloc': '4',
        'domain': '1'
    }

    parser = LentaRuParser()
    df_new = None
    for _ in range(5):
        try:
            df_new = parser.get_articles(news_param_dict, save_excel=False)
            break
        except Exception:
            continue

    if df_new is None:
        return False

    df_new['date'] = df_new['url'].apply(extract_date_from_url)
    df_new = df_new[['url', 'title', 'text', 'date']]

    df_old = pd.read_csv('data/lenta_news.csv')

    df = pd.concat([df_old, df_new], ignore_index=True)
    df = df.drop_duplicates(subset='url', keep='first')

    df.to_csv('data/lenta_news.csv', index=False)

    return True


def parse_imoex(dateFrom: str, dateTo: str) -> bool:
    """
    parse imoex via moexalgo and update imoex10m.csv
    """
    imoex = moexalgo.Ticker('IMOEX')
    df = pd.DataFrame()
    date = datetime.strptime(dateFrom, '%Y-%m-%d')
    dateTo = datetime.strptime(dateTo, '%Y-%m-%d')

    while date <= dateTo:
        date_end = min(date + timedelta(days=30 * 5), dateTo)
        df_per = pd.DataFrame(imoex.candles(date=date.date(), till_date=date_end.date(), period='10m'))
        df = pd.concat([df, df_per], ignore_index=True)
        date = date_end + timedelta(days=1)

    df_old = pd.read_csv('data/imoex10m.csv')
    df = pd.concat([df_old, df], ignore_index=True)
    df = df.drop_duplicates(subset='begin', keep='first')

    df.to_csv('data/imoex10m.csv', index=False)

    return True
