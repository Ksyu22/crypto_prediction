import requests

import pandas as pd
import numpy as np
from datetime import date, datetime

import yfinance as yf

def fetch_fng_index(limit=100000) -> pd.DataFrame:
    '''
    This function fetches fear & greed index from official api.
    By default 100000 entries are fetched.
    Start and end dates are kept for following use in fetching excahnge rate.
    '''
    url = 'https://api.alternative.me/fng/'
    params = {'limit': limit,
            'date_format': 'world'
            }
    response = requests.get(url, params).json()

    fng_df = pd.DataFrame(response['data']).drop(columns=['time_until_update', 'value_classification'])

    fng_df.timestamp = pd.to_datetime(fng_df.timestamp, format='%d-%m-%Y')
    fng_df.set_index('timestamp', inplace=True)
    fng_df.rename(columns={'value': 'fng_idx'}, inplace=True)

    fng_df.fng_idx = fng_df.fng_idx.astype('float')

    return fng_df

def fetch_start_end_dates(limit) -> pd.DataFrame:
    '''
     Fetches the start and end date of fear and greed index database
    '''
    fng_df = fetch_fng_index(limit)
    #getting the first & the last timestamp to reuse it for api data fetch
    fng_first_timestamp = fng_df.index[-1].date().strftime('%Y-%m-%d')
    fng_last_timestamp = fng_df.index[0].date().strftime('%Y-%m-%d')

    return fng_first_timestamp, fng_last_timestamp


def fetch_rate_exchange(ticker: str, limit=100000) -> pd.DataFrame:
    '''
    Fetches data from yfinance and brings it to useful format.
    '''
    start, end = fetch_start_end_dates(limit)

    df_rate = yf.download(ticker, start=start, end=end, interval = '1d')[['Close', 'High', 'Low', 'Volume']]
    df_rate.reset_index(inplace=True)
    df_rate = df_rate.copy()
    df_rate = df_rate.rename(columns={'Date': 'timestamp', 'Close': 'close', 'Volume': 'volume', 'High': 'high', 'Low': 'low'})

    df_rate.timestamp = pd.to_datetime(df_rate.timestamp).dt.tz_localize(None)
    df_rate.set_index(df_rate.timestamp, inplace=True)
    df_rate.drop(columns='timestamp', inplace=True)

    return df_rate

def fetch_data(ticker: str, limit=100000) -> pd.DataFrame:
    '''Function returns df containing fear and greed index + change rate
    for a specific ticker.'''
    fng_df = fetch_fng_index(limit)
    rate_df = fetch_rate_exchange(ticker, limit)

    fng_df = fng_df.merge(rate_df, on='timestamp', how='outer').sort_index(ascending=False)
    # ealing with nan values
    # nan values for fng index
    nan_dates = fng_df[fng_df.fng_idx.isnull()]

    # the first and last date with nan value
    first_nan_idx = datetime.strftime(nan_dates.index[0], format='%Y-%m-%d')
    last_nan_idx = datetime.strftime(nan_dates.index[-1], format='%Y-%m-%d')

    # index of the first and last date with nan value
    idx_first = fng_df.index.get_loc(first_nan_idx)
    idx_last = fng_df.index.get_loc(last_nan_idx)

    mean_nan = int(fng_df.fng_idx[idx_first-3:idx_last+4].mean())

    fng_df.fng_idx = fng_df.fng_idx.replace(np.nan, mean_nan)

    return fng_df


if __name__ == '__main__':
    print('ok')
    #fng = fetch_fng_index(15)
    #rate = fetch_rate_exchange('BTC-USD', 15)
    df = fetch_data('BTC-USD', 15)
    print(df)
