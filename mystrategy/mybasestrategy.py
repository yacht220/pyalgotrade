from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade.broker import backtesting
import mybroker

class MyBaseStrategy(strategy.BacktestingStrategy):
    def __init__(self, barFeed, cash_or_brk = None):
        if cash_or_brk is not None:
            super(MyBaseStrategy, self).__init__(barFeed, cash_or_brk)
        else:
            super(MyBaseStrategy, self).__init__(barFeed, cash_or_brk)

    def setPosition(self, position):
        raise NotImplementedError()

    def getPosition(self):
        raise NotImplementedError()

    def onEnterOk(self, position):        
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at $%.2f" % (execInfo.getPrice()))

    def onEnterCanceled(self, position):
        self.setPosition(None)   

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.setPosition(None)

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.getPosition().exitMarket()

    def enterLongSignal(self):
        raise NotImplementedError()

    def exitLongSignal(self):
        raise NotImplementedError()

    def onBars(self, bars):
        raise NotImplementedError()