import json
import pandas as pd

from api import Deribit
from api import LedgerX


class Options:

    def __init__(self, crypto_type, exchanges):
        self.exchanges = exchanges
        self.crypto_type = crypto_type
        self.data = self.get_data()

    def get_data(self, pprint=False):
        '''
        @param crypto_type:string   ex:'BTC'
        @return {
            'lexgerx': [
                {
                    "volume": int,
                    "bid": float,
                    "ask": float,
                    "strike": float,
                    "option_type": "put",
                    "date_exp": "2020-01-01"
                }, 
                {}, ...
            ],
            'ledgerx': [
                {}, {}, ...
            ]
        }
        '''
        dict_out = {}
        for ex in self.exchanges:
            if ex == 'deribit': 
                dict_out['deribit'] = Deribit().options_data(self.crypto_type)
            if ex == 'ledgerx': 
                dict_out['ledgerx'] = LedgerX().options_data(self.crypto_type)
        if pprint==True:
            print(json.dumps(dict_out, indent=2))
        return dict_out
    
    def get_df(self, pprint=False):
        for ex in self.exchanges:
            if ex == self.exchanges[0]:
                df = pd.DataFrame(self.data[ex])
                df['exchange'] = ex
            else:
                df_ex = pd.DataFrame(self.data[ex])
                df_ex['exchange'] = ex
                df = pd.concat([df, df_ex])
        if pprint==True:
            print(df)
        return df





        


exchanges = ['deribit', 'ledgerx']
Options('BTC', exchanges).get_df(pprint=True)