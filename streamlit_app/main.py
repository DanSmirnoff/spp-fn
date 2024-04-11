from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from news import get_news
from stocks import get_stocks_info
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt


dateFrom = (datetime.now() - timedelta(1))
dateFrom = dateFrom.strftime("%Y-%m-%d")
dateTo = datetime.now().strftime("%Y-%m-%d")

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

news_content = get_news(news_param_dict, 10)

st.sidebar.title("Последние новости")
for idx, row in news_content.iterrows():
    title = row['title']
    url = row['url']
    st.sidebar.markdown(f"- <a href='{url}' style='color: black; text-decoration: none;'>{title}</a>", unsafe_allow_html=True)

dateFrom = datetime.now().date() - timedelta(days=180)
dateTo = datetime.now().date()
daily_info = get_stocks_info('IMOEX', str(dateFrom), str(dateTo), 'D')
daily_info['date'] = daily_info['begin'].dt.date

sns.set(style='whitegrid')
fig, ax = plt.subplots(figsize=(18, 10))
sns_plot = sns.lineplot(data=daily_info, x='date', y='open', color='green', label='IMOEX')
sns_plot = sns.lineplot(data=daily_info, x='date', y='close', color='red', label='Predictions')
matplotlib_fig_1d = sns_plot.get_figure()

st.title('IMOEX')
st.pyplot(matplotlib_fig_1d)

current_date = datetime.now().date()
predicted_opening = 6666.6666
st.write(f'<span style="font-weight:bold;">Предсказанное открытие {current_date}: </span>'
         f' <span style="color:green; font-weight:bold;">{predicted_opening}</span>',
         unsafe_allow_html=True)

