import serial

bs = serial.Serial("/dev/rfcomm0", baudrate=9600)
print("Conectado")
def send(a):
    r = bs.write(a)
    data = bs.readline()
    print(data)
    print(r)

send(b'1')
