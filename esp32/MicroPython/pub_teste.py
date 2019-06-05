import net_setup
from time import sleep
from umqtt.simple import MQTTClient
from hcsr04 import HCSR04
import mfrc522
from os import uname
from read import do_read
import machine
from hx711 import HX711


#MQTT
SERVER = '10.3.141.1'  # MQTT Server Address (Change to the IP address of your Pi)
CLIENT_ID = 'ESP32_DHT11_Sensor'
TOPIC = b'ultrassonico'

client = MQTTClient(CLIENT_ID, SERVER)
client.connect()   # Connect to MQTT broker

#ULTRASSONICO
sensor = HCSR04(trigger_pin=26, echo_pin=25, echo_timeout_us=10000)

#BOTAO
apertado = False
def handle_interrupt(pin):
    #print("Botao apertado")
    global apertado
    apertado = True

bot = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
bot.irq(trigger=machine.Pin.IRQ_FALLING, handler=handle_interrupt)


#HX711: DATA = 32, SCK=33
hx = HX711(32,33)
hx.tare()
print(hx.read())

def run():
    hx.tare()
    while True:
        try:
            rfid = do_read()
            if rfid is None:
                rfid = '0'
            distance = sensor.distance_cm()
            peso = hx.read()
            msg = (b'ultrasonic: {0:3}, rfid: {1:3}, peso: {2:3}'.format(distance, str(rfid), peso))
            client.publish(TOPIC, msg)  # Publish sensor data to MQTT topic
            print(msg)
        except OSError:
            print('Failed to read sensor.')
        sleep(4)

