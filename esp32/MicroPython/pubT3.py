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
connection = client.connect()   # Connect to MQTT broker

#ULTRASSONICO
sensor = HCSR04(trigger_pin=26, echo_pin=25, echo_timeout_us=10000)
distancia = 0

#BOTAO
pronta = '0'
apertado = '0'
def handle_interrupt(pin):
    global apertado
    if apertado == '0':
        print("Botao apertado.")
        apertado = '1'

bot = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
bot.irq(trigger=machine.Pin.IRQ_FALLING, handler=handle_interrupt)

def tratamento_botao():
    global apertado
    try:
        if apertado == '1':
            global pronta
            if(pronta == '1'):
                pronta = '0'
            client.publish(TOPIC_STATUS, pronta)
            print('Cancelamento. Pronta: ' + pronta)
            for i in range (0, 60):
                print('Esperando... ' + str(59 - i))
                if(i % 10 == 0):
                    client.publish(TOPIC_STATUS, pronta)
                sleep(1)
            apertado = '0'
    except OSError as er:
        apertado = '0'
        print(er.args[0])
        print('Erro no botao')
        if(er.args[0] == 104):
            print('Connection error.')
            client.connect()
        global thread2
        thread2 = 0
        return


#HX711: DATA = 32, SCK=33
hx = HX711(32,33)
peso = 0

#RFID:
rfid = '[0, 0, 0, 0]'
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

        except OSError as er:
            if(er.args[0] == 104):
                print('Connection error.')
                client.connect()
            print(er.args[0])
            print('Erro na coleta.')
            #print('Failed to read sensor.')
            continue
        sleep(4)

def waiting():
    global pronta
    pronta = '0'
    while True:
        try:
            for i in range (0, 30):
                pronta = waiting_check()
                if(apertado == '1'):
                    tratamento_botao()
                sleep(1)
            print('Pronta: ' + pronta)
            client.publish(TOPIC_STATUS, pronta)
        except OSError as er:
            print(er.args[0])
            print('Erro na espera')
            if(er.args[0] == 104):
                print('Connection error.')
                client.connect()
            global thread2
            thread2 = 0
            return

def waiting_check():
    if(distancia > 30 and peso < 315 and rfid != '[0, 0, 0, 0]'):
        return '1'
    return '0'



def test():
    while True:
        print(peso)
        sleep(2)

thread1 = 0
thread2 = 0
thread3 = 0
def working():
    while True:
        global thread1
        global thread2
        global thread3
        if thread1 == 0:
            thread1 = 1
            _thread.start_new_thread(read, ())
        if thread2 == 0:
            thread2 = 1
            _thread.start_new_thread(waiting, ())

_thread.start_new_thread(working(), ())
#working()
