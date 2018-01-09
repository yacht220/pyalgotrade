from pyalgotrade.technical import cross
from mystrategy.common import mylogger

mysignallogger = mylogger.getMyLogger("mysingal")

def isUp(line, period = 2):
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

def isDown(line, period = 2):
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

def bigGradient(line, up):
    ratio = (float(line[-1]) - float(line[-2])) / float(line[-2])
    mysignallogger.info("ratio is %s" % ratio)
    if up is True:
        return ratio >= 0.002
    else:
        return ratio <= -0.002

def isOver(lineA, lineB, period = 1):
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

def isBelow(lineA, lineB, period = 1):
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

def isClose(lineA, lineB, period = 2):
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

def isAway(lineA, lineB, period = 2):
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


class MyPriceSmaCrossOverSignal(object):
	def __init__(self):
		pass

	def enterLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
		return cross.cross_above(prices, smaFast) > 0

	def exitLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
		return cross.cross_below(prices, smaFast) > 0

class MyPriceSmaUpDownSignal(object):
    def __init__(self):
        pass

    def enterLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
        if smaFast is None or smaFast[-1] is None or smaSlow is None or smaSlow[-1] is None:
            return False

        return smaFast[-1] > smaSlow[-1] and isUp(smaFast, 2) and isUp(smaSlow, 2)

    def exitLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
        if smaFast is None or smaFast[-1] is None:
            return False

        return bar.getPrice() < smaFast[-1] and isDown(smaFast, 2)

class MySmaCrossOverUpDownSignal(object):
    def __init__(self):
        pass

    def enterLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
        if smaFast is None or smaFast[-1] is None or smaSlow is None or smaSlow[-1] is None:
            return False

        return isOver(smaFast, smaSlow, 1) and isUp(smaFast, 2) and isUp(smaSlow, 2)

    def exitLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
        if smaFast is None or smaFast[-1] is None or smaSlow is None or smaSlow[-1] is None:
            return False
        
        return isBelow(smaFast, smaSlow, 1)#cross.cross_below(smaFast, smaSlow) > 0# or isDown(smaFast, 5)

class MyQuickAdvanceAndDeclineSignal(object):
    def __init__(self):
        pass

    def enterLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
        if len(prices) <= 1:
            return False
        
        advance = (prices[-1] - prices[-2]) / prices[-2]
        mysignallogger.info("Advance %s" % advance)

        if advance >= 0.02:
            return True

        return False

    def exitLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
        if len(prices) <= 1:
            return False

        decline = (prices[-2] - prices[-1]) / prices[-2]
        mysignallogger.info("Decline %s" % decline)

        if decline >= 0.02:
            return True

        return False

class MySmaUpAndDownSignal(object):
    def __init__(self):
        pass

    def enterLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
        if smaFast is None or smaFast[-1] is None:
            return False

        return smaIsUp(smaFast, 2)

    def exitLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
        if smaFast is None or smaFast[-1] is None:
            return False

        return smaIsDown(smaFast, 2)

class MyMacdCrossOverUpDownSignal(object):
    def __init__(self):
        pass

    def enterLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
        if macd is None or macd[-1] is None or macd.getSignal() is None or macd.getSignal()[-1] is None:
            return False
            
        return macd[-1] > macd.getSignal()[-1] > 0 and isUp(macd) and isUp(macd.getSignal())

    def exitLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
        if macd is None or macd[-1] is None or macd.getSignal() is None or macd.getSignal()[-1] is None:
            return False

        return cross.cross_below(macd, macd.getSignal()) > 0

class MyEmaCrossOverUpDownSignal(object):
    def __init__(self):
        pass

    def enterLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
        if emaFast is None or emaFast[-1] is None or emaSlow is None or emaSlow[-1] is None:
            return False

        return isOver(emaFast, emaSlow, 1) and isUp(emaFast, 2) and isUp(emaSlow, 2)

    def exitLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
        if emaFast is None or emaFast[-1] is None or emaSlow is None or emaSlow[-1] is None:
            return False
        return isBelow(emaFast, emaSlow, 1)#cross.cross_below(emaFast, emaSlow) > 0
        #return emaFast[-1] < emaSlow[-1] and smaIsDown(emaFast, 2) and smaIsDown(emaSlow, 2)

class MySmaCrossOverUpDownSignalStopLossStopProfit(object):
    def __init__(self):
        self.__priceStop = False
        self.__buyPrice = None
        self.__highest = 0

    def enterLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
        if len(prices) <= 1 or smaFast is None or smaFast[-1] is None or smaSlow is None or smaSlow[-1] is None:
            return False

        if self.__priceStop is True and isBelow(smaFast, smaSlow, 1):
            self.__priceStop = False
        if self.__priceStop is False and isOver(smaFast, smaSlow, 1) and isUp(smaFast, 2) and isUp(smaSlow, 2):
            self.__buyPrice = prices[-1]
            self.__highest = 0
            return True

    def exitLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
        if len(prices) <= 1 or smaFast is None or smaFast[-1] is None or smaSlow is None or smaSlow[-1] is None:
            return False
        
        if self.__highest < bar.getHigh():
            self.__highest = bar.getHigh()
        if isBelow(smaFast, smaSlow, 1):
            return True
        elif self.__buyPrice > prices[-1]:
            d = (self.__highest - prices[-1]) / self.__highest 
            if d >= 0.035:
                self.__priceStop = True
                return True
        elif self.__buyPrice < prices[-1]:
            d = (prices[-1] - self.__buyPrice) / self.__buyPrice
            if d >= 0.025:
                self.__priceStop = True
                return True
        else:
            return False