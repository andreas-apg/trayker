from time import sleep
from umqtt.simple import MQTTClient
from machine import Pin
from dht import DHT11

SERVER = '192.168.100.144'  # MQTT Server Address (Change to the IP address of your Pi)
CLIENT_ID = 'ESP32_DHT11_Sensor'
TOPIC = b'temp_humidity'

client = MQTTClient(CLIENT_ID, SERVER)
client.connect()   # Connect to MQTT broker

sensor = DHT11(Pin(15, Pin.IN, Pin.PULL_UP))   # DHT-22 on GPIO 15 (input with internal pull-up resistor)

while True:
    try:
        sensor.measure()   # Poll sensor
        t = sensor.temperature()
        h = sensor.humidity()
        if isinstance(t, int) and isinstance(h, int):  # Confirm sensor results are numeric
            msg = (b'{0:3},{1:3}'.format(t, h))
            client.publish(TOPIC, msg)  # Publish sensor data to MQTT topic
            print(msg)
        else:
            print('Invalid sensor readings.')
    except OSError:
        print('Failed to read sensor.')
    sleep(4)

