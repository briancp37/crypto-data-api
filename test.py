from main import Historical

df = Historical().Data().read_csv(exchange='bitfinex', pair='btcusd', interval='1h')
print(df)