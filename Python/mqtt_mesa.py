import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
	print('Connected with result code {0}'.format(rc))
	client.subscribe([('mesa1', 0),('mesa2',0), ('mesa3', 0)])

def on_message(client, userdata, msg):
    msg = msg.payload.decode("utf-8").split('|')
    #distancia = float(msg[0])
    #RFID = msg[1]
    #peso = float(msg[2])
    #print(userdata)
    print(msg)
    #print('Distancia: {:03.0f} cm, RFID: {}, Peso: {:04.0f} g'.format(distancia, RFID, peso))
    #print(msg)
    #print(msg.payload.decode("utf-8").split(','))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect('localhost', 1883, 60)

client.loop_forever()
