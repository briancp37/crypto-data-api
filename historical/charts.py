import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates




def chart(df, lines, *args):
    df_ohlc = df[['open', 'high', 'low', 'close']]['2017-06-01':]
    df_ohlc['timestamp'] = df_ohlc.index.map(mdates.date2num)
    df_ohlc = df_ohlc[['timestamp', 'open', 'high', 'low', 'close']]
    
    f1, ax = plt.subplots(figsize = (20,12))
    
    # plot the candlesticks
    candlestick_ohlc(ax, df_ohlc.values , width=.6, colorup='green', colordown='red')
    
    for line in lines:
        ax.axhline(y=line, color = 'grey', linestyle = 'dashed')

    for hline in args:
        ax.axhline(y=hline, color = 'purple', linestyle = 'dotted')
     
    plt.xlabel('Date')
    plt.ylabel('Price')
    # plt.title(pair.upper() + ' Technical Analysis')
    plt.legend()
    #plt.subplots_adjust(left = .09, bottom = .2, right = .94, top = .9, wspace = .2)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    
    plt.show()