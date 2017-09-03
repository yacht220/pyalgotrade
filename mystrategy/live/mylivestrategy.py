from mystrategy.live import mylivefeed
from mystrategy.live import mylivebroker
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade.technical import macd
from mystrategy.common import mysignal
from mystrategy import common
#from mystrategy.backtesting import mybroker
#from pyalgotrade.broker import backtesting
import pdb
import math

class Strategy(strategy.BaseStrategy):
    def __init__(self, feed, brk, signal, smaPeriodFast = None, smaPeriodSlow = None, 
                 emaPeriodFast = None, emaPeriodSlow = None, emaPeriodSignal = None):
        super(Strategy, self).__init__(feed, brk)
        self.__instrument = common.ltc_symbol
        self.__prices = feed[self.__instrument].getCloseDataSeries()
        if smaPeriodFast is not None:
            self.__smaFast = ma.SMA(self.__prices, smaPeriodFast)
        else:
            self.__smaFast = None

        if smaPeriodSlow is not None:
            self.__smaSlow = ma.SMA(self.__prices, smaPeriodSlow)
        else:
            self.__smaSlow = None

        if emaPeriodFast is not None:
            self.__emaFast = ma.EMA(self.__prices, emaPeriodFast)
        else:
            self.__emaFast = None

        if emaPeriodSlow is not None:
            self.__emaSlow = ma.EMA(self.__prices, emaPeriodSlow)
        else:
            self.__emaSlow = None

        if emaPeriodFast is not None and emaPeriodSlow is not None and emaPeriodSignal is not None:
            self.__macd = macd.MACD(self.__prices, emaPeriodFast, emaPeriodSlow, emaPeriodSignal)
        else:
            self.__macd = None

        self.__bid = None
        self.__ask = None
        self.__position = None
        self.__posSize = 0.05
        #self.__filledBuyPrice = None
        #self.__filledSellPrice = None
        self.__signal = signal

        # Subscribe to order book update events to get bid/ask prices to trade.
        #feed.getOrderBookUpdateEvent().subscribe(self.__onOrderBookUpdate)

    def _truncFloat(self, floatvalue, decnum):
        tmp = int('1' + '0' * decnum)
        return float(int(floatvalue * tmp)) / float(tmp)

    def _getOrderBookUpdate(self):
        bid, ask = self.getFeed().getOrderBookUpdate()

        self.__bid = bid 
        self.__ask = ask
        self.info("Order book updated. Best bid: %s. Best ask: %s" % (self.__bid, self.__ask))

    def onEnterOk(self, position):
        filledPrice = position.getEntryOrder().getExecutionInfo().getPrice()
        #self.info("Current portfolio value $%.2f" % (self.getBroker().getEquity()))
        self.info("Position opened at %s" % filledPrice) 

    def onEnterCanceled(self, position):
        self.info("Position entry canceled")
        self.__position = None

    def onExitOk(self, position):
        self.__position = None
        filledPrice = position.getExitOrder().getExecutionInfo().getPrice()
        self.info("Position closed at %s" % filledPrice)

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
        if self.getFeed().getInit() is True:
            self.info("Bar feed is in init")
            return

        self._getOrderBookUpdate()
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
            if self.__signal.enterLongSignal(self.__prices, bar, self.__smaFast, self.__smaSlow, self.__emaFast, self.__emaSlow, self.__macd):
                #self.__buyPrice = bar.getClose()
                shares = self._truncFloat(float(self.getBroker().getCash() * 1.00 / self.__ask), 4)
                self.info("Entry signal. Buy %s shares at %s CNY" % (shares, self.__ask))
                # Enter a buy market order. The order is good till canceled.
                #self.__position = self.enterLong(self.__instrument, shares, True)
                self.__position = self.enterLongLimit(self.__instrument, self.__ask, shares, True)
        # Check if we have to exit the position.
        elif not self.__position.exitActive():
            if self.__signal.exitLongSignal(self.__prices, bar, self.__smaFast, self.__smaSlow, self.__emaFast, self.__emaSlow, self.__macd):
                #self.__sellPrice = bar.getClose()
                self.info("Exit signal. Sell at %s CNY" % (self.__bid))
                #self.__position.exitMarket()

                # Actual position shares should be obtained from account info
                # since commission would be subtracted from filled quantity in previous buy order.
                self.__position.setShares(self.getBroker().getShares(self.__instrument))
                self.__position.exitLimit(self.__bid)

def main():
    barFeed = mylivefeed.LiveTradeFeed()
    brk = mylivebroker.MyLiveBroker()
    signal = mysignal.MySmaCrossOverUpDownSignal()
    strat = Strategy(barFeed, brk, signal, 12, 26)
    
    strat.run()

if __name__ == "__main__":
    main()
