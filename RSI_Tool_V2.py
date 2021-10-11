import datetime
import pandas as pd
import numpy as np
import pandas_datareader as pdr

def RSI(df):
	# start_date = datetime.date.today() - datetime.timedelta(days=(365))
	# end_date = datetime.date.today() 
	# df = pdr.get_data_yahoo(ticker,start=start_date,end=end_date)
	# print(df)
	
	upList = np.zeros(shape=(14))
	downList = np.zeros(shape=(14))
	data = df["Adj Close"]
	RSI_first_step = True
	i,p = 0,0
	RSI,RS = [],[]

	while i < (len(data) - 1):
		diff = data[i + 1] - data[i]
		if p < 13: # Stop at p = 12 because we want to set up 13 indeces before we do the RSI first step calculation
			p += 1
			if diff > 0:
				upList[i] = diff
				downList[i] = 0
			elif diff < 0:
				upList[i] = 0
				downList[i] = diff
			else:
				upList[i] = 0
				downList[i] = 0

		else:
			if RSI_first_step:  # Detect RSI first step. Add 14th index, and begin calculating the RSI.
				if diff > 0:
					upList[i] = diff
					downList[i] = 0
				elif diff < 0:
					upList[i] = 0
					downList[i] = diff
				elif diff == 0:
					upList[i] = 0
					downList[i] = 0
				
				RSI_first_step = False
				avg_gain = sum(upList) / 14
				avg_loss = sum(downList) / 14
				RSI.append((100 - (100 / (1 + (avg_gain / -avg_loss)))))
			
			else: # RSI calculation differs once 14 data values are acquired.

				# print(upList,downList)
				upList = np.concatenate((upList[1:], np.full(1, 0))) # Shift the array.
				downList = np.concatenate((downList[1:], np.full(1, 0)))
				# print(upList,downList)

				if diff > 0:
					new_avg_gain = avg_gain * 13 + diff 
					new_avg_loss = avg_loss * 13
					RSI.append((100 - (100 / (1 + ((new_avg_gain)/ -new_avg_loss)))))

					upList[13] = diff
					downList[13] = 0

				elif diff < 0:
					new_avg_gain = avg_gain * 13
					new_avg_loss = avg_loss * 13 + diff
					RSI.append((100 - (100 / (1 + (new_avg_gain / -(new_avg_loss + diff))))))

					upList[13] = 0
					downList[13] = diff

				elif diff == 0:
					new_avg_gain = avg_gain * 13
					new_avg_loss = avg_loss * 13
					RSI.append(100)

					upList[13] = 0
					upList[13] = 0

				avg_gain = new_avg_gain / 14
				avg_loss = new_avg_loss / 14

		i += 1
	RSI = np.concatenate((np.full(14, 0),RSI[:])) # To make the final result index equal the length of the original dataframe
	return RSI
