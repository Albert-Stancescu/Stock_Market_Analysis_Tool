# Imports
import yfinance as yf
from yahoo_fin import stock_info as si
from multiprocessing import Pool
from pandas_datareader import data as pdr
import pandas as pd
import numpy as np
import datetime
import time

from Stock_Data_Compiler_V2 import StockChart
from Excel_Writer import Stock_to_Excel


yf.pdr_override()
s = time.time()

#=================Initialization===================
LSTM_Analysis = False
Track_to_Excel = True

if __name__ == '__main__':
    all_tickers, tickers = [], []
    # all_tickers.extend(ticker for ticker in si.tickers_sp500())
    all_tickers.extend(ticker for ticker in si.tickers_nasdaq())
    # all_tickers.extend(ticker for ticker in si.tickers_dow())
    all_tickers.extend(ticker for ticker in si.tickers_other())
    for ticker in all_tickers:
        if ticker not in tickers:
            tickers.append(ticker)
        else:
            continue

    print(tickers)
    print(f'Currently assaying {len(tickers)} individual stocks.')

    tickers = [item.replace(".", "-") for item in tickers] # Yahoo Finance uses dashes instead of dots
    index_name = '^GSPC' # S&P 500
    # start_date = datetime.datetime.now() - datetime.timedelta(days=365)
    # end_date = datetime.date.today()
    period = 500
    start_date = datetime.date.today() - datetime.timedelta(days=(365 + period))
    end_date = datetime.date.today() 
    buyList = pd.DataFrame(columns=['Stock', "Close", "RS_Rating", "50 Day MA", "150 Day Ma", "200 Day MA", "52 Week Low", "52 week High"])
    sellList = pd.DataFrame(columns=['Stock', "Close", "RS_Rating", "50 Day MA", "150 Day Ma", "200 Day MA", "52 Week Low", "52 week High"])

    # # Index Returns
    index_df = pdr.get_data_yahoo(index_name, start_date, end_date)
    index_df['Percent Change'] = index_df['Adj Close'].pct_change()
    index_return = (index_df['Percent Change'] + 1).cumprod()[-1]

    Stock_Data_Compiler = []
    i = 0
    path = r'D:\Stock Analysis/S&P 500'
    while i < len(tickers):
        Stock_Data_Compiler.append([tickers[i],index_df,index_return,path])
        i += 1

    cpus = 5
    with Pool(cpus) as p:
        df = p.starmap(StockChart,Stock_Data_Compiler)

    # Creating dataframe of only top 30%
    rs_df = pd.DataFrame(list(zip(tickers, df)), columns=['Ticker', 'Returns_multiple'])
    rs_df['RS_Rating'] = rs_df.Returns_multiple.rank(pct=True) * 100
    rs_df = rs_df[rs_df.RS_Rating >= rs_df.RS_Rating.quantile(.70)]

    # Checking Minervini conditions of top 30% of stocks in given list
    rs_stocks = rs_df['Ticker']
    for stock in rs_stocks:    
        try:
            df = pd.read_csv(rf'{path}/stock_{stock}.csv', index_col=0)
            sma = [50, 150, 200]

            #Cannot do technical analysis with stocks that have not been on the markets for a long time. 30 days was chosen arbitarily.
            if len(df["Close"]) < (period + 10):
                continue

            for x in sma:
                df["SMA_"+str(x)] = round(df['Adj Close'].rolling(window=x).mean(), 2)
            
            # Storing required values 
            currentClose = df["Adj Close"][-1]
            moving_average_50 = df["SMA_50"][-1]
            moving_average_150 = df["SMA_150"][-1]
            moving_average_200 = df["SMA_200"][-1]
            Close = df["Close"][-1]
            currentRSI = df["RSI"][-1]
            check_days = 2
            buy_signals = df["Buy"][-check_days:]
            sell_signals = df["Sell"][-check_days:]
            low_of_52week = round(min(df["Low"][-260:]), 2)
            high_of_52week = round(max(df["High"][-260:]), 2)
            RS_Rating = round(rs_df[rs_df['Ticker']==stock].RS_Rating.tolist()[0])

            
            try:
                moving_average_200_20 = df["SMA_200"][-20]
            except Exception:
                moving_average_200_20 = 0

            try:
                moving_average_200_20_max = max(df["SMA_200"][:-20])
            except Exception:
                c = len(df["SMA_200"])
                moving_average_200_20_max = max(df["SMA_200"][:-c])

            # # Condition 1: Current Price > 150 SMA and > 200 SMA
            # condition_1 = currentClose > moving_average_150 > moving_average_200
            
            # # Condition 2: 150 SMA and > 200 SMA
            # condition_2 = moving_average_150 > moving_average_200

            # Condition 3: 200 SMA trending up for at least 1 month
            condition_3 = moving_average_200 > moving_average_200_20
            
            # # Condition 4: 50 SMA > 150 SMA and 50 SMA> 200 SMA
            # condition_4 = moving_average_50 > moving_average_150 > moving_average_200
               
            # # Condition 5: Current Price > 50 SMA
            # condition_5 = currentClose > moving_average_50
               
            # Condition 6: Current Price is at least 30% above 52 week low
            condition_6 = currentClose >= (1.3 * low_of_52week)
               
            # Condition 7: Current Price is within 25% of 52 week high
            condition_7 = currentClose >= (.75 * high_of_52week)

            # # Condition 8: Checking for a low RSI value
            # condition_8 = currentRSI < 30

            # Condition 9: Checking if a recent BUY signal was made in the past {check} days
            buy_Condition = (buy_signals.count() >= 1)

            # Condition 10: Checking if a recent SELL signal was made in the past {check} days
            sell_Condition = (sell_signals.count() >= 1)

            # Condition 11: Check to see if the spike recently spiked, and is falling.
            # condition_11 = (moving_average_200 * 2) > moving_average_200_20_max
            
            # If all conditions above are true, add stock to exportList
            if buy_Condition:
                buyList = buyList.append({'Stock': stock, 'Close': Close, "RS_Rating": RS_Rating ,"50 Day MA": moving_average_50, "150 Day Ma": moving_average_150, "200 Day MA": moving_average_200, "52 Week Low": low_of_52week, "52 week High": high_of_52week}, ignore_index=True)

            if sell_Condition:
                sellList = sellList.append({'Stock': stock,'Close': Close, "RS_Rating": RS_Rating ,"50 Day MA": moving_average_50, "150 Day Ma": moving_average_150, "200 Day MA": moving_average_200, "52 Week Low": low_of_52week, "52 week High": high_of_52week}, ignore_index=True)

        except Exception as e:
            print (e)
            print(f"Could not gather data on {stock}")

    if len(buyList) != 0:
        for BuyStock in buyList["Stock"]:
            print (BuyStock + " made the Buy requirements")
    else:
        print("No stocks made the set conditions for buying!")
    
    time.sleep(5)

    if len(sellList) != 0:
        for SellStock in sellList["Stock"]:
            print (SellStock + " made the Sell requirements")
    else:
        print("No stocks made the set conditions for selling!")

    buyList = buyList.sort_values(by='RS_Rating', ascending=False)
    buyWriter = pd.ExcelWriter("Buy Indicators ScreenOutput.xlsx")
    buyList.to_excel(buyWriter, "Sheet1")
    buyWriter.save()

    sellList = sellList.sort_values(by='RS_Rating', ascending=False)
    sellWriter = pd.ExcelWriter("Sell Indicators ScreenOutput.xlsx")
    sellList.to_excel(sellWriter, "Sheet1")
    sellWriter.save()

    TickerList = pd.DataFrame(tickers,columns=["Stock_Name"])
    AllStocks = TickerList.sort_values(by="Stock_Name",ascending=True)
    AllStocksWriter = pd.ExcelWriter("AllStocks.xlsx")
    AllStocks.to_excel(AllStocksWriter, "Sheet1")
    AllStocksWriter.save()

    e = time.time()
    print(f'Total Time Elapsed = {(e-s) / 60} minutes')

    # if LSTM_Analysis == True:
    # from LSTM_Stocks_V2 import LSTM
    #     s = time.time()
    #     print('Running LSTM analysis')
    #     for BuyStock in buyList["Stock"]:
    #         LSTM(BuyStock)
    #     e = time.time()
    #     print(f'Total Time Elapsed = {(e-s) / 60} minutes')

    if Track_to_Excel == True:
        Stock_to_Excel(buyList,sellList,path)
