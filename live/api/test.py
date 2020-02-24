from deribit import Deribit
from ledgerx import LedgerX

_Deribit = Deribit()
_Deribit.options_data('BTC', pprint=True)

_LedgerX = LedgerX()
_LedgerX.options_data('BTC', pprint=True)

