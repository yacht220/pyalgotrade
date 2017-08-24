from pyalgotrade.technical import cross

def smaIsUp(sma, period = 3):
    assert(period >= 2)
    up = True
    if sma[-2] is None:
        return False
    next_ = sma[-1]
    iter_ = 2
    while iter_ <= period:
        if sma[-iter_] > next_:
            up = False
            break
        next_ = sma[-iter_]
        iter_ += 1

        return up

class MyPriceSmaCrossOverSignal(object):
	def __init__(self):
		pass

	def enterLongSignal(self, prices, bar, smaFast, smaSlow):
		return cross.cross_above(prices, smaFast) > 0

	def exitLongSignal(self, prices, bar, smaFast, smaSlow):
		return cross.cross_below(prices, smaFast) > 0

class MyPriceSmaUpDownSignal(object):
    def __init__(self):
        pass

    def enterLongSignal(self, prices, bar, smaFast, smaSlow):
        return bar.getPrice() > smaFast[-1] and smaIsUp(smaFast)

    def exitLongSignal(self, prices, bar, smaFast, smaSlow):
        return bar.getPrice() < smaFast[-1]

class MySmaCrossOverUpDownSignal(object):
    def __init__(self):
        pass

    def enterLongSignal(self, prices, bar, smaFast, smaSlow):
        if smaFast is None or smaFast[-1] is None or smaSlow is None or smaSlow[-1] is None:
            return False
        return smaFast[-1] > smaSlow[-1] and smaIsUp(smaFast) and smaIsUp(smaSlow)

    def exitLongSignal(self, prices, bar, smaFast, smaSlow):
        if smaFast is None or smaFast[-1] is None or smaSlow is None or smaSlow[-1] is None:
            return False
        return cross.cross_below(smaFast, smaSlow) > 0