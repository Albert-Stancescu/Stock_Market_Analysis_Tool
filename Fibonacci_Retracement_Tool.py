def Fibonacci_Retracement(Stock_Ticker,data):
	#Variables
	price_max = data["Close"].max()
	price_min = data["Close"].min()
	diff = price_max - price_min
	ratios = [0,0.236, 0.382, 0.5 , 0.618, 0.786,1]
	levels = []

	#Building Fibonacci Bands based on Min and Max Price values from Data
	for ratio in ratios:
		levels.append(price_max + diff*-ratio)

	return levels

