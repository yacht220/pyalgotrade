# PyAlgoTrade
#
# Copyright 2011-2015 Gabriel Martin Becedillas Ruiz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>
"""

import datetime
import time

from pyalgotrade import bar
from pyalgotrade import barfeed
from pyalgotrade import observer
from mystrategy.huobi import huobiapi
from mystrategy import common
from mystrategy.common import mylogger
import pdb

mylivefeedlogger = common.mylogger.getMyLogger("mylivefeed")


class TradeBar(bar.Bar):
    # Optimization to reduce memory footprint.
    __slots__ = ('__dateTime', '__tradeId', '__price', '__amount')

    def __init__(self, dateTime, tradeJson):
        self.__dateTime = dateTime
        #self.__tradeId = trade.getId()
        self.__open = float(tradeJson['open'])
        self.__high = float(tradeJson['high'])
        self.__low = float(tradeJson['low'])
        self.__price = float(tradeJson['close'])
        self.__amount = float(tradeJson['amount'])
        #self.__buy = trade.isBuy()

    def __setstate__(self, state):
        (self.__dateTime, self.__tradeId, self.__price, self.__amount) = state

    def __getstate__(self):
        return (self.__dateTime, self.__tradeId, self.__price, self.__amount)

    def setUseAdjustedValue(self, useAdjusted):
        if useAdjusted:
            raise Exception("Adjusted close is not available")

    '''def getTradeId(self):
        return self.__tradeId'''

    def getFrequency(self):
        return bar.Frequency.TRADE

    def getDateTime(self):
        return self.__dateTime

    def getOpen(self, adjusted=False):
        return self.__open

    def getHigh(self, adjusted=False):
        return self.__high

    def getLow(self, adjusted=False):
        return self.__low

    def getClose(self, adjusted=False):
        return self.__price

    def getVolume(self):
        return self.__amount

    def getAdjClose(self):
        return None

    def getTypicalPrice(self):
        return self.__price

    def getPrice(self):
        return self.__price

    def getUseAdjValue(self):
        return False

    '''def isBuy(self):
        return self.__buy

    def isSell(self):
        return not self.__buy'''

class LiveTradeFeed(barfeed.BaseBarFeed):

    """A real-time BarFeed that builds bars from live trades.

    :param maxLen: The maximum number of values that the :class:`pyalgotrade.dataseries.bards.BarDataSeries` will hold.
        Once a bounded length is full, when new items are added, a corresponding number of items are discarded
        from the opposite end. If None then dataseries.DEFAULT_MAX_LEN is used.
    :type maxLen: int.

    .. note::
        Note that a Bar will be created for every trade, so open, high, low and close values will all be the same.
    """

    KLINE_PERIOD = '15min'

    def __init__(self, maxLen=None):
        super(LiveTradeFeed, self).__init__(bar.Frequency.MINUTE, maxLen)
        self.__barDicts = []
        self.registerInstrument(huobiapi.INSTRUMENT_SYMBOL)
        self.__prevTradeDateTime = None
        self.__stopped = False
        self.__huobidata = huobiapi.HuobiDataApi()

    def __dispatchImpl(self, eventFilter):
        # Preprocess history bar feeds
        if self.__init is True:
            mylivefeedlogger.info("Process initial bar feeds, bar index %s" % self.__barInitIndex)

            #datetime_ = self.__getTradeDateTime(self.__barInit[self.__barInitIndex][0])   
            datetime_ = datetime.datetime.fromtimestamp(self.__barInit[self.__barInitIndex]['id'])     
            barDict = {
                huobiapi.INSTRUMENT_SYMBOL: TradeBar(datetime_, self.__barInit[self.__barInitIndex])
            }
            self.__barDicts.append(barDict)
            self.__barInitIndex -= 1

            # Leave last 2 feeds unpreprocessed since they will be handled in live feed later
            if self.__barInitIndex == 1:
                self.__init = False

            return True

        bar = self.__huobidata.getKline(huobiapi.SYMBOL, LiveTradeFeed.KLINE_PERIOD, 2)['data']
        assert(len(bar) == 2)
        mylivefeedlogger.info("Latest price %s" % float(bar[0]['close']))
        #curdatetime = self.__getTradeDateTime(bar[1][0])
        curdatetime = datetime.datetime.fromtimestamp(bar[0]['id'])
        if (curdatetime == self.__prevTradeDateTime):
                time.sleep(60)
                return False

        #prevdatetime = self.__getTradeDateTime(bar[0][0]) 
        prevdatetime = datetime.datetime.fromtimestamp(bar[1]['id'])      
        barDict = {
            huobiapi.INSTRUMENT_SYMBOL: TradeBar(prevdatetime, bar[1])
        }
        self.__prevTradeDateTime = curdatetime
        self.__barDicts.append(barDict)

        mylivefeedlogger.info("LiveTradeFeed.__dispatchImpl():")
        for tb in self.__barDicts:
            mylivefeedlogger.info("  %s, %s" % (tb[huobiapi.INSTRUMENT_SYMBOL].getDateTime(), tb[huobiapi.INSTRUMENT_SYMBOL].getClose()))

        #pdb.set_trace()
        return True

    # Bar datetimes should not duplicate. In case trade object datetimes conflict, we just move one slightly forward.
    def __getTradeDateTime(self, dateString):
        year = int(dateString[0:4])
        month = int(dateString[4:6])
        day = int(dateString[6:8])
        hour = int(dateString[8:10])
        minute = int(dateString[10:12])
        ret = datetime.datetime(year, month, day, hour, minute)
        '''if ret == self.__prevTradeDateTime:
            ret += datetime.timedelta(microseconds=1)
        self.__prevTradeDateTime = ret'''
        return ret

    '''def __onTrade(self, trade):
        # Build a bar for each trade.
        barDict = {
            huobiapi.INSTRUMENT_SYMBOL: TradeBar(self.__getTradeDateTime(trade), trade)
            }
        self.__barDicts.append(barDict)'''

    def getInit(self):
        return self.__init

    def getCurrentDateTime(self):
        return datetime.datetime.now()

    def getOrderBookUpdate(self):
        jsonData = self.__huobidata.getDepth(huobiapi.SYMBOL, 'step5')['tick']
        return jsonData['bids'][0][0], jsonData['asks'][0][0]

    def barsHaveAdjClose(self):
        return False

    def getNextBars(self):
        ret = None
        if len(self.__barDicts):
            ret = bar.Bars(self.__barDicts.pop(0))
        return ret

    def peekDateTime(self):
        # Return None since this is a realtime subject.
        return None

    # This may raise.
    def start(self):
        mylivefeedlogger.info("Start feed")
        super(LiveTradeFeed, self).start()
        self.__init = True

        # Get history bar feeds for initial preprocess
        self.__barInit = self.__huobidata.getKline(huobiapi.SYMBOL, LiveTradeFeed.KLINE_PERIOD, 100)['data']
        self.__barInitLen = len(self.__barInit)
        self.__barInitIndex = self.__barInitLen - 1

    def dispatch(self):
        # Note that we may return True even if we didn't dispatch any Bar
        # event.
        ret = False
        if self.__dispatchImpl(None):
            ret = True
        if super(LiveTradeFeed, self).dispatch():
            #pdb.set_trace()
            ret = True
        return ret

    # This should not raise.
    def stop(self):
	mylivefeedlogger.info("Stop feed")
        self.__stopped = True

    # This should not raise.
    def join(self):
        pass

    def eof(self):
        return self.__stopped
