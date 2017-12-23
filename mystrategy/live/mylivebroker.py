from pyalgotrade import broker
from mystrategy.huobi import huobiapi
from mystrategy.common import mylogger
from mystrategy import common
import datetime
import time

mylivebrklogger = mylogger.getMyLogger("mylivebroker")

class MyInstrumentTraits(broker.InstrumentTraits):
    def roundQuantity(self, quantity):
        return float(quantity)

class MyOrder(object):
    def __init__(self):
        self.__id = None
        #self.__type = None
        #self.__requestPrice = None
        #self.__requestQuantity = None
        self.__filledPrice = None
        self.__filledQuantity = None
        #self.__vot = None
        self.__fee = None
        #self.__total = None 
        #self.__status = None
        self.__dateTime = None

    def setId(self, id_):
        self.__id = id_

    def getId(self):
        return self.__id

    '''def setType(self, type_):
        self.__type = type_

    def getType(self):
        return self.__type

    def setRequestPrice(self, requestPrice):
        self.__requestPrice = requestPrice

    def getRequestPrice(self):
        return self.__requestPrice

    def setRequestQuantity(self, requestQuantity):
        self.__requestQuantity = requestQuantity

    def getRequestQuantity(self):
        return self.__requestQuantity'''

    def setFilledPrice(self, filledPrice):
        self.__filledPrice = filledPrice

    def getFilledPrice(self):
        return self.__filledPrice

    def setFilledQuantity(self, filledQuantity):
        self.__filledQuantity = filledQuantity

    def getFilledQuantity(self):
        return self.__filledQuantity

    '''def setVot(self, vot):
        self.__vot = vot

    def getVot(self):
        return self.__vot'''

    def setFee(self, fee):
        self.__fee = fee

    def getFee(self):
        return self.__fee

    '''def setTotal(self, total):
        self.__total = total

    def getTotal(self):
        return self.__total

    def setStatus(self, status):
        self.__status = status

    def getStatus(self):
        return self.__status'''

    def setDateTime(self, time):
        self.__dateTime = time

    def getDateTime(self):
        return self.__dateTime    

