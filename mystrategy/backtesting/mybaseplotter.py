from pyalgotrade import plotter
from pyalgotrade.broker import backtesting
from pyalgotrade.stratanalyzer import returns
import mybasestrategy
import myfeed
import mybroker
from mystrategy.common import mysignal
from mystrategy import common
from mystrategy.huobi import huobiapi

common.isBacktesting = True

# Load the yahoo feed from the CSV file
#feed = yahoofeed.Feed()
#feed.addBarsFromCSV("orcl", "./mystrategy/orcl-2000.csv")

huobi = huobiapi.HuobiDataApi()
kline = huobi.getKline(huobiapi.SYMBOL, '15min', 2000)['data']
#print kline
feed = myfeed.Feed()
feed.addBarsFromJson(huobiapi.INSTRUMENT_SYMBOL, kline)

commission = backtesting.TradePercentage(0.004)
brk = mybroker.MyBroker(10000, feed, commission)

#signal = mysignal.MyPriceSmaCrossOverSignal()
#signal = mysignal.MyPriceSmaUpDownSignal()
#signal = mysignal.MySmaCrossOverUpDownSignal()
#signal = mysignal.MyEmaCrossOverUpDownSignal()
#signal = mysignal.MyQuickAdvanceAndDeclineSignal()
#signal = mysignal.MySmaUpAndDownSignal()
#signal = mysignal.MyMacdCrossOverUpDownSignal()
#signal = mysignal.MySmaCrossOverUpDownSignalStopLossStopProfit()
#signal = mysignal.MyMultiSmaCrossOverUpDownSignal()
signal = mysignal.MyPriceSmaDeviationSignal()

smaPeriodFast = 48
smaPeriodSlow = 96
smaPeriodA = None
smaPeriodB = None
smaPeriodC = None
emaPeriodFast = None
emaPeriodSlow = None
emaPeriodSignal = None
# Evaluate the strategy with the feed's bars.
myStrategy = mybasestrategy.MyBaseStrategy(feed, brk, huobiapi.INSTRUMENT_SYMBOL, signal, smaPeriodFast, 
	smaPeriodSlow, smaPeriodA, smaPeriodB, smaPeriodC, emaPeriodFast, emaPeriodSlow, emaPeriodSignal)

# Attach a returns analyzers to the strategy.
returnsAnalyzer = returns.Returns()
myStrategy.attachAnalyzer(returnsAnalyzer)
# Attach the plotter to the strategy.
plt = plotter.StrategyPlotter(myStrategy)
# Include the SMA in the instrument's subplot to get it displayed along with the closing prices.
if myStrategy.getSMAFast() is not None:
	plt.getInstrumentSubplot(huobiapi.INSTRUMENT_SYMBOL).addDataSeries("SMAFast", myStrategy.getSMAFast())

if myStrategy.getSMASlow() is not None:
	plt.getInstrumentSubplot(huobiapi.INSTRUMENT_SYMBOL).addDataSeries("SMASlow", myStrategy.getSMASlow())

if myStrategy.getSMAA() is not None:
	plt.getInstrumentSubplot(huobiapi.INSTRUMENT_SYMBOL).addDataSeries("SMAA", myStrategy.getSMAA())

if myStrategy.getSMAB() is not None:
	plt.getInstrumentSubplot(huobiapi.INSTRUMENT_SYMBOL).addDataSeries("SMAB", myStrategy.getSMAB())

if myStrategy.getSMAC() is not None:
	plt.getInstrumentSubplot(huobiapi.INSTRUMENT_SYMBOL).addDataSeries("SMAC", myStrategy.getSMAC())

if myStrategy.getEMAFast() is not None:
	plt.getInstrumentSubplot(huobiapi.INSTRUMENT_SYMBOL).addDataSeries("EMAFast", myStrategy.getEMAFast())

if myStrategy.getEMASlow() is not None:
	plt.getInstrumentSubplot(huobiapi.INSTRUMENT_SYMBOL).addDataSeries("EMASlow", myStrategy.getEMASlow())

# Plot the simple returns on each bar.
plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", returnsAnalyzer.getReturns())

# Run the strategy.
myStrategy.run()
myStrategy.info("Final portfolio value: %.2f %s" % (myStrategy.getResult(), huobiapi.CURRENCY_SYMBOL))

# Plot the strategy.
plt.plot()
