from hx711_spi import HX711
hx = HX711(18, 19, 5)
hx.set_gain(32)
hx.tare()
def run():
	val = hx.get_units()
	print(val)
	val = hx.read()
	print(val)
