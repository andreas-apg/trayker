import os
import queue
import paho.mqtt.client as mqtt
import _thread
from time import sleep
from flask import Flask, jsonify, render_template
from flask_cors import CORS
import fila_tarefa

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(20)
CORS(app)

distancia1 = 0
rfid1 = '[0, 0, 0, 0]'
peso1 = 0
pronta1 = 0
anterior1 = 0

distancia2 = 0
rfid2 = '[0, 0, 0, 0]'
peso2 = 0
pronta2 = 0
anterior2 = 0

distancia3 = 0
rfid3 = '[0, 0, 0, 0]'
peso3 = 0
pronta3 = 0
anterior3 = 0

fila = fila_tarefa.fila()
atendendo = 'NENHUMA'

def on_connect(client, userdata, flags, rc):
	print('Connected with result code {0}'.format(rc))
	client.subscribe([('mesa1', 0),('mesa2',0), ('mesa3', 0)])

def on_message(client, userdata, msg):
    msg = msg.payload.decode("utf-8").split('|')
    mesa = msg[0]
    pronta = msg[1]
    distancia = float(msg[2])
    RFID = msg[3]
    peso = float(msg[4])
    print('{}: Pronta: {}, Distancia: {:03.0f} cm, RFID: {}, Peso: {:04.0f} g'.format(mesa, pronta, distancia, RFID, peso))

    if(mesa == 'MESA1'):
        print(mesa)
        global distancia1
        distancia1 = distancia
        global rfid1
        rfid1 = RFID
        global peso1
        peso1 = peso
        global anterior1
        anterior1 = pronta1
        global pronta1
        pronta1 = pronta
    elif(mesa == 'MESA2'):
        print(mesa)
        global distancia2
        distancia2 = distancia
        global rfid2
        rfid2 = RFID
        global peso2
        peso2 = peso
        global anterior2
        anterior2 = pronta2
        global pronta2
        pronta2 = pronta
    elif(mesa == 'MESA3'):
        print(mesa)
        global distancia3
        distancia3 = distancia
        global rfid3
        rfid2 = RFID
        global peso3
        peso3 = peso
        global anterior3
        anterior3 = pronta3
        global pronta3
        pronta3 = pronta
    #print(msg.payload.decode("utf-8").split(','))

def mqtt_thread():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('localhost', 1883, 60)
    client.loop_forever()

@app.route("/")
def html():
    return render_template('trayker.html')

@app.route("/API", methods=['GET'])
def index():
    resposta = {
        'mesa1': {
            'ultrassonico': distancia1,
            'rfid': rfid1,
            'peso': peso1,
            'pronta': pronta1
        },
        'mesa2': {
            'ultrassonico': distancia2,
            'rfid': rfid2,
            'peso': peso2,
            'pronta': pronta2
        },
        'mesa3': {
            'ultrassonico': distancia3,
            'rfid': rfid3,
            'peso': peso3,
            'pronta': pronta3
        }
    }
    return jsonify(resposta)

def agendamento():
	sleep(10)
	while True:
        print(fila_tarefa.get_fila())
		global fila_tarefa
		if(pronta1 != anterior1):
			if(pronta1 == '1'):
				fila_tarefa.insere('MESA1')
			else:
				if(atendendo != 'MESA1'):
					fila_tarefa.remove('MESA1')
		if(pronta2 != anterior2):
			if(pronta2 == '1'):
				fila_tarefa.insere('MESA2')
			else:
				if(atendendo != 'MESA2'):
					fila_tarefa.remove('MESA2')
		if(pronta3 != anterior3):
			if(pronta3 == '1'):
				fila_tarefa.insere('MESA3')
			else:
				if(atendendo != 'MESA3'):
					fila_tarefa.remove('MESA3')
		global atendendo
		if(atendendo == 'NENHUMA'):
			if(len(fila.get_fila) > 0):
				atendendo = fila_tarefa.pop



def flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

def teste():
    while True:
        sleep(10)
        print('{} {} {}'.format(distancia1, rfid1, peso1))
        print('{} {} {}'.format(distancia2, rfid2, peso2))
        print('{} {} {}'.format(distancia3, rfid3, peso3))

_thread.start_new_thread(teste, ())
_thread.start_new_thread(mqtt_thread, ())
# _thread.start_new_thread(agendamento, ())

flask()
