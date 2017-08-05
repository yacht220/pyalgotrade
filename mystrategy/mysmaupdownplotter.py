from pyalgotrade import plotter
#from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.stratanalyzer import returns
import mysmaupdown
import myfeed
import huobiapi

# Load the yahoo feed from the CSV file
#feed = yahoofeed.Feed()
#feed.addBarsFromCSV("orcl", "./mystrategy/orcl-2000.csv")

huobi = huobiapi.DataApi()
kline = huobi.getKline(huobiapi.SYMBOL_BTCCNY, '060', 300)
#print kline
feed = myfeed.Feed()
feed.addBarsFromJson("btc", kline)

# Evaluate the strategy with the feed's bars.
myStrategy = mysmaupdown.MySMAUpDown(feed, "btc", 10)

# Attach a returns analyzers to the strategy.
returnsAnalyzer = returns.Returns()
myStrategy.attachAnalyzer(returnsAnalyzer)

# Attach the plotter to the strategy.
plt = plotter.StrategyPlotter(myStrategy)
# Include the SMA in the instrument's subplot to get it displayed along with the closing prices.
plt.getInstrumentSubplot("btc").addDataSeries("SMA", myStrategy.getSMA())
# Plot the simple returns on each bar.
plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", returnsAnalyzer.getReturns())

# Run the strategy.
myStrategy.run()
myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())

# Plot the strategy.
plt.plot()