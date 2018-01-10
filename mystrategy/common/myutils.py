def truncFloat(floatvalue, decnum):
	tmp = int('1' + '0' * decnum)
	return float(int(floatvalue * tmp)) / float(tmp)