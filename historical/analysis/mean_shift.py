import datetime
import numpy as np
from sklearn import cluster

class SrLines(object):
    def __init__(self, df_1h, band_q=.0475, n_jobs=-1):
        """
        Inputs:
            - inpt = {'1h': {'df': 0, 'mult': 1},
                      'D' : {'df': 0, 'mult': 3},
                      'W' : {'df': 0, 'mult': 5}} 
            - pair = 'btcusd'
        """
        self.df = df_1h
        self.mult = {'1h': 1, 'D':3, 'W':5}
        self.cluster_centers = []
        self.cluster_labels = []
        self.band_q = band_q
        self.n_jobs = n_jobs
        # self.BFD = Bitfinex_Data()
        # self.inpt = inpt
        # self.pair = pair
        
        # for x in list(self.inpt.keys()):
        #     self.inpt[x]['df'] = self.BFD.read_csv(self.pair, x)

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


        
    def build_data(self, input_cols, end_date=None):
        """
        Inputs:
            - input_cols = ['high', 'low']
            - end_date = datetime.utcfromtimestamp(unix_current / 1000.0)
        Outputs:
            - data = [[], ..., []]       size:n
        """
        
        if end_date == None:
            end_date = datetime.datetime.utcnow()
        i=0
        data = np.array([])
        print(self.df)
        for interval in ['1h', 'D', 'W']:
            j=0
            if interval != '1h':
                self.df = self.slicer(self.df, interval)
            for col in input_cols:
                if j==0:
                    # df = self.inpt[x]['df']
                    # df =
                    mtx_df = self.df[self.df.index < end_date]
                    mtx = mtx_df.as_matrix(columns=[col])
                else:
                    mtx = np.concatenate((mtx, self.df[self.df.index < end_date].as_matrix(columns=[col])), axis=0)
            new_data = np.repeat(mtx, self.mult[interval], axis=0)
            
            if i== 0:
                data = new_data
            else:
                data = np.concatenate((data, new_data), axis=0)
            i += 1
        
        print(data)
        print('max(data) = {}'.format(max(data))) 
        
        return data

    def sr_lines(self):  
        """
        Inputs:
            - prices = [[], ..., []]            size:(N,1) 
        Outputs:
            - self.cluster_centers = [[]]       size:n
        """
        prices = self.build_data(['high', 'low'])
        log_prices = np.log(prices)
        print('max(log_prices) = {}'.format(max(log_prices))) 
        log_prices = log_prices[~np.isnan(log_prices)]
        log_prices = log_prices.reshape(-1, 1)
#        a = time.time()
        bandwidth = cluster.estimate_bandwidth(log_prices, quantile = self.band_q, n_samples = 100)
#        b = time.time()
#        print("bandwidth time = {}".format(b-a))
        self.ms = cluster.MeanShift(bandwidth=bandwidth, bin_seeding=True, n_jobs = self.n_jobs)
#        print("cluster time = {}".format(time.time() - b))
#        d = time.time()
        self.ms.fit(log_prices)
#        e = time.time()
#        print("fit time = {}".format(e-d))
        self.cluster_centers = [np.exp(c[0]) for c in self.ms.cluster_centers_]
        return self.cluster_centers



    


