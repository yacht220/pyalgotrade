from pyalgotrade import plotter
from pyalgotrade.broker import backtesting
from pyalgotrade.stratanalyzer import returns
import mybasestrategy
import myfeed
import mybroker
from mystrategy.common import mysignal
from mystrategy.huobi import huobiapi

# Load the yahoo feed from the CSV file
#feed = yahoofeed.Feed()
#feed.addBarsFromCSV("orcl", "./mystrategy/orcl-2000.csv")

huobi = huobiapi.BtcLtcDataApi()
kline = huobi.getKline(huobiapi.SYMBOL_LTCCNY, '060', 500)
#print kline
feed = myfeed.Feed()
feed.addBarsFromJson("btc", kline)

commission = backtesting.TradePercentage(0.002)
brk = mybroker.MyBroker(10000, feed, commission)

#signal = mysignal.MyPriceSmaCrossOverSignal()
#signal = mysignal.MyPriceSmaUpDownSignal()
signal = mysignal.MySmaCrossOverUpDownSignal()
#signal = mysignal.MyEmaCrossOverUpDownSignal()
#signal = mysignal.MyQuickAdvanceAndDeclineSignal()
#signal = mysignal.MySmaUpAndDownSignal()
#signal = mysignal.MyMacdCrossOverUpDownSignal()

# Evaluate the strategy with the feed's bars.
myStrategy = mybasestrategy.MyBaseStrategy(feed, brk, "btc", signal, 12, 26, 12, 26, 9)

# Attach a returns analyzers to the strategy.
returnsAnalyzer = returns.Returns()
myStrategy.attachAnalyzer(returnsAnalyzer)
# Attach the plotter to the strategy.
plt = plotter.StrategyPlotter(myStrategy)
# Include the SMA in the instrument's subplot to get it displayed along with the closing prices.
plt.getInstrumentSubplot("btc").addDataSeries("SMAFast", myStrategy.getSMAFast())
if myStrategy.getSMASlow() is not None:
	plt.getInstrumentSubplot("btc").addDataSeries("SMASlow", myStrategy.getSMASlow())

# Plot the simple returns on each bar.
plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", returnsAnalyzer.getReturns())

# Run the strategy.
myStrategy.run()
myStrategy.info("Final portfolio value: %.2f CNY" % myStrategy.getResult())

# Plot the strategy.
plt.plot()