#Imports
import numpy as np
import pandas as pd
import datetime
import math

import RSI_Tools

def combinatorics_3(arr): #This calculation was acquired from: http://momentum.technicalanalysis.org.uk/Ehle.pdf
	return (arr[0] + 2 * arr[1] + arr[2]) / 4
def combinatorics_7(arr): #This calculation was acquired from: http://momentum.technicalanalysis.org.uk/Ehle.pdf
	return (arr[0] + 2 * arr[1] + 3 *arr[2] + 4 * arr[3] + 3 * arr[4] + 2 * arr[5] + arr[6]) / 16


def rolling_window(a, window):
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def Normalize(data):
	result = pd.DataFrame(index=data.keys())
	d_pos,d_neg = np.where(data > 0, data, np.NaN),np.where(data < 0, data, np.NaN)
	pos_val_set,neg_val_set = False,False
	if np.isnan(d_pos).all():
		pos_max,pos_min = 0,0
		pos_val_set = True

	if np.isnan(d_neg).all():
		neg_max,neg_min = 0,0
		neg_val_set = True

	if pos_val_set == False:
		pos_max,pos_min = np.nanmax(d_pos),np.nanmin(d_pos)
	if neg_val_set == False:
		neg_max,neg_min = np.nanmax(d_neg),np.nanmin(d_neg)

	#Ensure no divide by zero errors:
	if neg_max == neg_min:
		neg_min = 0
	if pos_max == pos_min:
		pos_min = 0

	d = []
	for x in data:
		if x > 0:
			d.append((x -pos_min) / (pos_max - pos_min))
		elif x < 0:
			d.append(- (x - neg_max) / (neg_min - neg_max))
		elif x == 0:
			d.append(0)
		else:
			d.append(x)
	result[0] = d
	return result

def Trend(data,offset=1,normalize=True):
	dx = 1
	y = data.rolling(window=7).apply(lambda x: combinatorics_7(list(x))) #Smooth out the dataset
	dy= np.zeros(shape=(len(y),1))
	dy = pd.Series(np.diff(y/ dx,append=True),y.keys())
	dy[-offset:] = np.nan

	if normalize == False:
		n_dy = dy

	if normalize == True:
		# n_dy = pd.DataFrame(index=y.keys())
		n_dy = Normalize(dy)

	return n_dy


#----------------------------------------------------------------------------------------------------
def OBV(data):
	OBV = []
	OBV.append(0)
	for i in range(1, len(data["Close"])):
		if data["Close"][i] > data["Close"][i-1]: #If the closing price is above the prior close price 
			OBV.append(OBV[-1] + data["Volume"][i]) #then: Current OBV = Previous OBV + Current Volume
		elif data["Close"][i] < data["Close"][i-1]:
			OBV.append(OBV[-1] - data["Volume"][i])
		else:
			OBV.append(OBV[-1])
	return OBV

#----------------------------------------------------------------------------------------------------
def Aroon(data):
	Aroon_Up_F,Aroon_Down_F = np.empty(shape=len(data)),np.empty(shape=len(data))
	Aroon_Up_Data = data.rolling(window=25).apply(lambda x: Aroon_Up(list(x)))
	Aroon_Down_Data = data.rolling(window=25).apply(lambda x: Aroon_Down(list(x)))
	
	d = [Aroon_Up_Data,Aroon_Down_Data]
	j = 0
	for arr in d:
		i = 0
		for value in arr:
			if j == 0:
				if np.isnan(value):
					Aroon_Up_F[i] = np.nan
				else:
					Aroon_Up_F[i] = value
			if j == 1:
				if np.isnan(value):
					Aroon_Down_F[i] = np.nan
				else:
					Aroon_Down_F[i] = value
			i += 1
		j += 1
	return Aroon_Up_F,Aroon_Down_F


def Aroon_Calculator(arr):
	temp_max,temp_min = min(arr),max(arr)
	i_max, i_min = np.NaN, np.NaN
	for i in range(len(arr)):
		if arr[i] > temp_max:
			temp_max = arr[i]
			i_max = i + 1
		elif arr[i] < temp_min:
			temp_min = arr[i]
			i_min = i + 1
		else:
			continue
	return i_max,i_min

def Aroon_Up(arr):
	i_max = Aroon_Calculator(arr)[0]
	return (25 - i_max) * 100 / 25
def Aroon_Down(arr):
	i_min = Aroon_Calculator(arr)[1]
	return (25 - i_min) * 100 / 25

