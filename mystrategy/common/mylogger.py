import pyalgotrade.logger

def getMyLogger(name):
	logger = pyalgotrade.logger.getLogger(name)
	return logger