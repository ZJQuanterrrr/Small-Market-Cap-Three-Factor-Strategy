# -*- coding: utf-8 -*-
"""
@author: C.Z.J
"""
import akshare as ak
import pandas as pd
import datetime
import time
import matplotlib
import matplotlib.pyplot as plt
import math
import numpy as np
import talib


# set graph style
matplotlib.rcParams['axes.unicode_minus']=False
plt.rcParams['font.sans-serif']=['SimHei'] # show Chinese character
plt.style.use('seaborn')

# get stock code
stock_code = []
# get code of A-stock in Shanghai/Shenzhen/Beijing Stock Exchange
stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
stock_code.extend(stock_zh_a_spot_em_df['代码'])

del stock_zh_a_spot_em_df

# get code of new stock
stock_new_a_spot_em_df = ak.stock_new_a_spot_em()
stock_code.extend(stock_new_a_spot_em_df['代码'])

del stock_new_a_spot_em_df

# get code of stock in China Growth Enterprise Board
stock_cy_a_spot_em_df = ak.stock_cy_a_spot_em()
stock_code.extend(stock_cy_a_spot_em_df['代码'])

del stock_cy_a_spot_em_df

# get code of stock in SSE Star Market
stock_kc_a_spot_em_df = ak.stock_kc_a_spot_em()
stock_code.extend(stock_kc_a_spot_em_df['代码'])

del stock_kc_a_spot_em_df

stock_code = list(set(stock_code)) # delete duplicate code


# get pe, pb, ps, total_mv
Code = []
Problem_stock = []
Pe = []
Pb = []
Ps = []
Total_mv = []
date = datetime.date(2022, 11, 1) # the day that we select stocks


# compute the time
start = time.time()
# get data
for code in stock_code:
    
    try:
        start1 = time.time()
        
        stock_a_indicator_lg_df = ak.stock_a_indicator_lg(symbol=code)
        stock_a_indicator_lg_df = stock_a_indicator_lg_df.set_index(stock_a_indicator_lg_df.columns[0])
        Pe.append(stock_a_indicator_lg_df.loc[date, 'pe'])
        Pb.append(stock_a_indicator_lg_df.loc[date, 'pb'])
        Ps.append(stock_a_indicator_lg_df.loc[date, 'ps'])
        Total_mv.append(stock_a_indicator_lg_df.loc[date, 'total_mv'])
        Code.append(code)
        
        del stock_a_indicator_lg_df
        
        end1 = time.time()
        print(code, 'finished!')
        print('Get List_Running time: %s Seconds'%(end1 - start1))
    except:
        Problem_stock.append(code)
        print(code, 'error!')
        pass
        
end = time.time()
print('Get Total_Running time: %s Seconds'%(end - start))
del start, start1, end, end1
del stock_code, code, date

# input data into dataframe
df0 = pd.DataFrame()
df0['code']=Code
df0['pe']=Pe
df0['pb']=Pb
df0['ps']=Ps
df0['total_mv']=Total_mv

del Code, Pe, Pb, Ps, Total_mv


# condition
df1=df0[   df0['pe']<20    ]
df1=df1[   df1['pb']<2     ] 
df1=df1[   df1['ps']<5     ] 
df1=df1[   df1['total_mv']<1000000   ]


# pick the potentially profitable stock
df1=df1.sort_values(by="pe" , ascending=True)
df1=df1.head(50)
df1=df1.sort_values(by="ps" , ascending=True)
df1=df1.head(30)
df1=df1.sort_values(by="pb" , ascending=True)
df1=df1.head(10)
df1=df1['code']# get the portfolio
df1.values.tolist()# transform to list
stock=','.join(df1) # use ',' to divide the element


cum=0
for i in df1:
    df = ak.stock_zh_a_hist(symbol=i, period="daily", start_date="20221101", end_date='20230420', adjust="hfq")
    df = df.set_index(df.columns[0])
    ret = df['涨跌幅'] / 100# transform % unit to normal unit
    cum = (np.cumprod(1+ret)-1)/len(df1) + cum# equally-weighted portfolio

del i
del df1, df, ret


# get data of CSI 300
df12  = ak.stock_zh_index_daily(symbol="sh000300")
df12 = df12.set_index(df12.columns[0])
date1 = datetime.date(2022, 10, 31)
date2 = datetime.date(2023, 4, 20)
date11 = datetime.date(2022, 11, 1)
ret12 = df12.loc[date1:date2, 'close'].pct_change().dropna(axis=0)
cum12 = np.cumprod(1+ret12)-1
date = df12.loc[date11:date2].index

del date1, date2, date11


# draw plot
plt.plot(date, cum, label = 'portfolio', color='darkred')
plt.plot(date, cum12, label="CSI 300", color='darkcyan')
plt.title('Small market-cap three-factor strategy yield')
plt.legend()


f=cum[-2]*245/len(date)
f1=100*f# transform to % unit
print("annualized return：{:.2f}%, total return: {:.2f}%".format(f1, f1*len(date)/250))