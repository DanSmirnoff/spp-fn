import os

import moexalgo
import pandas as pd
import numpy as np
import statsmodels.api as sm
import datetime
import holidays
import torch
import joblib
from sklearn.decomposition import PCA
from transformers import AutoTokenizer, AutoModel
from datetime import datetime, timedelta, date


TRANSFORMERS_OFFLINE=1
test_date = '2023-08-25'


def add_data(df1, df2):
    current_date = df2['date'].iloc[0]
    if current_date in df1['date'].values:
        df1.loc[df1['date'] == current_date, 'date'] = df2['date'].iloc[0]
    else:
        df1 = pd.concat([df1, df2], ignore_index=True)
    return df1


def update_bert_pca():
    """
    берет из lenta_news.csv донные за день
    прогоняет bert и pca и обновляет файл bert_pca.csv
    """
    tokenizer = AutoTokenizer.from_pretrained("Geotrend/distilbert-base-ru-cased", local_files_only=True)
    bert = AutoModel.from_pretrained("Geotrend/distilbert-base-ru-cased", local_files_only=True)
    pca = joblib.load('data/pca_model.pkl')

    df_nlp = pd.read_csv('data/lenta_news.csv')
    df_nlp = df_nlp[df_nlp['date'] == test_date] # str(datetime.now().date())
    df_nlp['date'] = pd.to_datetime(df_nlp['date']).dt.strftime('%Y-%m-%d')
    features = {'pub_date': [], 'features': []}
    for _, row in df_nlp.iterrows():
        text = row['text']
        try:
            tokens = tokenizer(text, return_tensors='pt', max_length=512, truncation=True)
        except Exception as ex:
            print(ex)
            continue
        with torch.no_grad():
            output = bert(**tokens)
        last_hidden_state = output.last_hidden_state.cpu().mean(dim=1).squeeze().numpy()
        features['features'].append(last_hidden_state)
        features['pub_date'].append(row['date'])

    try:
        pca_output = np.mean(pca.transform(features['features']), axis=0)
        pca_df = pd.DataFrame(pca_output).T # bruh
        pca_df.insert(loc=0, column='date', value=df_nlp['date'].unique())
    except Exception as ex:
        print(ex)
        return False

    for i in range(50):
        pca_df = pca_df.rename(columns={i: f'embed_{i}'})

    old_df = pd.read_csv('data/bert_pca.csv')
    pca_df = add_data(old_df, pca_df)
    pca_df.to_csv(os.path.abspath(os.path.join(os.getcwd(), '..', '..', 'data', 'bert_pca.csv')), index=False)
    pca_df.to_csv('data/bert_pca.csv', index=False)

    return True


