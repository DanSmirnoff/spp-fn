import pandas as pd
import requests


def get_news(num: int) -> pd.DataFrame:
    url = "http://127.0.0.1:8000/api/v1/news"
    response = requests.post(url, json={"num": num})
    return pd.DataFrame(response.json()).loc[::-1]
