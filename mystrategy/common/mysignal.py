import abc
from pyalgotrade.technical import cross
from mystrategy.common import mylogger

mysignallogger = mylogger.getMyLogger("mysingal")

class MyBaseSignal(object):
    def __init__(self):
        # All data series (price, sma, ema, macd, etc.) should be in time sequence order (from past to current in data[0:-1])
        self.prices = None
        self.bar = None
        self.smaFast = None
        self.smaSlow = None
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

    @abc.abstractmethod
    def enterLongSignal(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def exitLongSignal(self):
        raise NotImplementedError()

class MyPriceSmaCrossOverSignal(MyBaseSignal):
    def __init__(self):
        pass

    def enterLongSignal(self):
        return cross.cross_above(self.prices, self.smaFast) > 0

    def exitLongSignal(self):
        return cross.cross_below(self.prices, self.smaFast) > 0

class MyPriceSmaUpDownSignal(MyBaseSignal):
    def __init__(self):
        pass

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
        pass

    def enterLongSignal(self):
        if self.smaFast is None or self.smaFast[-1] is None or self.smaSlow is None or self.smaSlow[-1] is None:
            return False

        return self.isOver(self.smaFast, self.smaSlow, 1) and self.isUp(self.smaFast, 2) and self.isUp(self.smaSlow, 2)

    def exitLongSignal(self):
        if self.smaFast is None or self.smaFast[-1] is None or self.smaSlow is None or self.smaSlow[-1] is None:
            return False
        
        return self.isBelow(self.smaFast, self.smaSlow, 1)#cross.cross_below(self.smaFast, self.smaSlow) > 0# or self.isDown(self.smaFast, 5)

class MyQuickAdvanceAndDeclineSignal(MyBaseSignal):
    def __init__(self):
        pass

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
        pass

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
        pass

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
        pass

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
    def __init__(self):
        self.__priceStop = False
        self.__buyPrice = None
        self.__highest = 0

    def enterLongSignal(self):
        if len(self.prices) <= 1 or self.smaFast is None or self.smaFast[-1] is None or self.smaSlow is None or self.smaSlow[-1] is None:
            return False

        if self.__priceStop is True and self.isBelow(self.smaFast, self.smaSlow, 1):
            self.__priceStop = False
        if self.__priceStop is False and self.isOver(self.smaFast, self.smaSlow, 1) and self.isUp(self.smaFast, 2) and self.isUp(self.smaSlow, 2):
            self.__buyPrice = self.prices[-1]
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
            if d >= 0.035:
                self.__priceStop = True
                return True
        elif self.__buyPrice < self.prices[-1]:
            d = (self.prices[-1] - self.__buyPrice) / self.__buyPrice
            if d >= 0.025:
                self.__priceStop = True
                return True
        else:
            return False