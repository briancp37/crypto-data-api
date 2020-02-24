import datetime
import time
import calendar
import pandas as pd
import numpy as np
import requests
import logging
import os

pd.set_option('display.max_rows', 10)

logging.basicConfig()
logger = logging.getLogger(__name__)

class BitfinexData:
    
    def __init__(self, pair, path):
        self.pair = pair
        self.path = path + 'bitfinex/'
        self.unix_2016 = 1451606400000
        self.unix_current = time.time() * 1000
        self.units = ['1h', 'D', 'W']
    
    def Bitfinex_API_v2(self, interval, unix_start):
        """
        @return
            [
                [
                    <timestamp>, 
                    <open>, 
                    <close>, 
                    <high>, 
                    <low>, 
                    <volume>
                ], 
                [ ],  ...
            ]
        """
        uri = 'https://api.bitfinex.com/v2/candles/trade:{}:t{}/hist'.format(interval, self.pair.upper())
        url = uri + '?limit=10000&start={}&sort=1'.format(unix_start)
        print(url)
        json = requests.get(url).json()
        return json

    def download_data(self, unix_start, interval):
        '''
        
        '''
        init = False
        print(unix_start)
        print(self.unix_current)
        while unix_start < self.unix_current:
            result = self.Bitfinex_API_v2(interval, unix_start)
            arr = np.array(result)
            if init == False:
                df = pd.DataFrame(arr)
                init = True
            else:
                df_arr = pd.DataFrame(arr)
                df = pd.concat([df,df_arr])
            time.sleep(2)
            
            print(self.unix_to_utc(unix_start))
            last_ts = int(float(result[-1][0]))
            unix_start = last_ts
            
            if len(result) < 4000:
                unix_start = self.unix_current
        try:
            print('Periods updated:        {}'.format(len(result)))
            print('Updated through:        {}'.format(self.unix_to_utc(df.index[-1])))
        except:
            print('unix_current:        {}'.format(self.unix_current))
            print('STR -> unix_current: {}'.format(self.unix_to_utc(self.unix_current)))
            print('unix_time:           {}'.format(unix_start))
            print('STR -> unix_time: {}'.format(self.unix_to_utc(unix_start)))
        return df
    
    def format_data(self, df):  
        columns = ['ts', 'open', 'close', 'high', 'low', 'volume']
        df.columns = columns
        df.set_index('ts', inplace=True)
        df.drop_duplicates(inplace=True)
        df.dropna(inplace=True)
        df.index = pd.to_datetime(df.index, unit='ms')
        df.sort_index(inplace=True)
#        df = df.resample('min').ffill()
        return df
    
    def get_data(self, unix_start, interval):
        df_unformatted = self.download_data(self.unix_2016, interval)
        df = self.format_data(df_unformatted)
        return df

    def create_csv(self, interval):
        if interval == '1h':
            # df_unformatted = self.download_data(self.unix_2016, interval)
            df = self.get_data(self.unix_2016, interval)
        else:
            df = self.slicer(self.read_csv('1h'), interval)
        self.save_csv(df, interval)
        return df

    def save_csv(self, df, interval):
        # path = self.path + 'bitfinex/' 
        if not os.path.exists(self.path + self.pair):
            os.makedirs(self.path + self.pair)
        path = self.path + '{}/{}.csv'.format(self.pair, interval)
        df.to_csv(path)
        return df
        
    def read_csv(self, interval):
        path = self.path + '{}/{}.csv'.format(self.pair, interval)
        print(path)
        df = pd.read_csv(path, index_col=0, parse_dates = True)
        print('hi')
        print(df)
        # try:
        #     df = pd.read_csv(path, index_col=0, parse_dates = True)#.dropna(inplace=True)
        # except:
        #     df = False # self.create_csv(interval)
        return df 
    
    def str_to_unix(self, str_timestamp):
        datetime_obj = datetime.datetime.strptime(str_timestamp, '%Y-%m-%d %H:%M:%S')
        unix = time.mktime(datetime_obj.timetuple()) * 1000
        print(unix)
        return unix
    def unix_to_utc(self, unix_time):
        utc_time = datetime.datetime.utcfromtimestamp(unix_time*.001)
        utc_str = utc_time.strftime("%Y-%m-%d %H:%M:%S")
        return utc_str
    def current_ts_str(self):
        dt = datetime.datetime.utcnow().replace(minute=0, second=0)
        ts_cur_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        return ts_cur_str
    
    def update_csv(self):
        print("Current timestamp:       {}".format(self.current_ts_str()))
        for unit in self.units:
            df = self.read_csv(unit)
            if isinstance(df, pd.DataFrame):
                if unit == '1h':
                    print("Last recorded timestamp: {}".format(str(df.index[-1])))
                    last_ts_unix = calendar.timegm(df.index[-2].timetuple()) * 1000.0  # time.mktime
                    df_formatted = self.get_data(last_ts_unix, '1h')
                    # df_unformatted = self.download_data(last_ts_unix, '1h')
                    # df_formatted = self.format_data(df_unformatted)
                else:
                    df_formatted = self.slicer(df_formatted, unit)
            
                df_combined = pd.concat([df,df_formatted])
                df_combined.dropna(inplace=True)  
                df_combined = df_combined.loc[~df_combined.index.duplicated(keep='last')]   # dedup

                # df_combined.drop_duplicates(subset='ts', inplace=True)
                self.save_csv(df_combined, '1h')
            else:
                df_combined = self.create_csv(unit)
        return df_combined
    
    def slicer(self, df, interval):
        """
        H = hourly
        D = daily
        W = weekly
        M = monthly
        """
        if interval == '1h':
            interval = 'H'
        df_ohlcv = df.resample(interval).agg({'open':'first', 'high':'max', 'low': 'min', 'close':'last', 'volume':'sum'})
        return df_ohlcv
        