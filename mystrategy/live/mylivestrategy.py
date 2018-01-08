from mystrategy.live import mylivefeed
from mystrategy.live import mylivebroker
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade.technical import macd
from mystrategy.common import mysignal
from mystrategy import common
from mystrategy.common import myemail
from mystrategy.huobi import huobiapi
import pdb
import math

class MyLiveStrategy(strategy.BaseStrategy):
    def __init__(self, feed, brk, signal, smaPeriodFast = None, smaPeriodSlow = None, 
                 emaPeriodFast = None, emaPeriodSlow = None, emaPeriodSignal = None):
        super(MyLiveStrategy, self).__init__(feed, brk)
        self.__instrument = huobiapi.INSTRUMENT_SYMBOL
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
        self.__signal = signal

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
        self.info("Position opened at %s %s" % (filledPric, huobiapi.CURRENCY_SYMBOL)) 
        myemail.sendEmail("Position opened at %s %s" % (filledPrice, huobiapi.CURRENCY_SYMBOL))

    def onEnterCanceled(self, position):
        self.info("Position entry canceled")
        self.__position = None
        myemail.sendEmail("Position entry canceled")

    def onExitOk(self, position):
        self.__position = None
        filledPrice = position.getExitOrder().getExecutionInfo().getPrice()
        self.info("Position closed at %s %s" % (filledPrice, huobiapi.CURRENCY_SYMBOL))
        myemail.sendEmail("Position closed at %s %s" %(filledPrice, huobiapi.CURRENCY_SYMBOL))

    def onExitCanceled(self, position):
        self.info("Position exit canceled")
        # If the exit was canceled, re-submit it.
        self.__position.exitLimit(self.__bid)
        myemail.sendEmail("Position exit canceled")

    def onBars(self, bars):
        #pdb.set_trace()
        bar = bars[self.__instrument]
        self.info("Time: %s. Price: %s. Volume: %s." % (bar.getDateTime(), bar.getClose(), bar.getVolume()))
        if self.getFeed().getInit() is True:
            self.info("Bar feed is in init")
            return

        myemail.sendEmail("Everything is OK, current price %s %s" % (bar.getClose(), huobiapi.CURRENCY_SYMBOL))

        self.getBroker().refreshAccountBalance()
        #self.info("Current portfolio value %.2f CNY" % self.getResult())
        self._getOrderBookUpdate()

        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if common.skipBuy is True or self.__signal.enterLongSignal(self.__prices, bar, self.__smaFast, self.__smaSlow, self.__emaFast, self.__emaSlow, self.__macd):
                shares = self._truncFloat(float(self.getBroker().getCash() * 1.00 / self.__ask), huobiapi.PRECISION)
                if common.skipBuy is True:
                    shares = self._truncFloat(self.getBroker().getShares(self.__instrument), huobiapi.PRECISION)
                    common.fakeShares = shares
                self.info("Entry signal. Buy %s shares at %s %s" % (shares, self.__ask, huobiapi.CURRENCY_SYMBOL))
                self.__position = self.enterLongLimit(self.__instrument, self.__ask, shares, True)
                myemail.sendEmail("Entry signal")
        # Check if we have to exit the position.
        elif not self.__position.exitActive():
            if self.__signal.exitLongSignal(self.__prices, bar, self.__smaFast, self.__smaSlow, self.__emaFast, self.__emaSlow, self.__macd):
                # Actual position shares should be obtained from account info
                # since commission would be subtracted from filled quantity in previous buy order.
                self.__position.setShares(self._truncFloat(self.getBroker().getShares(self.__instrument), huobiapi.PRECISION))
                self.info("Exit signal. Sell %s shares at %s %s" % (self.__position.getShares(), self.__bid, huobiapi.CURRENCY_SYMBOL))
                self.__position.exitLimit(self.__bid)
                myemail.sendEmail("Exit signal")
                common.skipBuy = False

def main():
    common.isBacktesting = False
    barFeed = mylivefeed.LiveTradeFeed()
    brk = mylivebroker.MyLiveBroker()
    signal = mysignal.MySmaCrossOverUpDownSignal()
    strat = MyLiveStrategy(barFeed, brk, signal, 48, 96)
    
    strat.run()

if __name__ == "__main__":
    main()
