from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from news import get_news
from stocks import get_stocks_info
from predictions import get_predictions
import seaborn as sns
import matplotlib.pyplot as plt

from threading import Timer


news_content = pd.DataFrame()


def update_news_content():
    global news_content
    news_content = get_news(10)

    st.sidebar.title("Последние новости")
    for idx, row in news_content.iterrows():
        title = row['title']
        url = row['url']
        st.sidebar.markdown(f"- <a href='{url}' style='color: black; text-decoration: none;'>{title}</a>",
                            unsafe_allow_html=True)

    Timer(2400, update_news_content).start()


@st.cache(ttl=2400)
def get_news_cached():
    return get_news(10)


def update_chart():
    global df

    # TODO change date
    dateTo = datetime.strptime('2024-04-02', '%Y-%m-%d').date()
    dateFrom = dateTo - timedelta(days=180)

    daily_info = get_stocks_info('IMOEX', dateFrom, dateTo, 'D')
    predictions = get_predictions(dateFrom, dateTo)

    df = pd.DataFrame({'date': daily_info['date'], 'open': daily_info['open'], 'prediction': predictions['prediction']})

    sns.set(style='whitegrid')
    fig, ax = plt.subplots(figsize=(18, 10))
    sns_plot = sns.lineplot(data=df, x='date', y='open', color='green', label='IMOEX')
    sns_plot = sns.lineplot(data=df, x='date', y='prediction', color='red', label='Predictions')
    plt.legend(loc='upper left', bbox_to_anchor=(0, 1))
    matplotlib_fig_1d = sns_plot.get_figure()

    st.title('IMOEX')
    st.pyplot(matplotlib_fig_1d)

    Timer(86400, update_chart).start()


def update_prediction():
    global df

    # TODO change date
    current_date = datetime.now().date() - timedelta(days=10)
    pred = get_predictions(current_date, current_date + timedelta(days=1))
    predicted_opening = round(pred['prediction'].iloc[-1], 2)
    if predicted_opening > df['open'].iloc[-1]:
        color = 'green'
    else:
        color = 'red'

    st.write(f'<span style="font-weight:bold;">Предсказанное открытие {pred['date'].iloc[-1]}: </span>'
             f' <span style="color:{color}; font-weight:bold;">{predicted_opening}</span>',
             unsafe_allow_html=True)

    Timer(2400, update_prediction).start()


update_news_content()
update_chart()
update_prediction()

