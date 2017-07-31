from pyalgotrade.broker import backtesting

class MyBroker(backtesting.Broker):
	def __init__(self, cash, barFeed, commission):
		super(MyBroker, self).__init__(cash, barFeed, commission)