#----------------------------------------------------------------------------------------------------
def Stochastic_Oscillator(data):
	Smooth_data = data.rolling(window=3).apply(lambda x: combinatorics_3(list(x))) 
	Stochastic = Smooth_data.rolling(window=30).apply(lambda x: Stochastic_Oscillator_Calculator(list(x))) ##To smooth, change "data" to "Smooth_data"
	return Stochastic

def Stochastic_Oscillator_Calculator(arr):
	temp_max,temp_min = min(arr),max(arr)
	for i in range(len(arr)):
		if arr[i] > temp_max:
			temp_max = arr[i]
		elif arr[i] < temp_min:
			temp_min = arr[i]
	if temp_max == temp_min:
		return np.nan
	return (arr[13]-temp_min)/(temp_max - temp_min) * 100
#----------------------------------------------------------------------------------------------------

def Primary_Analysis(data,start_date,end_date,period): #builds Bollinger Bands
	#Variables
	multiplier = 2

	#Building the Bollinger Bands
	data['UpperBand'] = data['Close'].rolling(period).mean() + data['Close'].rolling(period).std() * multiplier
	data['LowerBand'] = data['Close'].rolling(period).mean() - data['Close'].rolling(period).std() * multiplier
	data['SMA'] = data['Close'].rolling(window=period).mean()

	#Buy and Sell Signals - basic
	signals_results = Secondary_Analysis(data)
	return (data)


def Secondary_Analysis(data,normalize=True):
	buy_signal,sell_signal = [],[] #sell list
	data["dy"] = pd.DataFrame(Trend(data["SMA"]))
	data["ddy"] = Trend(data["dy"],offset=2)
	data["dddy"] = Trend(data["ddy"],offset=3)

	data["RSI"] = RSI_Tools.RSI(data)
	data["SRSI"] = RSI_Tools.SRSI(data)
	data["OBV"] = OBV(data)
	data["OBV_EMA"] = data["OBV"].ewm(com=20).mean()
	data["s_OBV"] = data["OBV"].rolling(window=7).apply(lambda x: combinatorics_7(list(x))) 

	data["Aroon_Up"] = Aroon(data["Close"])[0]
	data["Aroon_Down"] = Aroon(data["Close"])[1]

	data["Stochastic_Oscillator"] = Stochastic_Oscillator(data["Close"])

	i,sensitivity = 0 , 0.01
	srsi_sensitivity, rsi_sensitivity, stochastic_sensitivity = 15, 30, 20

	for timeStamp, closePrice in data["Close"].iteritems():

		Stochastic = data["Stochastic_Oscillator"][i]
		RSI = data["RSI"][i]
		SRSI = data["SRSI"][i]

		observed_volume = data["s_OBV"][i]
		observed_volume_EMA = data["OBV_EMA"][i]

		Aroon_Up = data["Aroon_Up"][i]
		Aroon_Down = data["Aroon_Down"][i]


		#===================Buying Conditions=================
		buyCondition_1 = abs(closePrice/data.loc[timeStamp,'LowerBand']) < (1 + sensitivity)
		buyCondition_2 = (SRSI <= (srsi_sensitivity)) or (Stochastic <= (stochastic_sensitivity)) or (RSI <= (rsi_sensitivity))
		buyCondition_3 = observed_volume < observed_volume_EMA
		buyCondition_4 = Aroon_Down < Aroon_Up

		buyConditions = [buyCondition_1, buyCondition_2, buyCondition_3, buyCondition_4]

		#===================Selling Conditions=================
		sellCondition_1 = abs(closePrice/data.loc[timeStamp,'UpperBand']) > (1 - sensitivity)
		sellCondition_2 = (SRSI >= (100 - srsi_sensitivity)) or (Stochastic >= (100 - stochastic_sensitivity)) or (RSI >= (100 - rsi_sensitivity))
		sellCondition_3 = observed_volume > observed_volume_EMA
		sellCondition_4 = Aroon_Down > Aroon_Up

		sellConditions = [sellCondition_1, sellCondition_2, sellCondition_3, sellCondition_4]

		#=======================Assaying========================
		if all(buyConditions): #Then you should buy
			buy_signal.append(closePrice)
			sell_signal.append(np.nan)

		elif all(sellConditions): #Then you should sell 
			buy_signal.append(np.nan)
			sell_signal.append(closePrice)

		else:
			buy_signal.append(np.nan)
			sell_signal.append(np.nan)
		i += 1

	signals = (buy_signal,sell_signal)
	data["Buy"],data["Sell"]  = signals[0],signals[1]
	return (data)

# def OBV(data):
# 	df = data
# 	for OBV in data:
