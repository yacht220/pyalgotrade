# Float operation should be more careful as it's nature of modern processor.
# Please refer to https://docs.python.org/2.7/tutorial/floatingpoint.html or https://docs.python.org/3.6/tutorial/floatingpoint.html

from decimal import Decimal
import decimal

def truncFloat(floatvalue, decnum):
	tmp = Decimal('1' + '0' * decnum)
	floatvalue = Decimal(str(floatvalue))
	ret = float((floatvalue * tmp).to_integral_value(rounding = decimal.ROUND_DOWN) / tmp)
	#print 36.157 # It will give you 36.15699999, at least in my PC.
	#print Decimal(36.157)
	#print Decimal(Decimal(str(36.157)) * Decimal(10000)).to_integral_value(rounding = decimal.ROUND_DOWN)
	return ret

def truncFloatAlt(floatvalue, decnum):
	tmp = int('1' + '0' * decnum)
	#floatvalue = float(str(floatvalue))
	ret = float(int(float(str(floatvalue * tmp)))) / tmp
	return ret