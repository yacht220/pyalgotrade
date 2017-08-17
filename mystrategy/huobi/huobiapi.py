import json
import requests
import time
from datetime import datetime
import pdb

SYMBOL_BTCCNY = 'BTC_CNY'
SYMBOL_LTCCNY = 'LTC_CNY'
SYMBOL_BTCUSD = 'BTC_USD'

class DataApi(object):
    KLINE_SYMBOL_URL = {
        SYMBOL_BTCCNY: 'http://api.huobi.com/staticmarket/btc_kline_[period]_json.js',
        SYMBOL_LTCCNY: 'http://api.huobi.com/staticmarket/btc_kline_[period]_json.js',
        SYMBOL_BTCUSD: 'http://api.huobi.com/usdmarket/btc_kline_[period]_json.js'
    }   

    DEPTH_SYMBOL_URL = {
        SYMBOL_BTCCNY: 'http://api.huobi.com/staticmarket/depth_btc_json.js',
        SYMBOL_LTCCNY: 'http://api.huobi.com/staticmarket/depth_ltc_json.js',
        SYMBOL_BTCUSD: 'http://api.huobi.com/usdmarket/depth_btc_json.js'
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

    def getDepth(self, symbol, level):
        url = self.DEPTH_SYMBOL_URL[symbol]
        url = url.replace('json', level)

        try:
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                return data
        except Exception, e:
            print e
            return None

class TradeApiFake(object):
    def __init__(self):
        self.__orderIdTmp = None
        self.__orderTypeTmp = None
        self.__requestQuantityTmp = None
        self.__requestPriceTmp = None
        self.__feeTmp = 0.002
        self.__cashTmp = 10000
        self.__isInPositionTmp = False
        self.__dateTime = None
        self.__data = DataApi()

    def getAccountInfo(self):
        #pdb.set_trace()
        if  self.__isInPositionTmp is True:
            curBar = self.__data.getKline(SYMBOL_BTCCNY, '001', 1)
            total = self.__cashTmp + self.__requestQuantityTmp * float(curBar[0][4])
            share = self.__requestQuantityTmp
        else:
            total = self.__cashTmp
            share = 0

        ret = {'total': total, 
               'available_cny_display': self.__cashTmp, 
               'available_btc_display':share}
        return ret

    def getOrderInfo(self, id_):
        vot = self.__requestQuantityTmp * self.__requestPriceTmp
        fee = vot * self.__feeTmp
        if self.__isInPositionTmp is True:
            total = vot + fee
        else:
            total = vot - fee
        ret = {'id':self.__orderIdTmp, 
               'type':self.__orderTypeTmp, 
               'order_price':self.__requestPriceTmp, 
               'order_amount':self.__requestQuantityTmp,
               'processed_price':self.__requestPriceTmp,
               'processed_amount':self.__requestQuantityTmp,
               'vot':vot,
               'fee':fee,
               'total':total,
               'status':2}
        return self.__dateTime, ret

    def buyMarket(self, quantity):
        #pdb.set_trace()
        curBar = self.__data.getKline(SYMBOL_BTCCNY, '001', 1)
        self.__isInPositionTmp = True
        self.__orderIdTmp = 1234
        self.__orderTypeTmp = 3
        self.__requestPriceTmp = float(curBar[0][4])
        self.__requestQuantityTmp = quantity
        cost = self.__requestPriceTmp * self.__requestQuantityTmp
        fee = cost * self.__feeTmp
        self.__cashTmp -= cost + fee
        self.__dateTime = datetime.fromtimestamp(time.time())
        ret = {'result':'success', 'id':self.__orderIdTmp}
        return self.__dateTime, ret

    def sellMarket(self, quantity):
        curBar = self.__data.getKline(SYMBOL_BTCCNY, '001', 1)
        self.__isInPositionTmp = False
        self.__orderIdTmp = 1235
        self.__orderTypeTmp = 4
        self.__requestPriceTmp = float(curBar[0][4])
        self.__requestQuantityTmp = quantity
        cost = self.__requestPriceTmp * self.__requestQuantityTmp
        fee = cost * self.__feeTmp
        self.__cashTmp += cost - fee
        self.__dateTime = datetime.fromtimestamp(time.time())
        ret = {'result':'success', 'id':self.__orderIdTmp}
        return self.__dateTime, ret

    def buyLimit(self, price, quantity):
        self.__isInPositionTmp = True
        self.__orderIdTmp = 1234
        self.__orderTypeTmp = 3
        self.__requestPriceTmp = price
        self.__requestQuantityTmp = quantity
        cost = self.__requestPriceTmp * self.__requestQuantityTmp
        fee = cost * self.__feeTmp
        self.__cashTmp -= cost + fee
        self.__dateTime = datetime.fromtimestamp(time.time())
        ret = {'result':'success', 'id':self.__orderIdTmp}
        return self.__dateTime, ret
        

    def sellLimit(self, price, quantity):
        self.__isInPositionTmp = False
        self.__orderIdTmp = 1235
        self.__orderTypeTmp = 4
        self.__requestPriceTmp = price
        self.__requestQuantityTmp = quantity
        cost = self.__requestPriceTmp * self.__requestQuantityTmp
        fee = cost * self.__feeTmp
        self.__cashTmp += cost - fee
        self.__dateTime = datetime.fromtimestamp(time.time())
        ret = {'result':'success', 'id':self.__orderIdTmp}
        return self.__dateTime, ret