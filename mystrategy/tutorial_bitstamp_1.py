from pyalgotrade.bitstamp import barfeed
from pyalgotrade.bitstamp import broker
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
import pdb


class Strategy(strategy.BaseStrategy):
    def __init__(self, feed, brk):
        super(Strategy, self).__init__(feed, brk)
        smaPeriodFast = 3
        smaPeriodSlow = 7
        self.__instrument = "BTC"
        self.__prices = feed[self.__instrument].getCloseDataSeries()
        self.__smafast = ma.EMA(self.__prices, smaPeriodFast)
        self.__smaslow = ma.EMA(self.__prices, smaPeriodSlow)
        self.__bid = None
        self.__ask = None
        self.__position = None
        self.__posSize = 0.05
        self.__buyPrice = None
        self.__sellPrice = None
        self.__cash = 1000

        # Subscribe to order book update events to get bid/ask prices to trade.
        feed.getOrderBookUpdateEvent().subscribe(self.__onOrderBookUpdate)

    def __onOrderBookUpdate(self, orderBookUpdate):
        bid = orderBookUpdate.getBidPrices()[0]
        ask = orderBookUpdate.getAskPrices()[0]

        if bid != self.__bid or ask != self.__ask:
            self.__bid = bid
            self.__ask = ask
            #self.info("Order book updated. Best bid: %s. Best ask: %s" % (self.__bid, self.__ask))

    def onEnterOk(self, position):
        self.__buyPrice = position.getEntryOrder().getExecutionInfo().getPrice()
        #self.info("Current portfolio value $%.2f" % (self.getBroker().getEquity()))
        self.info("Position opened at %s" % self.__buyPrice)

    def onEnterCanceled(self, position):
        #self.info("Position entry canceled")
        self.__position = None

    def onExitOk(self, position):
        self.__position = None
        self.__sellPrice = position.getExitOrder().getExecutionInfo().getPrice()
        self.info("Position closed at %s" % self.__sellPrice)
        self.__cash += self.__sellPrice - self.__buyPrice
        self.info("Current portfolio value $%.2f" % self.getBroker().getEquity())


    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitLimit(self.__bid)

    def onBars(self, bars):
        bar = bars[self.__instrument]
        #self.info("Price: %s. Volume: %s." % (bar.getClose(), bar.getVolume()))

        # Wait until we get the current bid/ask prices.
        if self.__ask is None:
            return

        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if cross.cross_above(self.__smafast, self.__smaslow) > 0:
                self.info("Entry signal. Buy at %s" % (self.__ask))
                self.__position = self.enterLongLimit(self.__instrument, self.__ask, self.__posSize, True)
                #self.info("Current portfolio value $%.2f" % (self.getBroker().getEquity()))
        # Check if we have to close the position.
        elif not self.__position.exitActive() and cross.cross_below(self.__smafast, self.__smaslow) > 0:
            self.info("Exit signal. Sell at %s" % (self.__bid))
            self.__position.exitLimit(self.__bid)
            #self.info("Current portfolio value $%.2f" % (self.getBroker().getEquity()))

def main():
    barFeed = barfeed.LiveTradeFeed()
    brk = broker.PaperTradingBroker(1000, barFeed)
    strat = Strategy(barFeed, brk)
    
    strat.run()

if __name__ == "__main__":
    main()
