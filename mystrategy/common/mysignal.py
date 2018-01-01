from pyalgotrade.technical import cross
from mystrategy.common import mylogger

mysignallogger = mylogger.getMyLogger("mysingal")

def isUp(sma, period = 2):
    assert(period >= 2)
    up = True
    if sma[-period] is None:
        return False
    next_ = sma[-1]
    iter_ = 2
    while iter_ <= period:
        if sma[-iter_] >= next_:
            up = False
            break
        next_ = sma[-iter_]
        iter_ += 1

    return up

def isDown(sma, period = 2):
    assert(period >= 2)
    down = True
    if sma[-period] is None:
        return False

    next_ = sma[-1]
    iter_ = 2
    while iter_ <= period:
        if sma[-iter_] <= next_:
            down = False
            break
        next_ = sma[-iter_]
        iter_ += 1

    return down

def bigGradient(sma, up):
    ratio = (float(sma[-1]) - float(sma[-2])) / float(sma[-2])
    mysignallogger.info("ratio is %s" % ratio)
    if up is True:
        return ratio >= 0.002
    else:
        return ratio <= -0.002

def priceOver(smaFast, smaSlow, period = 1):
    assert(period >= 1)
    over = True
    if smaFast[-period] is None or smaSlow[-period] is None:
        return False

    iter_ = 1
    while iter_ <= period:
        if smaFast[-iter_] <= smaSlow[-iter_]:
            over = False
            break
        iter_ += 1

    return over

def priceBelow(smaFast, smaSlow, period = 1):
    assert(period >= 1)
    below = True
    if smaFast[-period] is None or smaSlow[-period] is None:
        return False

    iter_ = 1
    while iter_ <= period:
        if smaFast[-iter_] >= smaSlow[-iter_]:
            below = False
            break
        iter_ += 1

    return below

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

        return priceOver(smaFast, smaSlow, 1) and isUp(smaFast, 2) and isUp(smaSlow, 2)

    def exitLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
        if smaFast is None or smaFast[-1] is None or smaSlow is None or smaSlow[-1] is None:
            return False
        return priceBelow(smaFast, smaSlow, 1)#cross.cross_below(smaFast, smaSlow) > 0# or isDown(smaFast, 5)

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

        return emaFast[-1] > emaSlow[-1] and isUp(emaFast, 3) and isUp(emaSlow, 3)

    def exitLongSignal(self, prices, bar, smaFast, smaSlow, emaFast, emaSlow, macd):
        if emaFast is None or emaFast[-1] is None or emaSlow is None or emaSlow[-1] is None:
            return False
        return cross.cross_below(emaFast, emaSlow) > 0
        #return emaFast[-1] < emaSlow[-1] and smaIsDown(emaFast, 2) and smaIsDown(emaSlow, 2)