def compute_imoex_stats():
    """
    берет данные по imoex за сегодня и считает статистики
    обновляет файл stats_imoex_open.csv
    """
    df = pd.read_csv('data/imoex10m.csv')
    df = df.rename(columns={'begin': 'date'})
    df['date'] = pd.to_datetime(df['date'])
    curr_date = date(2023, 8, 25) #datetime.now().date()
    df = df[df['date'].dt.date == curr_date]

    grouped = df.groupby(df['date'].dt.date)

    stats_df = pd.DataFrame()

    # compute statistics for each group
    # open
    stats_df['open'] = grouped['open'].first()
    # close 
    stats_df['close'] = grouped['open'].last()
    # Average closing price
    stats_df['average'] = grouped['open'].mean()

    # Median
    stats_df['median'] = grouped['open'].median()
    # Min
    stats_df['min'] = grouped['open'].min() 
    # Max
    stats_df['max'] = grouped['open'].max()
    # Standard deviation
    stats_df['standard_deviation'] = grouped['open'].std()
    # Average min max price range 
    stats_df['price_range_average'] = grouped.apply(lambda x: (x['high'] - x['low']).mean())    

    # Exponential smoothing
    smoothing_parameters = {'trend': 'add'}

    def double_exponential_smoothing(data):
        double_exp_smooth_model = sm.tsa.ExponentialSmoothing(data, **smoothing_parameters)
        double_exp_smooth_fit = double_exp_smooth_model.fit()
        smoothed_values_double_exp = double_exp_smooth_fit.fittedvalues
        return smoothed_values_double_exp

    for group_name, group_data in grouped:
        exp_smooth_model = sm.tsa.SimpleExpSmoothing(group_data['open'])
        exp_smooth_fit = exp_smooth_model.fit()
        smoothed_values_exp = exp_smooth_fit.fittedvalues

        # Double exponential smoothing
        smoothed_values_double_exp = double_exponential_smoothing(group_data['open'])

        # Update stats_df with exponential smoothing result
        stats_df.loc[group_name, 'exponential_smoothing'] = smoothed_values_exp.iloc[-1]

        # Update stats_df with double exponential smoothing result
        stats_df.loc[group_name, 'double_exponential_smoothing'] = smoothed_values_double_exp.iloc[-1]

    for col in stats_df.columns:
        if not ('open' in col or 'close' in col):
            stats_df[col + '_window2'] = [0] * len(stats_df)
            stats_df[col + '_window3'] = [0] * len(stats_df)
            stats_df[col + '_window5'] = [0] * len(stats_df)
            stats_df[col + '_window7'] = [0] * len(stats_df)

    dates = list(stats_df.index)
    for i in range(7, len(dates)):
        for k in (2, 3, 5, 7):
            cur_dates = dates[i - k:i]
            data = df[df['date'].dt.date.isin(cur_dates)]

            stats_df['average_window' + str(k)].iloc[i] = data['open'].mean()
            stats_df['median_window' + str(k)].iloc[i] = data['open'].median()
            stats_df['min_window' + str(k)].iloc[i] = data['open'].min() 
            stats_df['max_window' + str(k)].iloc[i] = data['open'].max()  
            stats_df['standard_deviation_window' + str(k)].iloc[i] = data['open'].std()
            stats_df['price_range_average_window' + str(k)].iloc[i] = (data['high'] - data['low']).mean()
            
            exp_smooth_model = sm.tsa.SimpleExpSmoothing(data['open'])
            exp_smooth_fit = exp_smooth_model.fit()
            smoothed_values_exp = exp_smooth_fit.fittedvalues

            smoothed_values_double_exp = double_exponential_smoothing(data['open'])
            stats_df['exponential_smoothing_window' + str(k)].iloc[i] = smoothed_values_exp.iloc[-1]
            stats_df['double_exponential_smoothing_window' + str(k)].iloc[i] = smoothed_values_double_exp.iloc[-1]

    stats_df = stats_df.dropna()

    # is_friday feature
    stats_df['is_friday'] = stats_df.index
    stats_df['is_friday'] = stats_df['is_friday'].apply(lambda date : int(date.weekday() == 4))

    # is_monday feature
    stats_df['is_monday'] = stats_df.index
    stats_df['is_monday'] = stats_df['is_monday'].apply(lambda date : int(date.weekday() == 0))

    # is_holiday feature
    ru_holidays = holidays.Russia()
    stats_df['is_holiday'] = stats_df.index
    stats_df['is_holiday'] = stats_df['is_holiday'].apply(lambda date : int(date in ru_holidays))

    # is_start_of_month feaute
    stats_df['is_start_of_month'] = stats_df.index
    stats_df['is_start_of_month'] = stats_df['is_start_of_month'].apply(lambda date : int(date.day == 1))

    stats_df = stats_df.reset_index()

    if len(stats_df) == 0:
        print('Данных за сегодня нет')
        return False

    old_df = pd.read_csv('data/stats_imoex_open.csv')
    stats_df = add_data(old_df, stats_df)
    stats_df.to_csv('data/stats_imoex_open.csv', index=False)

    return True # TODO обработать исключения


def unite_stats_pca():
    """
    объединяет данные из stats_imoex_open.csv и bert_pca.csv за сегодня
    и обновляет файл dataset.csv
    """
    df_nlp = pd.read_csv('data/bert_pca.csv')
    df_series = pd.read_csv('data/stats_imoex_open.csv')
    df_nlp.date = df_nlp.date.astype('str')
    df_series.date = df_series.date.astype('str')
    df_nlp = df_nlp[df_nlp['date'] == test_date] # str(datetime.now().date())
    df_series = df_series[df_series['date'] == test_date] # str(datetime.now().date())
    try:
        df = pd.merge(df_series, df_nlp, on='date', how='inner')
    except Exception as ex:
        print(f'failed to merge: {ex}')
        return False
    print(df)

    old_df = pd.read_csv('data/dataset.csv')
    df = add_data(old_df, df)
    df.to_csv('data/dataset.csv', index=False)
    return True
