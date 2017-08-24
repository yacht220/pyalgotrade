import json
import requests
import time
from datetime import datetime
import pdb
import urllib
import hashlib

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


HUOBI_TRADE_API = 'https://api.huobi.com/apiv3'

COINTYPE_BTC = 1

FUNCTIONCODE_GETACCOUNTINFO = 'get_account_info'
FUNCTIONCODE_ORDERINFO = 'order_info'
FUNCTIONCODE_BUY = 'buy'
FUNCTIONCODE_SELL = 'sell'
FUNCTIONCODE_BUYMARKET = 'buy_market'
FUNCTIONCODE_SELLMARKET = 'sell_market'
FUNCTIONCODE_CANCELORDER = 'cancel_order'

class TradeApi(object):
    def __init__(self):
        self.accessKey = ''
        self.secretKey = ''

    def _signature(self, params):
        params = sorted(params.iteritems(), key=lambda d:d[0], reverse=False)
        message = urllib.urlencode(params)
    
        m = hashlib.md5()
        m.update(message)
        m.digest()

        sig=m.hexdigest()
        return sig    

    def _processRequest(self, method_, params_, optional=None):
        method = method_
        params = params_
        
        time_ = time.time()
        datetime_ = datetime.fromtimestamp(time_)
        params['created'] = long(time_)
        params['access_key'] = self.accessKey
        params['secret_key'] = self.secretKey
        params['method'] = method
        
        sign = self._signature(params)
        params['sign'] = sign
        del params['secret_key']
        
        if optional:
            params.update(optional)
        
        payload = urllib.urlencode(params)

        r = requests.post(HUOBI_TRADE_API, params=payload)
        if r.status_code == 200:
            data = r.json()
            return datetime_, data
        else:
            return datetime_, None        
    
    def getAccountInfo(self, market='cny'):
        method = FUNCTIONCODE_GETACCOUNTINFO
        params = {}
        
        optional = {'market': market}
        datetime_, data = self._processRequest(method, params, optional)
        return datetime_, data

    def getOrderInfo(self, id_, coinType=COINTYPE_BTC, market='cny'):
        method = FUNCTIONCODE_ORDERINFO
        params = {
            'coin_type': coinType,
            'id': id_
        }
        optional = {'market': market}
        datetime_, data = self._processRequest(method, params, optional)
        return datetime_, data

    def buyLimit(self, price, quantity, coinType=COINTYPE_BTC, tradePassword='', tradeId = '', market='cny'):
        method = FUNCTIONCODE_BUY
        params = {
            'coin_type': coinType,
            'price': price,
            'amount': quantity
        }
        optional = {
            'trade_password': tradePassword,
            'trade_id': tradeId,
            'market': market
        }
        return self._processRequest(method, params, optional)

    def sellLimit(self, price, quantity, coinType=COINTYPE_BTC, tradePassword='', tradeId = '', market='cny'):
        method = FUNCTIONCODE_SELL
        params = {
            'coin_type': coinType,
            'price': price,
            'amount': quantity
        }
        optional = {
            'trade_password': tradePassword,
            'trade_id': tradeId,
            'market': market
        }
        return self._processRequest(method, params, optional)

    def buyMarket(self, quantity, coinType=COINTYPE_BTC, tradePassword='', tradeId = '', market='cny'):
        method = FUNCTIONCODE_BUYMARKET
        params = {
            'coin_type': coinType,
            'amount': quantity
        }
        optional = {
            'trade_password': tradePassword,
            'trade_id': tradeId,
            'market': market
        }
        return self._processRequest(method, params, optional) 
    
    def sellMarket(self, quantity, coinType=COINTYPE_BTC, tradePassword='', tradeId = '', market='cny'):
        method = FUNCTIONCODE_SELLMARKET
        params = {
            'coin_type': coinType,
            'amount': quantity
        }
        optional = {
            'trade_password': tradePassword,
            'trade_id': tradeId,
            'market': market
        }
        return self._processRequest(method, params, optional)      

    def cancelOrder(self, id_, coinType=COINTYPE_BTC, market='cny'):
        method = FUNCTIONCODE_CANCELORDER
        params = {
            'coin_type': coinType,
            'id': id_
        }
        optional = {'market': market}
        return self._processRequest(method, params, optional)    

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

        ret = {'total':str(total), 
               'available_cny_display':str(self.__cashTmp), 
               'available_btc_display':str(share)}
        return ret

    def getOrderInfo(self, id_):
        vot = self.__requestQuantityTmp * self.__requestPriceTmp
        fee = vot * self.__feeTmp
        if self.__isInPositionTmp is True:
            total = vot + fee
        else:
            total = vot - fee
        ret = {'id':str(self.__orderIdTmp), 
               'type':str(self.__orderTypeTmp), 
               'order_price':str(self.__requestPriceTmp), 
               'order_amount':str(self.__requestQuantityTmp),
               'processed_price':str(self.__requestPriceTmp),
               'processed_amount':str(self.__requestQuantityTmp),
               'vot':str(vot),
               'fee':str(fee),
               'total':str(total),
               'status':'2'}
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
        ret = {'result':'success', 'id':str(self.__orderIdTmp)}
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
        ret = {'result':'success', 'id':str(self.__orderIdTmp)}
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
        ret = {'result':'success', 'id':str(self.__orderIdTmp)}
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
        ret = {'result':'success', 'id':str(self.__orderIdTmp)}
        return self.__dateTime, ret

    def cancelOrder(self, id_):
        ret = {'result':'success'}
        return ret