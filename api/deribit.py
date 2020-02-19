import json
import requests
import pandas as pd
import numpy as np
import datetime

class Deribit:
    def __init__(self):
        self.uri = 'https://testapp.deribit.com/api/v2/public/'

    def get_info(self, crypto_type, contract_type):
        url = self.uri + 'get_book_summary_by_currency?currency=' + crypto_type + '&kind=' + contract_type
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None

    def options_data(self, crypto_type, pprint=False):
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
        api_data = self.get_info(crypto_type, 'option')['result']
        json_out = []
        for contract_in in api_data:
            contract_out = {}
            contract_out['volume'] = contract_in['volume']

            try:
                contract_out['bid'] = contract_in['bid_price'] * contract_in['underlying_price']
            except:
                contract_out['bid'] = np.nan
            
            try:
                contract_out['ask'] = contract_in['ask_price'] * contract_in['underlying_price']
            except:
                contract_out['ask'] = np.nan
            contract_out['strike'] = contract_in['instrument_name'][12:-2]

            if contract_in['instrument_name'][-1] == 'P':
                contract_out['option_type'] = 'put'
            elif contract_in['instrument_name'][-1] == 'C':
                contract_out['option_type'] = 'call'

            contract_out['date_exp'] = datetime.datetime.strptime(contract_in['instrument_name'][4:11], '%d%b%y').strftime('%Y-%m-%d')
            
            json_out.append(contract_out)

        if pprint == True:
            print(json.dumps(json_out, indent=2))
        return json_out


    # def dataConverter(self, kind, data):

    #     if kind == 'future':
    #         df = pd.DataFrame(data)
    #         columns = ['volume_usd', 'bid_price', 'mid_price', 'ask_price', 'instrument_name']
    #         df = df[columns]
    #         df['exp_date'] = df['instrument_name'].str[4:]
    #         df['exp_date'] = pd.to_datetime(df['exp_date'], errors='coerce')
    #         return df


    #     else:
    #         print("select kind from ['option', 'future']")
    #         return None




# if __name__ == "__main__":
#     main()