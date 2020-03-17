from .api import KrakenAPI
import pandas as pd

class Accounting:

    def __init__(self):
        pass

    def getTradeHistory(self, exchange_arr=None):
        '''
        @param exchange_arr (default = all)
        '''
        if exchange_arr is None:
            exchange_arr = ['Kraken']

        for ex in exchange_arr:

            if ex == 'Kraken':
                api = KrakenAPI()
            if ex == 'Coinbase':
                api = KrakenAPI()
            
            trades = api.getTradeHistory()

            if ex == exchange_arr[0]:
                df = pd.DataFrame(trades)
            else:
                df_= pd.DataFrame(trades)
                df.concat(df_)
                
        return df

    def getOpenPositions(self, exchange_arr=None):
        pass

    def getBalances(self, exchange_arr=None):
        pass
        
    def getOpenOrders(self, exchange_arr=None):
        pass
