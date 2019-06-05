import serial

bs = serial.Serial("/dev/rfcomm0", baudrate=9600)
print("Conectado")
def send(a):
	bs.write(a)
	data = bs.readline()
	print(data)
