
import numpy as np

import DateList_Generator as dateGen
import Fibonacci_Retracement_Tool as Fib
import Bollinger_Bands_Tool as Boll
from pandas_datareader import data as pdr
from yahoo_fin import stock_info as si
import matplotlib.pyplot as plt
from pandas import ExcelWriter
import yfinance as yf
import pandas as pd
import datetime
import time

def Trend(data):

	dx = 1
	y = data
	dy = np.zeros(shape=(len(y),1))
	ddy = np.zeros(shape=(len(y),1))

	dy = np.diff((y)/dx,append=True)
	ddy = np.diff((dy)/dx,append=True)

	return (dy,ddy)
