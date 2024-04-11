from typing import Dict

import pandas as pd
from parsers import LentaRuParser


def get_news(params: Dict[str, str], num: int) -> pd.DataFrame:
    parser = LentaRuParser()
    news = parser.get_articles(params, save_excel=False)
    news = news.iloc[::-1]
    return news[:min(num, len(news))]

