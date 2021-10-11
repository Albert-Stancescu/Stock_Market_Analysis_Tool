import matplotlib.pyplot as plt
import Bollinger_Bands_Tool as Boll
import numpy as np
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt

def exponential_smoothing(panda_series, alpha_value):
	ouput = sum([alpha_value * (1 - alpha_value) ** i * x for i, x in enumerate(reversed(panda_series))])
	return ouput


def StockChartBuilder(ticker,data,period,normalized=False,smoothing=False,Fibonacci=False,Aroon=False):

# 	#Building the plots to visualize the data
	fig, ax = plt.subplots(4,gridspec_kw={'height_ratios': [20, 5,3,3]})
	fig.set_figwidth(15)
	fig.set_figheight(15)
	ax[0].set(ylabel='Price',title=ticker + " Analysis")
	ax[0].plot(data["UpperBand"].keys()[period - 1:], data["UpperBand"][period - 1:], color='r', label='Upper Bollinger Bands')
	ax[0].plot(data["LowerBand"].keys()[period - 1:], data["LowerBand"][period - 1:], color='g', label='Lower Bollinger Bands')
	ax[0].plot(data["SMA"].keys()[period - 1:], data["SMA"][period - 1:], color='m', label='SMA')
	ax[0].plot(data["Open"].keys()[period - 1:],data["Open"][period - 1:],color='b',label=ticker)

	ax[0].scatter(data["Buy"].keys()[period - 1:], data['Buy'][period - 1:], color='green', lw=3, label = 'Buy',marker = '^', alpha = 1)
	ax[0].scatter(data["Sell"].keys()[period - 1:], data['Sell'][period - 1:], color='red', lw=3, label = 'Sell',marker = 'v', alpha = 1)
	
	ax[1].set(ylabel='RSI')	
	ax[1].plot(data["RSI"].keys()[period:],data["RSI"][period:])
	ax[1].plot(data["SRSI"].keys()[period:],data["SRSI"][period:],color='k',alpha=0.2)
	ax[1].hlines(y = 70, xmin=data["RSI"].keys()[period:][0], xmax=data["RSI"].keys()[period:][len(data["RSI"].keys()[period:]) - 1],color="r",linestyles="dashed")
	ax[1].hlines(y = 30, xmin=data["RSI"].keys()[period:][0], xmax=data["RSI"].keys()[period:][len(data["RSI"].keys()[period:]) - 1],color="r",linestyles="dashed")
	ax[1].hlines(y = 50, xmin=data["RSI"].keys()[period:][0], xmax=data["RSI"].keys()[period:][len(data["RSI"].keys()[period:]) - 1],color="k",alpha=0.3,linestyles="dashed")

	ax[2].set(ylabel="First Derivative")
	first_d = "ddy"
	if normalized == True: ax[2].set_ylim(-1,1)
	elif normalized == False:	ax[2].set_ylim([np.nanmin(data[first_d]),np.nanmax(data[first_d])])
	# ax[2].set_xlim(xmin=data["RSI"].keys()[period:][0],xmax=data["RSI"].keys()[period:][len(data["RSI"].keys()[period:]) - 1])
	ax[2].scatter(data[first_d].index.tolist(),data[first_d],color = ['r' if i < 0 else 'b' for i in data[first_d]], s = 5)
	ax[2].plot(data[first_d].index.tolist(),data[first_d],color="k")
	ax[2].hlines(y = 0, xmin=data[first_d].index.tolist()[period:][0], xmax=data[first_d].index.tolist()[-1],color="k",linestyles="dashed",alpha=0.3)


	ax[3].set(ylabel="Second Derivative")
	second_d = "dddy"
	if normalized == True: ax[3].set_ylim(-1,1)
	elif normalized == False:	ax[3].set_ylim([np.nanmin(data[second_d]),np.nanmax(data[second_d])])
	if smoothing == True:
		second_d_smooth = exponential_smoothing(data[second_d],0.3)
		# ax[3].scatter(ddy.index.tolist(),second_d_smooth.fittedvalues,color = ['r' if i < 0 else 'b' for i in second_d_smooth], s = 5)
		ax[3].plot(data[second_d].index.tolist(),second_d_smooth,color="k")
	elif smoothing == False:
		# ax[3].set_xlim(xmin=data["RSI"].keys()[period:][0],xmax=data["RSI"].keys()[period:][len(data["RSI"].keys()[period:]) - 1])
		ax[3].scatter(data[second_d].index.tolist(),data[second_d],color = ['r' if i < 0 else 'b' for i in data[second_d]], s = 5)
		ax[3].plot(data[second_d].index.tolist(),data[second_d],color="k")
	ax[3].hlines(y = 0, xmin=data[second_d].index.tolist()[period:][0], xmax=data[second_d].index.tolist()[-1],color="k",linestyles="dashed",alpha=0.3)


	#----------------------------------------------------------------------------------------------------
	fig2, ax = plt.subplots(3,gridspec_kw={'height_ratios': [1,1,1]})
	#plt.plot( df['Close'],  label='Close')#plt.plot( X-Axis , Y-Axis, line_width, alpha_for_blending,  label)
	ax[0].plot(data['s_OBV'][period:],  label='OBV', color= 'orange')
	ax[0].plot(data['OBV_EMA'][period:],  label='OBV_EMA', color= 'purple')
	ax[0].set(ylabel='OBV/OBV_EMA',xlabel="Date")

	ax[1].plot(data['OBV_EMA'].keys()[period:],data["Aroon_Up"][period:],label='Aroon Up', color= 'Green')
	ax[1].plot(data['OBV_EMA'].keys()[period:],data["Aroon_Down"][period:],label='Aroon Down', color= 'Red')
	ax[1].set(ylabel='Aroon Indicator',xlabel="date")

	ax[2].plot(data['OBV_EMA'].keys()[period:],data["Stochastic_Oscillator"][period:],label='Stochastic Oscillator', color= 'black')
	ax[2].hlines(y = 80, xmin=data["OBV_EMA"].keys()[period:][0], xmax=data["Stochastic_Oscillator"].keys()[period:][len(data["Stochastic_Oscillator"].keys()[period:]) - 1],color="r",linestyles="dashed")
	ax[2].hlines(y = 20, xmin=data["OBV_EMA"].keys()[period:][0], xmax=data["Stochastic_Oscillator"].keys()[period:][len(data["Stochastic_Oscillator"].keys()[period:]) - 1],color="r",linestyles="dashed")
	ax[2].hlines(y = 50, xmin=data["OBV_EMA"].keys()[period:][0], xmax=data["Stochastic_Oscillator"].keys()[period:][len(data["Stochastic_Oscillator"].keys()[period:]) - 1],color="k",alpha=0.3,linestyles="dashed")

	plt.show()

# def Fibonacci_Grapher(Fibonacci_Levels, xmax,xmin)