# Pay more attention on the float operation in python. It's not expected as you think.
# Please refer to https://docs.python.org/2.7/tutorial/floatingpoint.html or https://docs.python.org/3.6/tutorial/floatingpoint.html

from decimal import Decimal
import decimal

def truncFloat(floatvalue, decnum):
	tmp = Decimal('1' + '0' * decnum)
	floatvalue = Decimal(str(floatvalue))
	ret = float((floatvalue * tmp).to_integral_value(rounding = decimal.ROUND_DOWN) / tmp)
	#print Decimal(36.157)
	#print "manual", Decimal(Decimal(str(36.157)) * Decimal(10000)).to_integral_value(rounding = decimal.ROUND_DOWN)
	return ret