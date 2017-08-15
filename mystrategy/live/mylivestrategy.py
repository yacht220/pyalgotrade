from mystrategy.live import mylivefeed
from mystrategy.live import mylivebroker
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from mystrategy.backtesting import mysignal
#from mystrategy.backtesting import mybroker
#from pyalgotrade.broker import backtesting
import pdb


class Strategy(strategy.BaseStrategy):
    def __init__(self, feed, brk, signal):
        super(Strategy, self).__init__(feed, brk)
        smaPeriodFast = 3
        smaPeriodSlow = 5
        self.__instrument = "BTC"
        self.__prices = feed[self.__instrument].getCloseDataSeries()
        self.__smaFast = ma.SMA(self.__prices, smaPeriodFast)
        self.__smaSlow = ma.SMA(self.__prices, smaPeriodSlow)
        self.__bid = None
        self.__ask = None
        self.__position = None
        self.__posSize = 0.05
        self.__buyPrice = None
        self.__sellPrice = None
        self.__signal = signal

        # Subscribe to order book update events to get bid/ask prices to trade.
        #feed.getOrderBookUpdateEvent().subscribe(self.__onOrderBookUpdate)

    '''def __onOrderBookUpdate(self, orderBookUpdate):
        bid = orderBookUpdate.getBidPrices()[0]
        ask = orderBookUpdate.getAskPrices()[0]

        if bid != self.__bid or ask != self.__ask:
            self.__bid = bid
            self.__ask = ask
            #self.info("Order book updated. Best bid: %s. Best ask: %s" % (self.__bid, self.__ask))'''

    def onEnterOk(self, position):
        self.__buyPrice = position.getEntryOrder().getExecutionInfo().getPrice()
        #self.info("Current portfolio value $%.2f" % (self.getBroker().getEquity()))
        self.info("Position opened at %s" % self.__buyPrice)

    def onEnterCanceled(self, position):
        self.info("Position entry canceled")
        self.__position = None

    def onExitOk(self, position):
        self.__position = None
        self.__sellPrice = position.getExitOrder().getExecutionInfo().getPrice()
        self.info("Position closed at %s" % self.__sellPrice)

    def onExitCanceled(self, position):
        self.info("Position exit canceled")
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        #pdb.set_trace()
        self.info("Current portfolio value %.2f CNY" % self.getResult())

        '''if self.__smaFast[-1] is None:
            return 
        elif self.__smaSlow is not None and self.__smaSlow[-1] is None:
            return'''

        bar = bars[self.__instrument]
        self.info("Time: %s. Price: %s. Volume: %s." % (bar.getDateTime(), bar.getClose(), bar.getVolume()))
        '''for i in self.__prices:
            print "prices %s" % i

        for j in self.__smafast:
            print "smafast %s" % j

        for k in self.__smaslow:
            print "smaslow %s" % k'''

        # Wait until we get the current bid/ask prices.
        '''if self.__ask is None:
            return'''

        # If a position was not opened, check if we should enter a long position.
        '''if self.__position is None:
            if cross.cross_above(self.__smafast, self.__smaslow) > 0:
                self.info("Entry signal. Buy at %s" % (self.__ask))
                self.__position = self.enterLongLimit(self.__instrument, self.__ask, self.__posSize, True)
                #self.info("Current portfolio value $%.2f" % (self.getBroker().getEquity()))
        # Check if we have to close the position.
        elif not self.__position.exitActive() and cross.cross_below(self.__smafast, self.__smaslow) > 0:
            self.info("Exit signal. Sell at %s" % (self.__bid))
            self.__position.exitLimit(self.__bid)
            #self.info("Current portfolio value $%.2f" % (self.getBroker().getEquity()))'''

        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if self.__signal.enterLongSignal(self.__prices, bar, self.__smaFast, self.__smaSlow):
                self.__buyPrice = bar.getClose()
                shares = float(self.getBroker().getCash() * 0.9 / self.__buyPrice)
                self.info("Entry signal. Buy %s shares at %s CNY" % (shares, self.__buyPrice))
                # Enter a buy market order. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, self.__buyPrice, shares, True)
        # Check if we have to exit the position.
        elif not self.__position.exitActive():
            if self.__signal.exitLongSignal(self.__prices, bar, self.__smaFast, self.__smaSlow):
                self.__sellPrice = bar.getClose()
                self.info("Exit signal. Sell at %s CNY" % (self.__sellPrice))
                self.__position.exitMarket()

def main():
    barFeed = mylivefeed.LiveTradeFeed()
    brk = mytestbroker.PaperTradingBroker(10000, barFeed, 0.002)
    #commission = backtesting.TradePercentage(0.002)
    #brk = mybroker.MyBroker(10000, barFeed, commission)
    signal = mysignal.MySmaCrossOverUpDownSignal()
    strat = Strategy(barFeed, brk, signal)
    
    strat.run()

if __name__ == "__main__":
    main()
