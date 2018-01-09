from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade.technical import macd
import mybroker
from mystrategy.huobi import huobiapi
import pdb

class MyBaseStrategy(strategy.BacktestingStrategy):
	def __init__(self, feed, broker, instrument, signal, smaPeriodFast = None, 
		         smaPeriodSlow = None, emaPeriodFast = None, emaPeriodSlow = None,
		         emaPeriodSignal = None):
		self.__instrument = instrument
		self.__position = None
		super(MyBaseStrategy, self).__init__(feed, broker)

		# We'll use adjusted close values instead of regular close values.
		self.setUseAdjustedValues(False)
		self.__signal = signal
		self.__signal.prices = feed[instrument].getPriceDataSeries()
		if smaPeriodFast is not None:
			self.__signal.smaFast = ma.SMA(self.__signal.prices, smaPeriodFast)

		if smaPeriodSlow is not None:
			self.__signal.smaSlow = ma.SMA(self.__signal.prices, smaPeriodSlow)

		if emaPeriodFast is not None:
			self.__signal.emaFast = ma.EMA(self.__signal.prices, emaPeriodFast)
			
		if emaPeriodSlow is not None:
			self.__signal.emaSlow = ma.EMA(self.__signal.prices, emaPeriodSlow)

		if emaPeriodFast is not None and emaPeriodSlow is not None and emaPeriodSignal is not None:
			self.__signal.macd = macd.MACD(self.__signal.prices, emaPeriodFast, emaPeriodSlow, emaPeriodSignal)

	def _truncFloat(self, floatvalue, decnum):
		tmp = int('1' + '0' * decnum)
		return float(int(floatvalue * tmp)) / float(tmp)

	def getSMAFast(self):
		return self.__signal.smaFast

	def getSMASlow(self):
		return self.__signal.smaSlow

	def getEMAFast(self):
		return self.__signal.emaFast

	def getEMASlow(self):
		return self.__signal.emaSlow

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
		self.__signal.bar = bars[self.__instrument]

		# If a position was not opened, check if we should enter a long position.
		if self.__position is None:
			if self.__signal.enterLongSignal():
				shares = self._truncFloat(float(self.getBroker().getCash() * 0.99 / bars[self.__instrument].getPrice()), huobiapi.PRECISION)
				 # Enter a buy market order. The order is good till canceled.
				self.__position = self.enterLong(self.__instrument, shares, True)
		# Check if we have to exit the position.
		elif not self.__position.exitActive():
			if self.__signal.exitLongSignal():
				self.__position.exitMarket()