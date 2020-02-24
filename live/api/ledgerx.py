import json
import requests
import pandas as pd
import datetime


class LedgerX:
    def __init__(self):
        self.df_calls = pd.DataFrame()
        self.df_puts  = pd.DataFrame()

    def api_contracts(self, pprint=False):
        url = 'https://trade.ledgerx.com/api/contracts?after_ts=2019-12-18T07%3A00%3A00.000Z&limit=0'
        r = requests.get(url)
        x = r.json()
        if pprint == True:
            print(json.dumps(x, indent =2))
        return x

    def api_booktops(self, pprint=False):
        url = 'https://trade.ledgerx.com/api/book-tops?contract_id&limit=0'
        r = requests.get(url)
        x = r.json()['data']
        dict_out = {}
        for bt in x:
            dict_out[bt['contract_id']] = {
                'bid': bt['bid'],
                'ask': bt['ask']
            }
        if pprint == True:
            print(json.dumps(dict_out, indent =2))
        return dict_out

    def options_data(self, crypto_type='BTC', pprint=False):
        '''
        @param crypto_type:string   ex:'BTC'
        @return [
            {
                "volume": int,
                "bid": float,
                "ask": float,
                "strike": float,
                "option_type": "put",
                "date_exp": "2020-01-01"
            }, 
            {}, ...
        ]
        '''
        api_data_bt = self.api_booktops()
        api_data = self.api_contracts()['data']
        json_out = []
        for contract_in in api_data:
            if contract_in['derivative_type'] == 'options_contract':
                try:
                    contract_out = {}
                    contract_out['volume'] = contract_in['open_interest']
                    contract_out['bid'] = api_data_bt[contract_in['id']]['bid']
                    contract_out['ask'] = api_data_bt[contract_in['id']]['ask']
                    contract_out['strike'] = contract_in['strike_price'] * .01
                    contract_out['option_type'] = contract_in['type']
                    contract_out['date_exp'] = contract_in['date_expires'][:10]
                    json_out.append(contract_out)
                except: pass
        if pprint == True:
            print(json.dumps(json_out, indent =2))
        return json_out







    # def get_info_old(self):

    #     columns = ['label', 'underlying_asset', 'collateral_asset', 'active', 'type', 'strike_price', 'date_expires', 'derivative_type'] 
    #     data = self.ledgerx_contracts()['data']
    #     df_c = pd.DataFrame().from_records(data, index='id')
    #     df_c = df_c[columns]

    #     data_bt = self.ledgerx_booktops()['data']
    #     df_bt = pd.DataFrame().from_records(data_bt, index='contract_id')
    #     df_bt = df_bt[['bid', 'ask']]

    #     df = df_c.join(df_bt, how='inner')
    #     df.strike_price = df.strike_price * .01
    #     df.bid          = df.bid * .01
    #     df.ask          = df.ask * .01

    #     print(df)
    #     # s = df.strike_price.dropna().unique().tolist()
    #     # ss = s.sort()
    #     # print(type(s))
    #     # print(s)
    #     # print(sorted(s))
    #     all_options = {
    #         'strike': sorted(df.strike_price.dropna().unique().tolist()),
    #         'expiration': df.date_expires.dropna().unique().tolist()
    #     }

    #     print(all_options)

    #     self.df_calls = df[df.type=='call']
    #     self.df_puts  = df[df.type=='put']

    #     # strikes = df.strike_price.unique().tolist()
    #     # exp_dates = df.date_expires.unique().tolist()

        
    #     return self.df_calls, self.df_puts, all_options
# LedgerX().api_booktops(pprint=True)