class MyLiveBroker(broker.Broker):
    def __init__(self):
        super(MyLiveBroker, self).__init__()
        self.__huobitrade = huobiapi.HuobiTradeApi()
        self.__stop = False
        self.__activeOrders = {}
        self.__total = 0
        self.__cash = 0
        self.__shares = {}

    def _registerOrder(self, order):
        assert(order.getId() not in self.__activeOrders)
        assert(order.getId() is not None)
        self.__activeOrders[order.getId()] = order

    def _unregisterOrder(self, order):
        assert(order.getId() in self.__activeOrders)
        assert(order.getId() is not None)
        del self.__activeOrders[order.getId()]

    def _orderStatusUpdate(self, orders):
        for order in orders:
            huobiOrder = self._getOrderInfo(order.getId())
            fee = huobiOrder.getFee()
            filledPrice = huobiOrder.getFilledPrice()
            filledQuantity = huobiOrder.getFilledQuantity()
            dateTime = huobiOrder.getDateTime()
            #TODO check the status

            orderExecutionInfo = broker.OrderExecutionInfo(filledPrice, abs(filledQuantity), fee, dateTime)
            order.addExecutionInfoLive(orderExecutionInfo)
            if not order.isActive():
                self._unregisterOrder(order)

            if order.isFilled():
                eventType = broker.OrderEvent.Type.FILLED
            else:
                eventType = broker.OrderEvent.Type.PARTIALLY_FILLED
            self.notifyOrderEvent(broker.OrderEvent(order, eventType, orderExecutionInfo))

    def _getOrderInfo(self, id_):
        if common.fake is False:
            jsonData = self.__huobitrade.getOrderInfo(id_)['data']
        else:
            jsonData = self.__huobitrade.getOrderInfoFake(id_)
        timestamp = datetime.datetime.fromtimestamp(time.time())
        order = MyOrder()
        order.setId(long(jsonData['id']))
        #order.setType(int(jsonData['type']))
        #order.setRequestPrice(float(jsonData['price']))
        #order.setRequestQuantity(float(jsonData['amount']))
        order.setFilledPrice(float(jsonData['price']))
        order.setFilledQuantity(float(jsonData['filled-amount']))
        #order.setVot(float(jsonData['vot']))
        order.setFee(float(jsonData['filled-fees']))
        #order.setTotal(float(jsonData['total']))
        #order.setStatus(int(jsonData['status']))
        order.setDateTime(timestamp)
        return order

    '''def _buyMarket(self, quantity):
        timestamp, jsonData = self.__huobitrade.buyMarket(quantity, huobiapi.COINTYPE_LTC)
        if jsonData.has_key('code'):
            raise Exception("Buy market order submission failed! Error code %s" % jsonData['code'])

        orderId = long(jsonData['id'])
        huobiOrder = MyOrder()
        huobiOrder.setId(orderId)
        huobiOrder.setDateTime(timestamp)
        return huobiOrder

    def _sellMarket(self, quantity):
        timestamp, jsonData = self.__huobitrade.sellMarket(quantity, huobiapi.COINTYPE_LTC)
        if jsonData.has_key('code'):
            raise Exception("Buy market order submission failed! Error code %s" % jsonData['code'])

        orderId = long(jsonData['id'])
        huobiOrder = MyOrder()
        huobiOrder.setId(orderId)
        huobiOrder.setDateTime(timestamp)
        return huobiOrder'''

    def _buyLimit(self, price, quantity):
        #self.__huobitrade = huobiapi.HuobiTradeApiFake()
        if common.fake is False:
            jsonData = self.__huobitrade.buyLimit(str(price), str(quantity), huobiapi.SYMBOL_BTCUSDT)
        else:
            jsonData = self.__huobitrade.buyLimitFake(str(price), str(quantity), huobiapi.SYMBOL_BTCUSDT)
        timestamp = datetime.datetime.fromtimestamp(time.time())
        if jsonData['status'] != 'ok':
            raise Exception("Buy market order submission failed! Error code %s" % jsonData['status'])

        orderId = long(jsonData['data'])
        huobiOrder = MyOrder()
        huobiOrder.setId(orderId)
        huobiOrder.setDateTime(timestamp)
        return huobiOrder

    def _sellLimit(self, price, quantity):
        #self.__huobitrade = huobiapi.HuobiTradeApi()
        jsonData = self.__huobitrade.sellLimit(str(price), str(quantity), huobiapi.SYMBOL_BTCUSDT)
        timestamp = datetime.datetime.fromtimestamp(time.time())
        if jsonData['status'] != 'ok':
            raise Exception("Buy market order submission failed! Error code %s" % jsonData['status'])

        orderId = long(jsonData['data'])
        huobiOrder = MyOrder()
        huobiOrder.setId(orderId)
        huobiOrder.setDateTime(timestamp)
        return huobiOrder

    def _cancelOrder(self, id_):
        jsonData = self.__huobitrade.cancelOrder(id_)
        if jsonData['status'] != 'ok':
            mylivebrklogger.info("Failed to submit order %s cancellation request. Error code %s" % id, jsonData['status'])
            return False

        return True        

    def refreshAccountBalance(self):
        #self.__stop  = True
        jsonData = self.__huobitrade.getBalance()
        if jsonData['status'] != 'ok':
            raise Exception("Get account info failed! Error code %s" % jsonData['status'])

        balList = jsonData['data']['list']
        setCount = 0
        for i in balList:
            if i['currency'] == common.usdt_symbol and i['type'] == 'trade':
                self.__cash = float(i['balance'])
                setCount += 1
            elif i['currency'] == common.btc_symbol and i['type'] == 'trade':
                self.__shares = {common.btc_symbol:float(i['balance'])}
                setCount += 1
            if setCount == 2:
                break

        #self.__total = float(jsonData['total'])
        #self.__cash = float(jsonData['available_cny_display'])
        #self.__shares = {common.btc_symbol:float(jsonData['available_ltc_display'])}
        #self.__stop = False

    def submitOrder(self, order):
        if order.isInitial():
            order.setAllOrNone(False)
            order.setGoodTillCanceled(True)

            if order.isBuy():
                huobiOrder = self._buyLimit(order.getLimitPrice(), order.getQuantity())
            else:
                huobiOrder = self._sellLimit(order.getLimitPrice(), order.getQuantity())

            mylivebrklogger.info("Order id %s" % huobiOrder.getId())
            order.setSubmitted(huobiOrder.getId(), huobiOrder.getDateTime())
            self._registerOrder(order)
            order.switchState(broker.Order.State.SUBMITTED)
        else:
            raise Exception("The order was already processed")

    def start(self):
        mylivebrklogger.info("Start broker")
        super(MyLiveBroker, self).start()
        self.refreshAccountBalance()
    
    def stop(self):
        mylivebrklogger.info("Stop broker")
        self.__stop = True

    def join(self):
        pass

    def eof(self):
        return self.__stop

    def dispatch(self):
        ordersToProcess = self.__activeOrders.values()
        for order in ordersToProcess:
            if order.isSubmitted():
                order.switchState(broker.Order.State.ACCEPTED)
                self.notifyOrderEvent(broker.OrderEvent(order, broker.OrderEvent.Type.ACCEPTED, None))

        self._orderStatusUpdate(ordersToProcess)
        #self._refreshAccountBalance()
        #mylivebrklogger.info("Current equity %.2f" % self.getEquity())

    def peekDateTime(self):
        return None

    def getInstrumentTraits(self, instrument):
        return MyInstrumentTraits()

    def getCash(self, includeShort=True):
        return self.__cash

    def getShares(self, instrument):
        return self.__shares.get(instrument, 0)

    def getPositions(self):
        return self.__shares

    def getEquity(self):
        return self.__total

    def getActiveOrders(self, instrument=None):
        raise Exception("Not supported")

    def createMarketOrder(self, action, instrument, quantity, onClose=False):
        return broker.MarketOrder(action, instrument, quantity, onClose, self.getInstrumentTraits(instrument))

    def createLimitOrder(self, action, instrument, limitPrice, quantity):
        #raise Exception("Not supported")
        return broker.LimitOrder(action, instrument, limitPrice, quantity, self.getInstrumentTraits(instrument))

    def createStopOrder(self, action, instrument, stopPrice, quantity):
        raise Exception("Not supported")

    def createStopLimitOrder(self, action, instrument, stopPrice, limitPrice, quantity):
        raise Exception("Not supported")

    def cancelOrder(self, order):
        activeOrder = self.__activeOrders.get(order.getId())
        if activeOrder is None:
            raise Exception("The order is not active anymore")
        if activeOrder.isFilled():
            raise Exception("Can't cancel order that has already been filled")

        ret = self._cancelOrder(order.getId())
        if ret is False:
            mylivebrklogger.info("Failed to cancel order with id %s" % order.getId())
            return
        self._unregisterOrder(order)
        order.switchState(broker.Order.State.CANCELED)

        # Update cash and shares.
        self.refreshAccountBalance()

        # Notify that the order was canceled.
        self.notifyOrderEvent(broker.OrderEvent(order, broker.OrderEvent.Type.CANCELED, "User requested cancellation"))
