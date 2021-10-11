import DateList_Generator as dateGen
import Fibonacci_Retracement_Tool as Fib
import Stock_Analysis_Tool
import Stock_Chart_Visualizer

from pandas_datareader import data as pdr
from pathlib import Path
import yfinance as yf
import pandas as pd
import datetime
import time



def closest(lst, K):
	return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]

def StockChart(Stock_Ticker,Index=None,IndexReturn=None,path=None,start_first=False,trigger=True):
	s = time.time()
	print(f"Ticker is: {Stock_Ticker}")
	conditions = [path,start_first]
	if all(condition in [None, False] for condition in conditions): #This is designed to understand if this code is being passed stande-alone or from another script.
		trigger = False

	pd.set_option("display.max_rows", None, "display.max_columns", None)
	
	try:
		Str_Ticker = Stock_Ticker.upper()
	except Exception:
		print(f"Invalid stock ticker passed through the analysis tool. Query: {Stock_Ticker}")
	
	period = 20
	time_diff = 365 * 1 + period
	start_date = datetime.date.today() - datetime.timedelta(days=(time_diff))
	end_date = datetime.date.today() 
	
	if start_first == False: #If directed to from the screening tool
		try:
			df = pdr.get_data_yahoo(Str_Ticker,start=start_date,end=end_date)
		except Exception as e:
		 	print(f"Failed to retrieve stock information of {Str_Ticker} due to {e}")
		 	return

	if start_first == True: #If directed to from the LSTM analysis
		time_diff = 365 * 70 + period
		for i in range(time_diff):
			time_diff -= i
			start_date = datetime.date.today() - datetime.timedelta(days=(time_diff))
			try:
				df = pdr.get_data_yahoo(Str_Ticker,start=start_date, end=end_date)
				print(f"Stock data for {Str_Ticker} acquired.")
				break
			except OverflowError:
				continue
	
	# if len(df) < (end_date - start_date - datetime.timedelta(days=(time_diff/7 * 2 + 10))).days:
	# 	exit()
	
	try:
		check = (datetime.date.today() - df.index[0].to_pydatetime().date()).days
		if(check < 30):
			print(rf"Exited application early: {Stock_Ticker} has only been available for {check} days.")
			return
	except Exception as e:
		pass

	try:
		Analysis_df = Stock_Analysis_Tool.Primary_Analysis(df,start_date,end_date,period)
		print(f'{Str_Ticker} has been analyzed.')
	except Exception as e:
		print(f"Could not analyze {Str_Ticker} due to the following exception: {e}")
		return

	if trigger is False:
		# Stock_Chart_Visualizer.StockChartBuilder(Str_Ticker,Analysis_df,period)
		e = time.time()
		# print(f'Pandas Concat Time = {e-s}')
		return Analysis_df

	if trigger is True:
		try:
			Analysis_df['Percent Change'] = Analysis_df['Adj Close'].pct_change()
			stock_return = (df['Percent Change'] + 1).cumprod()[-1]
			return_multiple = round((stock_return / IndexReturn), 2)
			print (f'Ticker: {Str_Ticker}; Returns Multiple against S&P 500: {return_multiple}\n')
		except Exception as e:
			pass

		# Analysis_df.to_csv(rf'{path}/stock_{Str_Ticker}.csv')
		output_file = f'stock_{Str_Ticker}.csv'
		output_dir = Path(f'{path}')
		output_dir.mkdir(parents=True, exist_ok=True)
		Analysis_df.to_csv(output_dir / output_file)
		e = time.time()
		# print(f'Pandas Concat Time = {e-s}')

		try:
			return return_multiple
		except UnboundLocalError:
			return
	
	e = time.time()
	print(f'Pandas Concat Time = {e-s}')
	return 
	
	# print(df)

	# Fibonacci_Levels = Fib.Fibonacci_Retracement(Str_Ticker,df)

	# #Combine the Fibonacci Retracement with Bollinger Bands
	# for i in range(len(BollBandsdf["Buy"])):
	# 	if type(BollBandsdf["Buy"][i]) != 'numpy.float64':
	# 		continue
	# 	else:
	# 		closestVal = closest(Fibonacci_Levels,BollBandsdf["Buy"][i]) 
	# 		print("Printing",closestVal)

		# if BollBandsdf["Buy"][i] 