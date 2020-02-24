from .api import BitfinexData
from .analysis import SrLines
from .charts import chart
import numpy as np

class Data:
    def __init__(self):
        self.functions = {
            'bitfinex': BitfinexData
        }
        self.units = ['1h', 'D', 'W']
        self.path = '/Users/bpennington/git/crypto_data_api/historical/Data/'

    def create_csv(self, exchange, pair, interval):
        return self.functions['bitfinex'](pair, self.path).create_csv(interval)

    def read_csv(self, exchange, pair, interval, ts_start=0, ts_end=0):
        return self.functions[exchange](pair, self.path).read_csv('1h')#.dropna(inplace=True)

    def update_csv(self, exchange, pair):
        #Updates the '1h', 'D', and 'W' csv files.
        return self.functions['bitfinex'](pair, self.path).update_csv()
        
class Analysis:
    def __init__(self):
        pass

    def sr_lines(self, df, plot = False, band_q=.0475, n_jobs=-1, ):
        SRL = SrLines(df)
        self.lines = SRL.sr_lines()
        # self.lines = np.sort(self.lines)
        # self.lines = np.append(self.lines, max(df['high']))
        # self.lines = np.insert(self.lines, 0, 0, axis=0)
        if plot == True:
            chart(df, self.lines)
        return self.lines

