import requests

# private query nonce
import time

# private query signing
import urllib.parse
import hashlib
import hmac
import base64
import json
# import pandas as pd


# pd.set_option('display.max_rows', 10)

# logging.basicConfig()
# logger = logging.getLogger(__name__)

class KrakenAPI(object):
    """ Maintains a single session between this machine and Kraken.
    Specifying a key/secret pair is optional. If not specified, private
    queries will not be possible.
    The :py:attr:`session` attribute is a :py:class:`requests.Session`
    object. Customise networking options by manipulating it.
    Query responses, as received by :py:mod:`requests`, are retained
    as attribute :py:attr:`response` of this object. It is overwritten
    on each query.
    """
    def __init__(self, key='', secret=''):
        """ Create an object with authentication information.
        :param key: (optional) key identifier for queries to the API
        :type key: str
        :param secret: (optional) actual private key used to sign messages
        :type secret: str
        :returns: None
        """
        self.key = key
        self.secret = secret
        self.uri = 'https://api.kraken.com'
        self.apiversion = '0'
        self.session = requests.Session()
        self.name_conv = None
        self.asset_pairs = None
        # self.session.headers.update({
        #     'User-Agent': 'krakenex/' + version.__version__ + ' (+' + version.__url__ + ')'
        # })
        self.response = None
        self._json_options = {}
        return

    def json_options(self, **kwargs):
        """ Set keyword arguments to be passed to JSON deserialization.
        :param kwargs: passed to :py:meth:`requests.Response.json`
        :returns: this instance for chaining
        """
        self._json_options = kwargs
        return self

    def close(self):
        """ Close this session.
        :returns: None
        """
        self.session.close()
        return

    def load_key(self, path):
        """ Load key and secret from file.
        Expected file format is key and secret on separate lines.
        :param path: path to keyfile
        :type path: str
        :returns: None
        """
        with open(path, 'r') as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()
        return

    def _query(self, urlpath, data, headers=None, timeout=None):
        """ Low-level query handling.
        .. note::
           Use :py:meth:`query_private` or :py:meth:`query_public`
           unless you have a good reason not to.
        :param urlpath: API URL path sans host
        :type urlpath: str
        :param data: API request parameters
        :type data: dict
        :param headers: (optional) HTTPS headers
        :type headers: dict
        :param timeout: (optional) if not ``None``, a :py:exc:`requests.HTTPError`
                        will be thrown after ``timeout`` seconds if a response
                        has not been received
        :type timeout: int or float
        :returns: :py:meth:`requests.Response.json`-deserialised Python object
        :raises: :py:exc:`requests.HTTPError`: if response status not successful
        """
        if data is None:
            data = {}
        if headers is None:
            headers = {}

        url = self.uri + urlpath

        self.response = self.session.post(url, data = data, headers = headers,
                                          timeout = timeout)

        if self.response.status_code not in (200, 201, 202):
            self.response.raise_for_status()

        return self.response.json(**self._json_options)


    def query_public(self, method, data=None, timeout=None):
        """ Performs an API query that does not require a valid key/secret pair.
        :param method: API method name
        :type method: str
        :param data: (optional) API request parameters
        :type data: dict
        :param timeout: (optional) if not ``None``, a :py:exc:`requests.HTTPError`
                        will be thrown after ``timeout`` seconds if a response
                        has not been received
        :type timeout: int or float
        :returns: :py:meth:`requests.Response.json`-deserialised Python object
        """
        if self.name_conv is None:
            self.getNames()

        if data is None:
            data = {}

        urlpath = '/' + self.apiversion + '/public/' + method

        return self._query(urlpath, data, timeout = timeout)

    def query_private(self, method, data=None, timeout=None):
        """ Performs an API query that requires a valid key/secret pair.
        :param method: API method name
        :type method: str
        :param data: (optional) API request parameters
        :type data: dict
        :param timeout: (optional) if not ``None``, a :py:exc:`requests.HTTPError`
                        will be thrown after ``timeout`` seconds if a response
                        has not been received
        :type timeout: int or float
        :returns: :py:meth:`requests.Response.json`-deserialised Python object
        """
        if self.name_conv is None:
            self.getNames()

        if data is None:
            data = {}

        if not self.key or not self.secret:
            raise Exception('Either key or secret is not set! (Use `load_key()`.')

        data['nonce'] = self._nonce()

        urlpath = '/' + self.apiversion + '/private/' + method

        headers = {
            'API-Key': self.key,
            'API-Sign': self._sign(data, urlpath)
        }

        return self._query(urlpath, data, headers, timeout = timeout)

    def _nonce(self):
        """ Nonce counter.
        :returns: an always-increasing unsigned integer (up to 64 bits wide)
        """
        return int(1000*time.time())

    def _sign(self, data, urlpath):
        """ Sign request data according to Kraken's scheme.
        :param data: API request parameters
        :type data: dict
        :param urlpath: API URL path sans host
        :type urlpath: str
        :returns: signature digest
        """
        postdata = urllib.parse.urlencode(data)

        # Unicode-objects must be encoded before hashing
        encoded = (str(data['nonce']) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()

        signature = hmac.new(base64.b64decode(self.secret),
                             message, hashlib.sha512)
        sigdigest = base64.b64encode(signature.digest())

        return sigdigest.decode()

    def getNames(self):
        '''
        @return self.name_conv = {
            'ADA': 'ADA',
            ...,
            'XXBT': 'XBT',
            'ZUSD': 'USD'
        }
        '''
        urlpath = '/' + self.apiversion + '/public/Assets'
        api_ret = self._query(urlpath, data=None)
        res = api_ret['result']
        self.name_conv = {}
        for xcur in res:
            if xcur == 'XXBT':
                self.name_conv[xcur] = 'BTC'
            else:
                self.name_conv[xcur] = res[xcur]['altname']
        return self.name_conv

    def getAssetPairs(self):
        '''
        @return self.asset_pairs = {
            'ADAETH': {},
            ...,
            'XXBTZUSD': {
                'base': 'XXBT',
                'quote': 'ZUSD'
            }
        }
        '''
        urlpath = '/' + self.apiversion + '/public/AssetPairs'
        api_ret = self._query(urlpath, data=None)
        self.asset_pairs = api_ret['result']
        return self.asset_pairs

    def getBalances(self, pprint=False):
        '''
        @return self.name_conv = {
            'ADA': 'ADA',
            ...,
            'XXBT': 'XBT'
            'ZUSD': 'USD'
        }
        '''
        api_ret = self.query_private('Balance')
        if api_ret['error'] == []:
            result = api_ret['result']
            dict_out = {}
            for cur in result:
                dict_out[self.name_conv[cur]] = result[cur]
        else:
            print(api_ret)
        if pprint == True:
            print(json.dumps(dict_out, indent=2))
        return dict_out

    
    def getOpenOrders(self, pprint=False):
        api_ret = self.query_private('OpenOrders')
        json_out = api_ret
        if pprint == True:
            print(json.dumps(json_out, indent=2))
        return json_out
    
    def getClosedOrder(self, pprint=False):
        api_ret = self.query_private('ClosedOrders')
        json_out = api_ret
        if pprint == True:
            print(json.dumps(json_out, indent=2))
        return json_out

    def getTradeHistory(self, pprint=False):
        '''
        @return json_out = [
            {
                'id': str,
                'ordertxid': str,
                'postxid': str,
                'pair': str,
                'time': float,
                'type': str,
                'order_type': str,
                'price': str,
                'cost': str,
                'fee': str,
                'vol': str,
                'margin': str,
                'leverage': int,
                'buy_cur': str,
                'buy_units': str,
                'sell_cur': str,
                'sell_units': str,
            }, 
            {}, {}, ...
        ]
        '''
        if self.asset_pairs is None:
            self.getAssetPairs()

        api_ret = self.query_private('TradesHistory')
        trades = api_ret['result']['trades']
        json_out = []
        for trade_id in trades:
            trade_in = trades[trade_id]
            trade_out = {
                'id': trade_id,
                'ordertxid': trade_in['ordertxid'],
                'postxid': trade_in['postxid'],
                'pair': trade_in['pair'],
                'time': trade_in['time'],
                'type': trade_in['type'],
                'order_type': trade_in['ordertype'],
                'price': trade_in['price'],
                'cost': trade_in['cost'],
                'fee': trade_in['fee'],
                'vol': trade_in['vol'],
                'margin': trade_in['margin'],
                'leverage': int(float(trade_in['cost']) / float(trade_in['margin']))
            }
            pair = trade_in['pair']
            if trade_in['type'] == 'buy':
                trade_out['buy_cur'] = self.name_conv[self.asset_pairs[pair]['base']]
                trade_out['buy_units'] = trade_in['vol']
                trade_out['sell_cur'] = self.name_conv[self.asset_pairs[pair]['quote']]
                trade_out['sell_units'] = trade_in['cost']
            elif trade_in['type'] == 'sell':
                trade_out['buy_cur'] = self.name_conv[self.asset_pairs[pair]['quote']]
                trade_out['buy_units'] = trade_in['cost']
                trade_out['sell_cur'] = self.name_conv[self.asset_pairs[pair]['base']]
                trade_out['sell_units'] = trade_in['vol']

            json_out.append(trade_out)
        if pprint == True:
            print(json.dumps(json_out, indent=2))
        return json_out

    def getOpenPositions(self, pprint=False):
        '''
        @return json_out = [
            {
                'id': str,
                'ordertxid': str,
                'pair': str,
                'time': float,
                'type': str,
                'order_type': str,
                'price': str,
                'cost': str,
                'fee': str,
                'vol': str,
                'margin': str,
                'leverage': int,
                'buy_cur': str,
                'buy_units': str,
                'sell_cur': str,
                'sell_units': str,
            }, 
            {}, {}, ...
        ]
        '''
        if self.asset_pairs is None:
            self.getAssetPairs()
        api_ret = self.query_private('OpenPositions')
        trades = api_ret['result']

        json_out = []
        for trade_id in trades:
            trade_in = trades[trade_id]
            trade_out = {
                'id': trade_id,
                'ordertxid': trade_in['ordertxid'],
                'pair': trade_in['pair'],
                'time': trade_in['time'],
                'type': trade_in['type'],
                'order_type': trade_in['ordertype'],
                'price': str(float(trade_in['cost']) / float(trade_in['vol'])),
                'cost': trade_in['cost'],
                'fee': trade_in['fee'],
                'vol': trade_in['vol'],
                'margin': trade_in['margin'],
                'leverage': int(float(trade_in['cost']) / float(trade_in['margin']))
            }
            pair = trade_in['pair']
            if trade_in['type'] == 'buy':
                trade_out['buy_cur'] = self.name_conv[self.asset_pairs[pair]['base']]
                trade_out['buy_units'] = trade_in['vol']
                trade_out['sell_cur'] = self.name_conv[self.asset_pairs[pair]['quote']]
                trade_out['sell_units'] = trade_in['cost']
            elif trade_in['type'] == 'sell':
                trade_out['buy_cur'] = self.name_conv[self.asset_pairs[pair]['quote']]
                trade_out['buy_units'] = trade_in['cost']
                trade_out['sell_cur'] = self.name_conv[self.asset_pairs[pair]['base']]
                trade_out['sell_units'] = trade_in['vol']
            json_out.append(trade_out)
        if pprint == True:
            print(json.dumps(json_out, indent=2))
        return json_out

K = KrakenAPI()
K.load_key('/Users/bpennington/Documents/krakenReadOnly.txt')
x = K.getOpenPositions(pprint=True)
# print(x)