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
        self.__open = float(tradeJson[1])
        self.__high = float(tradeJson[2])
        self.__low = float(tradeJson[3])
        self.__price = float(tradeJson[4])
        self.__amount = float(tradeJson[5])
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

    KLINE_PERIOD = '060'

    def __init__(self, maxLen=None):
        super(LiveTradeFeed, self).__init__(bar.Frequency.MINUTE, maxLen)
        self.__barDicts = []
        self.registerInstrument(common.ltc_symbol)
        self.__prevTradeDateTime = None
        self.__stopped = False
        self.__huobidata = huobiapi.BtcLtcDataApi()
        
        #self.__orderBookUpdateEvent = observer.Event()

    def __dispatchImpl(self, eventFilter):
        # Preprocess history bar feeds
        if self.__init is True:
            mylivefeedlogger.info("Process initial bar feeds, bar index %s" % self.__barInitIndex)

            datetime_ = self.__getTradeDateTime(self.__barInit[self.__barInitIndex][0])        
            barDict = {
                common.ltc_symbol: TradeBar(datetime_, self.__barInit[self.__barInitIndex])
            }
            self.__barDicts.append(barDict)
            self.__barInitIndex += 1

            # Leave last 2 feeds unpreprocessed since they will be handled in live feed later
            if self.__barInitIndex >= self.__barInitLen - 2:
                self.__init = False

            return True

        bar = self.__huobidata.getKline(huobiapi.SYMBOL_LTCCNY, LiveTradeFeed.KLINE_PERIOD, 2)
        assert(len(bar) == 2)
        curdatetime = self.__getTradeDateTime(bar[1][0])
        if (curdatetime == self.__prevTradeDateTime):
                time.sleep(60)
                return False

        prevdatetime = self.__getTradeDateTime(bar[0][0])        
        barDict = {
            common.ltc_symbol: TradeBar(prevdatetime, bar[0])
        }
        self.__prevTradeDateTime = curdatetime
        self.__barDicts.append(barDict)

        mylivefeedlogger.info("LiveTradeFeed.__dispatchImpl:")
        for tb in self.__barDicts:
            mylivefeedlogger.info("  %s, %s" % (tb[common.ltc_symbol].getDateTime(), tb[common.ltc_symbol].getClose()))

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
            common.btc_symbol: TradeBar(self.__getTradeDateTime(trade), trade)
            }
        self.__barDicts.append(barDict)'''

    def getInit(self):
        return self.__init

    def getCurrentDateTime(self):
        return datetime.datetime.now()

    def getOrderBookUpdate(self):
        jsonData = self.__huobidata.getDepth(huobiapi.SYMBOL_LTCCNY, '1')
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
        self.__barInit = self.__huobidata.getKline(huobiapi.SYMBOL_LTCCNY, LiveTradeFeed.KLINE_PERIOD, 50)
        self.__barInitLen = len(self.__barInit)
        self.__barInitIndex = 0

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

    '''def getOrderBookUpdateEvent(self):
        """
        Returns the event that will be emitted when the orderbook gets updated.

        Eventh handlers should receive one parameter:
         1. A :class:`pyalgotrade.bitstamp.wsclient.OrderBookUpdate` instance.

        :rtype: :class:`pyalgotrade.observer.Event`.
        """
        return self.__orderBookUpdateEvent'''
