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

from pyalgotrade.barfeed import common
from pyalgotrade import bar
from pyalgotrade.barfeed import membf
import datetime

class Feed(membf.BarFeed):
    """Class for json data
    """
    def __init__(self, frequency=bar.Frequency.HOUR, timezone=None, maxLen=None):
        if isinstance(timezone, int):
            raise Exception("timezone as an int parameter is not supported anymore. Please use a pytz timezone instead.")

        if frequency not in [bar.Frequency.HOUR, bar.Frequency.WEEK]:
            raise Exception("Invalid frequency.")

        super(Feed, self).__init__(frequency, maxLen)

        self.__timezone = timezone
        self.__sanitizeBars = False
        self.__barClass = bar.BasicBar
        self.__frequency = frequency

    def __parseDate(self, dateString):
        year = int(dateString[0:4])
        month = int(dateString[4:6])
        day = int(dateString[6:8])
        hour = int(dateString[8:10])
        minute = int(dateString[10:12])
        ret = datetime.datetime(year, month, day, hour, minute)
        return ret

    def barsHaveAdjClose(self):
        return True

    def addBarsFromJson(self, instrument, jsondata):
        loadedBars = []
        for it in jsondata:
            dateTime = datetime.datetime.fromtimestamp(it['id'])
            open_ = float(it['open'])
            high = float(it['high'])
            low = float(it['low'])
            close = float(it['close'])
            volume = float(it['amount'])
            adjClose = None
            bar_ = self.__barClass(dateTime, open_, high, low, close, volume, adjClose, self.__frequency)
            loadedBars.append(bar_)
        self.addBarsFromSequence(instrument, loadedBars)