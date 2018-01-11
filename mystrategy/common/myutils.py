def truncFloat(floatvalue, decnum):
	tmp = int('1' + '0' * decnum)
	return float(int(round(floatvalue * tmp))) / float(tmp)