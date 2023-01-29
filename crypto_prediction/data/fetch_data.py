import requests

import pandas as pd
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

    fng_df = pd.DataFrame(response['data']).drop(columns='time_until_update')

    fng_df.timestamp = pd.to_datetime(fng_df.timestamp, format='%d-%m-%Y')
    fng_df.set_index('timestamp', inplace=True)
    fng_df.rename(columns={'value': 'fng_idx', 'value_classification': 'fng_class'}, inplace=True)

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

    df_rate = yf.download(ticker, start=start, end=end, interval = '1d')[['Close', 'Volume']]
    df_rate.reset_index(inplace=True)
    df_rate = df_rate.copy()
    df_rate = df_rate.rename(columns={'Date': 'timestamp', 'Close': 'rate', 'Volume': 'volume'})

    df_rate.timestamp = pd.to_datetime(df_rate.timestamp).dt.tz_localize(None)
    df_rate.set_index(df_rate.timestamp, inplace=True)
    df_rate.drop(columns='timestamp', inplace=True)

    return df_rate

def fetch_data(ticker: str, limit=100000) -> pd.DataFrame:
    '''Funcrtion returns df containing fear and greed index + change rate
    for a specific ticker.'''
    fng_df = fetch_fng_index(limit)
    rate_df = fetch_rate_exchange(ticker, limit)

    return fng_df.merge(rate_df, on='timestamp')


if __name__ == '__main__':
    print('ok')
    #fng = fetch_fng_index(15)
    #rate = fetch_rate_exchange('BTC-USD', 15)
    df = fetch_data('BTC-USD', 15)
    print(df)
