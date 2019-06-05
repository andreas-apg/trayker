import paho.mqtt.client as mqtt

def on_connect_mesa1(client, userdata, flags, rc):
	print('Connected with result code {0}'.format(rc))
	client.subscribe('mesa1_sensores')

def on_message_mesa1(client, userdata, msg):
    msg = msg.payload.decode("utf-8").split('|')
    distancia = float(msg[0])
    rfid = msg[1]
    peso = float(msg[2])
    #print(peso)
    print('Distancia: {:03.0f} cm, Peso: {:04.0f} g, RFID: {}'.format(distancia, peso, rfid))
    print(msg)
    #print(msg.payload.decode("utf-8").split(','))

client = mqtt.Client()
client.on_connect_mesa1 = on_connect
client.on_message_mesa1 = on_message
client.connect('localhost', 1883, 60)

client.loop_forever()
