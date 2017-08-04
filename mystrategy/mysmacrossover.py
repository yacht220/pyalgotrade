from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade.broker import backtesting
import mybroker
import mybasestrategy

class MySMACrossOver(mybasestrategy.MyBaseStrategy):
    def __init__(self, feed, instrument, smaPeriod):
        commission = backtesting.TradePercentage(0.002)
        brk = mybroker.MyBroker(10000, feed, commission)
        self.__instrument = instrument
        self.__position = None
        super(MySMACrossOver, self).__init__(feed, brk)

        # We'll use adjusted close values instead of regular close values.
        self.setUseAdjustedValues(False)
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__sma = ma.SMA(self.__prices, smaPeriod)

    def setPosition(self, position):
        self.__position = position

    def getPosition(self):
        return self.__position

    def getSMA(self):
        return self.__sma 

    def enterLongSignal(self):
        return cross.cross_above(self.__prices, self.__sma) > 0

    def exitLongSignal(self):
        return not self.__position.exitActive() and cross.cross_below(self.__prices, self.__sma) > 0

    def onBars(self, bars):
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if self.enterLongSignal():
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                 # Enter a buy market order. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, shares, True)
        # Check if we have to exit the position.
        elif self.exitLongSignal():
            self.__position.exitMarket()