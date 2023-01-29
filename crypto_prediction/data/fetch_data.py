import requests

import pandas as pd
from datetime import date, datetime

import yfinance as yf

def fetch_fng_index():
    '''
    This function fetches fear & greed index from official api
    '''
    url = 'https://api.alternative.me/fng/'
    params = {'limit': 100000,
            'date_format': 'world'
            }
    response = requests.get(url, params).json()

    fng_df = pd.DataFrame(response['data']).drop(columns='time_until_update')

    fng_df.timestamp = pd.to_datetime(fng_df.timestamp, format='%d-%m-%Y')
    fng_df.set_index('timestamp', inplace=True)
    fng_df.rename(columns={'value': 'fng_idx', 'value_classification': 'fng_class'}, inplace=True)

    #getting the first & the last timestamp to reuse it for api data fetch
    fng_first_timestamp = fng_df.index[-1].date().strftime('%Y-%m-%d')
    fng_last_timestamp = fng_df.index[0].date().strftime('%Y-%m-%d')

    fng_df.fng_idx = fng_df.fng_idx.astype('float')

    return fng_df, fng_first_timestamp, fng_last_timestamp


def fetch_rate_exchange():
    '''
    Fetches data from yfinance and brings it to useful format
    '''
    df_rate = yf.download('BTC-USD', interval = '1d')[['Close', 'Volume']]
    df_rate.reset_index(inplace=True)
    df_rate = df_rate.copy()
    df_rate = df_rate.rename(columns={'Date': 'timestamp', 'Close': 'rate', 'Volume': 'volume'})

    df_rate.timestamp = pd.to_datetime(df_rate.timestamp).dt.tz_localize(None)
    df_rate.set_index(df_rate.timestamp, inplace=True)
    df_rate.drop(columns='timestamp', inplace=True)


    return df_rate


if __name__ == '__main__':
    print('ok')
    df = fetch_rate_exchange()
    print(df)
