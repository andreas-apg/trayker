import net_setup
from time import sleep
from umqtt.simple import MQTTClient
from hcsr04 import HCSR04
import mfrc522
from os import uname
from read import do_read
import machine
from hx711 import HX711
import _thread
import sys

#MQTT
SERVER = '10.3.141.1'  # MQTT Server Address (Change to the IP address of your Pi)
CLIENT_ID = 'MESA1'
TOPIC = b'mesa1_sensores'
TOPIC_STATUS = b'mesa1_pronta'

client = MQTTClient(CLIENT_ID, SERVER)
client.connect()   # Connect to MQTT broker

#ULTRASSONICO
sensor = HCSR04(trigger_pin=26, echo_pin=25, echo_timeout_us=10000)
distancia = 0

#HX711: DATA = 32, SCK=33
hx = HX711(32,33)
peso = 0

#RFID:
rfid = '[0, 0, 0, 0]'

#BOTAO
apertado = False
def handle_interrupt(pin):
    #print("Botao apertado")
    global apertado
    apertado = True

def read():
    sleep(2)
    hx.tare()
    print(hx.read())
    sleep(2)
    while True:
        try:
            global rfid
    	    rfid = do_read()
    	    if rfid is None:
    		    rfid = '[0, 0, 0, 0]'
            global distancia
            distancia = sensor.distance_cm()
            global peso
            peso = hx.read()
            msg = (b'{0:3}|{1:3}|{2:3}'.format(distancia, str(rfid), peso))
            client.publish(TOPIC, msg)  # Publish sensor data to MQTT topic
            print(msg)

        except OSError:
            print('Failed to read sensor.')
            continue
        sleep(4)

def waiting():
    pronta = '0'
    while True:
        try:
            sleep(10)
            if(distancia > 30 and peso < 315 and rfid != '[0, 0, 0, 0]' and apertado == False):
                pronta = '1'
                sleep(10)
                pronta = checa_estado()
                sleep(10)
                pronta = checa_estado()
                sleep(10)
                pronta = checa_estado()
            else:
                pronta = '0'
            print('Pronta: ' + pronta)
            client.publish(TOPIC_STATUS, pronta)
        except OSError:
            print('Erro na espera')
            continue

def checa_estado():
    if(distancia > 30 and peso < 315 and rfid != '[0, 0, 0, 0]' and apertado == False):
        return '1'
    return '0'

def test():
    while True:
        print(peso)
        sleep(2)

_thread.start_new_thread(read, ())
_thread.start_new_thread(waiting, ())
