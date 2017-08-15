from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
import mybroker
import pdb

class MyBaseStrategy(strategy.BacktestingStrategy):
	def __init__(self, feed, broker, instrument, signal, smaPeriodFast, smaPeriodSlow = None):
		self.__instrument = instrument
		self.__position = None
		super(MyBaseStrategy, self).__init__(feed, broker)

		# We'll use adjusted close values instead of regular close values.
		self.setUseAdjustedValues(False)
		self.__prices = feed[instrument].getPriceDataSeries()
		self.__signal = signal
		self.__smaFast = ma.SMA(self.__prices, smaPeriodFast)
		if smaPeriodSlow is not None:
			self.__smaSlow = ma.SMA(self.__prices,smaPeriodSlow)
		else:
			self.__smaSlow = None

	def getSMAFast(self):
		return self.__smaFast

	def getSMASlow(self):
		return self.__smaSlow

	def onEnterOk(self, position):
		#pdb.set_trace()
		execInfo = position.getEntryOrder().getExecutionInfo()
		self.info("BUY at $%.2f" % (execInfo.getPrice()))

	def onEnterCanceled(self, position): 
		self.__position = None

	def onExitOk(self, position):
		execInfo = position.getExitOrder().getExecutionInfo()
		self.info("SELL at $%.2f" % (execInfo.getPrice()))
		self.__position = None

	def onExitCanceled(self, position):
		# If the exit was canceled, re-submit it.
		self.__position.exitMarket()

	def onBars(self, bars):
		if self.__smaFast[-1] is None:
			return 
		elif self.__smaSlow is not None and self.__smaSlow[-1] is None:
			return

		bar = bars[self.__instrument]

		# If a position was not opened, check if we should enter a long position.
		if self.__position is None:
			if self.__signal.enterLongSignal(self.__prices, bar, self.__smaFast, self.__smaSlow):
				shares = float(self.getBroker().getCash() * 0.99 / bars[self.__instrument].getPrice())
				 # Enter a buy market order. The order is good till canceled.
				self.__position = self.enterLong(self.__instrument, shares, True)
		# Check if we have to exit the position.
		elif not self.__position.exitActive():
			if self.__signal.exitLongSignal(self.__prices, bar, self.__smaFast, self.__smaSlow):
				self.__position.exitMarket()