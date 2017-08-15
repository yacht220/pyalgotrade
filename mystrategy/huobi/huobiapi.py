import json
import requests
import time
from datetime import datetime

SYMBOL_BTCCNY = 'BTC_CNY'
SYMBOL_LTCCNY = 'LTC_CNY'
SYMBOL_BTCUSD = 'BTC_USD'

class DataApi(object):
    KLINE_SYMBOL_URL = {
        SYMBOL_BTCCNY: 'http://api.huobi.com/staticmarket/btc_kline_[period]_json.js',
        SYMBOL_LTCCNY: 'http://api.huobi.com/staticmarket/btc_kline_[period]_json.js',
        SYMBOL_BTCUSD: 'http://api.huobi.com/usdmarket/btc_kline_[period]_json.js'
    }   
    def __init__(self):
        pass

    def getKline(self, symbol, period, length=0):
        url = self.KLINE_SYMBOL_URL[symbol]
        url = url.replace('[period]', period)
        
        if length:
            url = url + '?length=' + str(length)
            
        try:
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                return data
        except Exception, e:
            print e
            return None

class TradeApi(object):x
    def __init__(self):
        self.__requestQuantityTmp = None
        self.__requestPriceTmp = None
        self.__dateTime = None
        self.__data = DataApi()
 
    def getOrderInfo(self, id_):
        ret = {'id':1234, 'type':3, 'order_price':self.__requestPriceTmp, 'order_quantity'}

    def buyMarket(self, quantity):
        curBar = self.__data.getKline(SYMBOL_BTCCNY, '001', 1)
        self.__requestPriceTmp = float(curBar[0][4])
        self.__requestQuantityTmp = quantity
        self.__dateTime = datetime.fromtimestamp(time.time())
        ret = {'result':'success', 'id':1234}
        return self.__dateTime, ret

