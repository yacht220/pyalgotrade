from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade.broker import backtesting
import mybroker
import mybasestrategy

class MySMAUpDown(mybasestrategy.MyBaseStrategy):
    def __init__(self, feed, instrument, smaPeriod):
        commission = backtesting.TradePercentage(0.002)
        brk = mybroker.MyBroker(10000, feed, commission)
        self.__instrument = instrument
        self.__position = None
        super(MySMAUpDown, self).__init__(feed, brk)

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

    def smaIsUp(self, period = 3):
        assert(period >= 2)
        up = True
        if self.__sma[-2] is None:
            return False
        next_ = self.__sma[-1]
        iter_ = 2
        while iter_ <= period:
            if self.__sma[-iter_] > next_:
                up = False
                break
            next_ = self.__sma[-iter_]
            iter_ += 1

        return up

    def enterLongSignal(self, bar):
        return bar.getPrice() > self.__sma[-1] and self.smaIsUp()

    def exitLongSignal(self, bar):
        return not self.__position.exitActive() and bar.getPrice() < self.__sma[-1]
    
    def onBars(self, bars):
        # Wait for enough bars to be available to calculate a SMA.
        if self.__sma[-1] is None:
            return 

        bar = bars[self.__instrument]

        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if self.enterLongSignal(bar):
                shares = float(self.getBroker().getCash() * 0.99 / bars[self.__instrument].getPrice())
                 # Enter a buy market order. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, shares, True)
        # Check if we have to exit the position.
        elif self.exitLongSignal(bar):
            self.__position.exitMarket()