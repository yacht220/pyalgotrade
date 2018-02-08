import abc
from pyalgotrade.technical import cross
from mystrategy.common import mylogger
from mystrategy import common

mysignallogger = mylogger.getMyLogger("mysingal")

class MyBaseSignal(object):
    def __init__(self):
        # All data series (price, sma, ema, macd, etc.) should be in time sequence order (from past to current in data[0:-1])
        self.prices = None
        self.bar = None
        self.smaFast = None
        self.smaSlow = None
        self.smaA = None
        self.smaB = None
        self.smaC = None
        self.emaFast = None
        self.emaSlow = None
        self.macd = None

    def isUp(self, line, period = 2):
        assert(period >= 2)
        up = True
        if line[-period] is None:
            return False
        next_ = line[-1]
        iter_ = 2
        while iter_ <= period:
            if line[-iter_] >= next_:
                up = False
                break
            next_ = line[-iter_]
            iter_ += 1

        return up

    def isDown(self, line, period = 2):
        assert(period >= 2)
        down = True
        if line[-period] is None:
            return False

        next_ = line[-1]
        iter_ = 2
        while iter_ <= period:
            if line[-iter_] <= next_:
                down = False
                break
            next_ = line[-iter_]
            iter_ += 1

        return down

    def bigGradient(self, line, up):
        ratio = (float(line[-1]) - float(line[-2])) / float(line[-2])
        mysignallogger.info("ratio is %s" % ratio)
        if up is True:
            return ratio >= 0.002
        else:
            return ratio <= -0.002

    def isOver(self, lineA, lineB, period = 1):
        assert(period >= 1)
        over = True
        if lineA[-period] is None or lineB[-period] is None:
            return False

        iter_ = 1
        while iter_ <= period:
            if lineA[-iter_] <= lineB[-iter_]:
                over = False
                break
            iter_ += 1

        return over

    def isBelow(self, lineA, lineB, period = 1):
        assert(period >= 1)
        below = True
        if lineA[-period] is None or lineB[-period] is None:
            return False

        iter_ = 1
        while iter_ <= period:
            if lineA[-iter_] >= lineB[-iter_]:
                below = False
                break
            iter_ += 1

        return below

    def isClose(self, lineA, lineB, period = 2):
        assert(period >= 2)
        if lineA[-period] is None or lineB[-period] is None:
            return False

        diffPrev = None
        iter_ = 1
        while iter_ <= period:
            diffCur = abs(lineA[-iter_] - lineB[-iter_])
            if diffPrev != None and diffCur >= diffPrev:
                return False
            diffPrev = diffCur
            iter_ += 1

        return True

    def isAway(self, lineA, lineB, period = 2):
        assert(period >= 2)
        if lineA[-period] is None or lineB[-period] is None:
            return False

        diffPrev = None
        iter_ = 1
        while iter_ <= period:
            diffCur = abs(lineA[-iter_] - lineB[-iter_])
            if diffPrev != None and diffCur <= diffPrev:
                return False
            diffPrev = diffCur
            iter_ += 1

        return True

    def setBuyPrice(self, price):
        pass

    def setSellPrice(self, price):
        pass
    
    @abc.abstractmethod
    def enterLongSignal(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def exitLongSignal(self):
        raise NotImplementedError()

    def enterShortSignal(self):
        return False

    def exitShortSignal(self):
        return False

class MyPriceSmaCrossOverSignal(MyBaseSignal):
    def __init__(self):
        super(MyPriceSmaCrossOverSignal, self).__init__()

    def enterLongSignal(self):
        return cross.cross_above(self.prices, self.smaFast) > 0

    def exitLongSignal(self):
        return cross.cross_below(self.prices, self.smaFast) > 0

class MyPriceSmaUpDownSignal(MyBaseSignal):
    def __init__(self):
        super(MyPriceSmaUpDownSignal, self).__init__()

    def enterLongSignal(self):
        if self.smaFast is None or self.smaFast[-1] is None or self.smaSlow is None or self.smaSlow[-1] is None:
            return False

        return self.smaFast[-1] > self.smaSlow[-1] and self.isUp(self.smaFast, 2) and self.isUp(self.smaSlow, 2)

    def exitLongSignal(self):
        if self.smaFast is None or self.smaFast[-1] is None:
            return False

        return self.bar.getPrice() < self.smaFast[-1] and self.isDown(self.smaFast, 2)

class MySmaCrossOverUpDownSignal(MyBaseSignal):
    def __init__(self):
        super(MySmaCrossOverUpDownSignal, self).__init__()

    def enterLongSignal(self):
        if self.smaFast is None or self.smaFast[-1] is None or self.smaSlow is None or self.smaSlow[-1] is None:
            return False

        return self.isOver(self.smaFast, self.smaSlow, 1) and self.isUp(self.smaFast, 2) and self.isUp(self.smaSlow, 2)

    def exitLongSignal(self):
        if self.smaFast is None or self.smaFast[-1] is None or self.smaSlow is None or self.smaSlow[-1] is None:
            return False
        
        return self.isBelow(self.smaFast, self.smaSlow, 1)# or self.isDown(self.smaFast, 2) and self.isDown(self.smaSlow, 2) #cross.cross_below(self.smaFast, self.smaSlow) > 0

class MyQuickAdvanceAndDeclineSignal(MyBaseSignal):
    def __init__(self):
        super(MyQuickAdvanceAndDeclineSignal, self).__init__()

    def enterLongSignal(self):
        if len(self.prices) <= 1:
            return False
        
        advance = (self.prices[-1] - self.prices[-2]) / self.prices[-2]
        mysignallogger.info("Advance %s" % advance)

        if advance >= 0.02:
            return True

        return False

    def exitLongSignal(self):
        if len(self.prices) <= 1:
            return False

        decline = (self.prices[-2] - self.prices[-1]) / self.prices[-2]
        mysignallogger.info("Decline %s" % decline)

        if decline >= 0.02:
            return True

        return False

class MySmaUpAndDownSignal(MyBaseSignal):
    def __init__(self):
        super(MySmaUpAndDownSignal, self).__init__()

    def enterLongSignal(self):
        if self.smaFast is None or self.smaFast[-1] is None:
            return False

        return self.isUp(self.smaFast, 2)

    def exitLongSignal(self):
        if self.smaFast is None or self.smaFast[-1] is None:
            return False

        return self.isDown(self.smaFast, 2)

class MyMacdCrossOverUpDownSignal(MyBaseSignal):
    def __init__(self):
        super(MyMacdCrossOverUpDownSignal, self).__init__()

    def enterLongSignal(self):
        if self.macd is None or self.macd[-1] is None or self.macd.getSignal() is None or self.macd.getSignal()[-1] is None:
            return False
            
        return self.macd[-1] > self.macd.getSignal()[-1] > 0 and self.isUp(self.macd) and self.isUp(self.macd.getSignal())

    def exitLongSignal(self):
        if self.macd is None or self.macd[-1] is None or self.macd.getSignal() is None or self.macd.getSignal()[-1] is None:
            return False

        return cross.cross_below(self.macd, self.macd.getSignal()) > 0

class MyEmaCrossOverUpDownSignal(MyBaseSignal):
    def __init__(self):
        super(MyEmaCrossOverUpDownSignal, self).__init__()

    def enterLongSignal(self):
        if self.emaFast is None or self.emaFast[-1] is None or self.emaSlow is None or self.emaSlow[-1] is None:
            return False

        return self.isOver(self.emaFast, self.emaSlow, 1) and self.isUp(self.emaFast, 2) and self.isUp(self.emaSlow, 2)

    def exitLongSignal(self):
        if self.emaFast is None or self.emaFast[-1] is None or self.emaSlow is None or self.emaSlow[-1] is None:
            return False
        return self.isBelow(self.emaFast, self.emaSlow, 1)#cross.cross_below(emaFast, emaSlow) > 0
        #return emaFast[-1] < emaSlow[-1] and smaIsDown(emaFast, 2) and smaIsDown(emaSlow, 2)

class MySmaCrossOverUpDownSignalStopLossStopProfit(MyBaseSignal):
    CONFIRM_COUNT = 0

    def __init__(self):
        super(MySmaCrossOverUpDownSignalStopLossStopProfit, self).__init__()
        self.__priceStop = False
        self.__buyPrice = None
        self.__highest = 0
        self.__confirmCount = self.CONFIRM_COUNT

    def setBuyPrice(self, price):
        assert(price is not None)
        self.__buyPrice = price

    def enterLongSignal(self):
        if len(self.prices) <= 1 or self.smaFast is None or self.smaFast[-1] is None or self.smaSlow is None or self.smaSlow[-1] is None:
            return False

        if self.__priceStop is True and self.isBelow(self.smaFast, self.smaSlow, 1):
            self.__priceStop = False
        if self.__priceStop is False and self.isOver(self.smaFast, self.smaSlow, 1) and self.isUp(self.smaFast, 2) and self.isUp(self.smaSlow, 2):
            self.__highest = 0
            return True

    def exitLongSignal(self):
        if len(self.prices) <= 1 or self.smaFast is None or self.smaFast[-1] is None or self.smaSlow is None or self.smaSlow[-1] is None:
            return False
        
        if self.__highest < self.bar.getHigh():
            self.__highest = self.bar.getHigh()

        if self.isBelow(self.smaFast, self.smaSlow, 1):
            return True
        elif self.__buyPrice > self.prices[-1]:
            d = (self.__highest - self.prices[-1]) / self.__highest 
            if d >= 0.1:
                if self.__confirmCount == 0:
                    self.__priceStop = True
                    self.__confirmCount = self.CONFIRM_COUNT
                    return True
                else:
                    self.__confirmCount -= 1
            elif self.__confirmCount != self.CONFIRM_COUNT:
                self.__confirmCount = self.CONFIRM_COUNT

        elif self.__buyPrice < self.prices[-1]:
            d = (self.prices[-1] - self.__buyPrice) / self.__buyPrice
            if d >= 0.05:
                if self.__confirmCount == 0:
                    self.__priceStop = True
                    self.__confirmCount = self.CONFIRM_COUNT
                    return True
                else:
                    self.__confirmCount -= 1
            elif self.__confirmCount != self.CONFIRM_COUNT:
                self.__confirmCount = self.CONFIRM_COUNT
        
        return False

class MyMultiSmaCrossOverUpDownSignal(MyBaseSignal):
    def __init__(self):
        super(MyMultiSmaCrossOverUpDownSignal, self).__init__()

    def enterLongSignal(self):
        if self.smaA is None or self.smaA[-1] is None or \
            self.smaB is None or self.smaB[-1] is None or \
            self.smaC is None or self.smaC[-1] is None:
            return False

        return self.isOver(self.smaA, self.smaB, 1) and \
            self.isOver(self.smaB, self.smaC, 1) and \
            self.isUp(self.smaA, 2) and \
            self.isUp(self.smaB, 2) and \
            self.isUp(self.smaC, 2)

    def exitLongSignal(self):
        if self.smaA is None or self.smaA[-1] is None or \
            self.smaB is None or self.smaB[-1] is None or \
            self.smaC is None or self.smaC[-1] is None:
            return False
        
        return self.isBelow(self.smaA, self.smaB, 1)

class MyPriceSmaDeviationSignal(MyBaseSignal):
    # Long position
    SELL_COUNT_A = 1
    SELL_COUNT_B = 1
    SELL_WAIT_BUY_COUNT = 4

    # Short position
    BUY_COUNT_A = 1
    BUY_COUNT_B = 1
    BUY_WAIT_SELL_COUNT = 4

    def __init__(self):
        # Long position
        self.__stopBuy = False
        self.__buyPrice = None
        self.__sellCountA = self.SELL_COUNT_A
        self.__sellCountB = self.SELL_COUNT_B
        self.__waitBuyCount = self.SELL_WAIT_BUY_COUNT

        # Short position
        self.__stopSell = False
        self.__sellPrice = None
        self.__buyCountA = self.BUY_COUNT_A
        self.__buyCountB = self.BUY_COUNT_B
        self.__waitSellCount = self.BUY_WAIT_SELL_COUNT

        super(MyPriceSmaDeviationSignal, self).__init__()

    def setBuyPrice(self, price):
        assert(price is not None)
        self.__buyPrice = price

    def setSellPrice(self, price):
        assert(price is not None)
        self.__sellPrice = price

    def enterLongSignal(self):
        if len(self.prices) <= 1 or self.smaFast is None or self.smaFast[-1] is None or self.smaSlow is None or self.smaSlow[-1] is None:
            return False

        if self.isBelow(self.smaFast, self.smaSlow, 1):# or self.__waitBuyCount == 0:
            self.__stopBuy = False
            self.__sellCountA = self.SELL_COUNT_A
            self.__sellCountB = self.SELL_COUNT_B
            self.__waitBuyCount = self.SELL_WAIT_BUY_COUNT
        else:
            self.__waitBuyCount -= 1

        if self.isOver(self.smaFast, self.smaSlow, 1) and \
            self.isUp(self.smaFast, 2) and \
            self.isUp(self.smaSlow, 2) and \
            "self.isOver(self.prices, self.smaFast, 1)" and \
            "self.isUp(self.prices, 2)" and \
            self.__stopBuy is False:
                d = (self.prices[-1] - self.smaFast[-1]) / self.smaFast[-1]
                if abs(d) <= 0.01:
                    return True

        return False

    def exitLongSignal(self):
        if len(self.prices) <= 1 or self.smaFast is None or self.smaFast[-1] is None or self.smaSlow is None or self.smaSlow[-1] is None:
            return False

        if self.isBelow(self.smaFast, self.smaSlow, 1):
            return True
        elif self.isBelow(self.prices, self.smaSlow, 1):# and self.__sellCountA != self.SELL_COUNT_A:
            d = (self.smaSlow[-1] - self.prices[-1]) / self.smaSlow[-1]
            if d >= 0.05:
                self.__sellCountB -= 1
                if self.__sellCountB == 0:
                    return True
        elif self.prices[-1] < self.__buyPrice:
            d = (self.__buyPrice - self.prices[-1]) / self.__buyPrice
            if d >= 0.06:
                self.__sellCountB -= 1
                if self.__sellCountB == 0:
                    return True
        elif self.prices[-1] > self.__buyPrice:
            d = (self.prices[-1] - self.__buyPrice) / self.__buyPrice
            if d >= 0.05:            
                self.__sellCountA -= 1
                if self.__sellCountA == 0:
                    self.__stopBuy = True
                return True
        elif self.isOver(self.prices, self.smaFast, 1):
            d = (self.prices[-1] - self.smaFast[-1]) / self.smaFast[-1]
            if d >= 0.1:
                self.__sellCountA -= 1
                if self.__sellCountA == 0:
                    self.__stopBuy = True
                return True

        return False

    def enterShortSignal(self):
        if len(self.prices) <= 1 or self.smaFast is None or self.smaFast[-1] is None or self.smaSlow is None or self.smaSlow[-1] is None:
            return False

        if self.isOver(self.smaFast, self.smaSlow, 1):# or self.__waitSellCount == 0:
            self.__stopSell = False
            self.__buyCountA = self.BUY_COUNT_A
            self.__buyCountB = self.BUY_COUNT_B
            self.__waitSellCount = self.BUY_WAIT_SELL_COUNT
        else:
            self.__waitSellCount -= 1

        if self.isBelow(self.smaFast, self.smaSlow, 1) and \
            self.isDown(self.smaFast, 2) and \
            self.isDown(self.smaSlow, 2) and \
            "self.isBelow(self.prices, self.smaFast, 1)" and \
            "self.isDown(self.prices, 2)" and \
            self.__stopSell is False:
                d = (self.prices[-1] - self.smaFast[-1]) / self.smaFast[-1]
                if abs(d) <= 0.01:
                    return True

        return False

    def exitShortSignal(self):
        if len(self.prices) <= 1 or self.smaFast is None or self.smaFast[-1] is None or self.smaSlow is None or self.smaSlow[-1] is None:
            return False

        if self.isOver(self.smaFast, self.smaSlow, 1):
            return True
        elif self.isOver(self.prices, self.smaSlow, 1):# and self.__buyCountA != self.BUY_COUNT_A:
            d = (self.prices[-1]) - self.smaSlow[-1] / self.smaSlow[-1]
            if d >= 0.05:
                self.__buyCountB -= 1
                if self.__buyCountB == 0:
                    return True
        elif self.prices[-1] > self.__sellPrice:
            d = (self.prices[-1] - self.__sellPrice) / self.__sellPrice
            if d >= 0.06:
                self.__buyCountB -= 1
                if self.__buyCountB == 0:
                    return True
        elif self.prices[-1] < self.__sellPrice:
            d = (self.__sellPrice - self.prices[-1]) / self.__sellPrice
            if d >= 0.05:            
                self.__buyCountA -= 1
                if self.__buyCountA == 0:
                    self.__stopSell = True
                return True
        elif self.isBelow(self.prices, self.smaFast, 1):
            d = (self.smaFast[-1] - self.prices[-1]) / self.smaFast[-1]
            if d >= 0.1:
                self.__buyCountA -= 1
                if self.__buyCountA == 0:
                    self.__stopSell = True
                return True

        return False