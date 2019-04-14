import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
	print('Connected with result code {0}'.format(rc))
	client.subscribe('temp_humidity')

def on_message(client, userdata, msg):
	t, h = [int(x) for x in msg.payload.decode("utf-8").split(',')]
	if(h != 75):
		print('{0}C {1}%'.format(t, h))
	else:
		print('{0}C {1}%'.format(t, h))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect('localhost', 1883, 60)

client.loop_forever()
