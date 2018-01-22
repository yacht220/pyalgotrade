from mystrategy.live import mylivefeed
from mystrategy.live import mylivebroker
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade.technical import macd
from mystrategy.common import mysignal
from mystrategy.common import myutils
from mystrategy import common
from mystrategy.common import myemail
from mystrategy.huobi import huobiapi
import pdb
import math

class MyLiveStrategy(strategy.BaseStrategy):
    def __init__(self, feed, brk, signal, smaPeriodFast = None, smaPeriodSlow = None, 
                 emaPeriodFast = None, emaPeriodSlow = None, emaPeriodSignal = None):
        super(MyLiveStrategy, self).__init__(feed, brk)
        self.__emailServer = myemail.MyEmailServer()
        self.__bid = None
        self.__ask = None
        self.__position = None
        self.__posSize = 0.05
        self.__signal = signal
        self.__instrument = huobiapi.INSTRUMENT_SYMBOL
        
        self.__signal.prices = feed[self.__instrument].getCloseDataSeries()
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
        else:
            self.__macd = None

    def _getOrderBookUpdate(self):
        bid, ask = self.getFeed().getOrderBookUpdate()

        self.__bid = bid 
        self.__ask = ask
        self.info("Order book updated. Best bid: %s. Best ask: %s" % (self.__bid, self.__ask))

    def onEnterOk(self, position):
        filledPrice = position.getEntryOrder().getExecutionInfo().getPrice()
        self.info("Position opened at %s %s" % (filledPrice, huobiapi.CURRENCY_SYMBOL)) 
        self.__emailServer.sendEmail("Position opened at %s %s" % (filledPrice, huobiapi.CURRENCY_SYMBOL))

    def onEnterCanceled(self, position):
        self.info("Position entry canceled")
        self.__position = None
        self.__emailServer.sendEmail("Position entry canceled")

    def onExitOk(self, position):
        self.__position = None
        filledPrice = position.getExitOrder().getExecutionInfo().getPrice()
        self.info("Position closed at %s %s" % (filledPrice, huobiapi.CURRENCY_SYMBOL))
        self.__emailServer.sendEmail("Position closed at %s %s" %(filledPrice, huobiapi.CURRENCY_SYMBOL))

    def onExitCanceled(self, position):
        self.info("Position exit canceled")
        # If the exit was canceled, re-submit it.
        self.__position.exitLimit(self.__bid)
        self.__emailServer.sendEmail("Position exit canceled")

    def onBars(self, bars):
        #pdb.set_trace()
        self.__signal.bar = bars[self.__instrument]
        self.info("Time: %s. Price: %s. Volume: %s." % (self.__signal.bar.getDateTime(), self.__signal.bar.getClose(), self.__signal.bar.getVolume()))
        if self.getFeed().getInit() is True:
            self.info("Bar feed is in init")
            return

        self.__emailServer.sendEmail("Everything is OK, current price %s %s" % (self.__signal.bar.getClose(), huobiapi.CURRENCY_SYMBOL))

        self.getBroker().refreshAccountBalance()
        #self.info("Current portfolio value %.2f CNY" % self.getResult())
        self._getOrderBookUpdate()

        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if common.skipBuy is True or self.__signal.enterLongSignal():
                shares = myutils.truncFloat(float(self.getBroker().getCash() * 1.00 / self.__ask), huobiapi.PRECISION)
                if common.skipBuy is True:
                    shares = myutils.truncFloat(self.getBroker().getShares(self.__instrument), huobiapi.PRECISION)
                    common.fakeShares = shares
                    self.__signal.setBuyPrice(common.buyPrice)
                else:
                    self.__signal.setBuyPrice(self.__ask)
                self.info("Entry signal. Buy %s shares at %s %s" % (shares, self.__ask, huobiapi.CURRENCY_SYMBOL))
                self.__position = self.enterLongLimit(self.__instrument, self.__ask, shares, True)
                self.__emailServer.sendEmail("Entry signal")
        # Check if we have to exit the position.
        elif not self.__position.exitActive():
            if self.__signal.exitLongSignal():
                # Actual position shares should be obtained from account info
                # since commission would be subtracted from filled quantity in previous buy order.
                self.__position.setShares(myutils.truncFloat(self.getBroker().getShares(self.__instrument), huobiapi.PRECISION))
                self.info("Exit signal. Sell %s shares at %s %s" % (self.__position.getShares(), self.__bid, huobiapi.CURRENCY_SYMBOL))
                self.__position.exitLimit(self.__bid)
                self.__emailServer.sendEmail("Exit signal")
                common.skipBuy = False

def main():
    common.isBacktesting = False
    barFeed = mylivefeed.LiveTradeFeed()
    brk = mylivebroker.MyLiveBroker()
    signal = mysignal.MyPriceSmaDeviationSignal()
    #signal = mysignal.MySmaCrossOverUpDownSignal()
    strat = MyLiveStrategy(barFeed, brk, signal, 48, 96)
    
    strat.run()

if __name__ == "__main__":
    main()
