from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma
import mybasestrategy
import myfeed
import huobiapi

class MySimpleStrategy(mybasestrategy.MyBaseStrategy):
    def __init__(self, feed, instrument, smaPeriod):
        super(MySimpleStrategy, self).__init__(feed, 1000000)
        self.__position = None
        self.__instrument = instrument
        # We'll use adjusted close values instead of regular close values.
        self.setUseAdjustedValues(False)
        self.__sma = ma.SMA(feed[instrument].getPriceDataSeries(), smaPeriod)

    def setPosition(self, position):
        self.__position = position

    def getPosition(self):
        return self.__position

    def enterLongSignal(self, bar):
        return bar.getPrice() > self.__sma[-1]

    def exitLongSignal(self, bar):
        return bar.getPrice() < self.__sma[-1] and not self.__position.exitActive()

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate a SMA.
        if self.__sma[-1] is None:
            return 

        bar = bars[self.__instrument]
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if self.enterLongSignal(bar):
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, 10, True)
        # Check if we have to exit the position.
        elif self.exitLongSignal(bar):
            self.__position.exitMarket()

def run_strategy(smaPeriod):
    # Load the huobi feed as json
    huobi = huobiapi.DataApi()
    kline = huobi.getKline(huobiapi.SYMBOL_BTCCNY, '100', 300)
    feed = myfeed.Feed()
    feed.addBarsFromJson("btc", kline)

    # Evaluate the strategy with the feed.
    mySimpleStrategy = MySimpleStrategy(feed, "btc", smaPeriod)
    mySimpleStrategy.run()
    print "Final portfolio value: $%.2f" % mySimpleStrategy.getBroker().getEquity()

for i in range(10, 30):
    run_strategy(i)