import os
import queue
import logging
import datetime
import paho.mqtt.client as mqtt
import _thread
from time import sleep
from flask import Flask, jsonify, render_template
from flask_cors import CORS

import fila_tarefa
import serial

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(20)
CORS(app)

try:
    global bs
    bs = serial.Serial("/dev/rfcomm0", baudrate=9600)
    print('Bluetooth conectado.')
except OSError as er:
    print('Falha ao conectar o Bluetooth')

prontas = ['0', '0', '0', '0']
updated = [0, 0, 0, 0]
vida_tt = [0, 0, 0, 0]

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
    global prontas
    if(mesa == 'MESA1'):
        #print(mesa)
        global distancia1
        distancia1 = distancia
        global rfid1
        rfid1 = RFID
        global peso1
        peso1 = peso
        global pronta1
        global anterior1
        anterior1 = pronta1
        pronta1 = pronta
        prontas[1] = pronta
        global updated
        updated[1] = 1

    elif(mesa == 'MESA2'):
        #print(mesa)
        global distancia2
        distancia2 = distancia
        global rfid2
        rfid2 = RFID
        global peso2
        peso2 = peso
        global pronta2
        global anterior2
        anterior2 = pronta2
        pronta2 = pronta
        prontas[2] = pronta
        global updated
        updated[2] = 1

    elif(mesa == 'MESA3'):
        #print(mesa)
        global distancia3
        distancia3 = distancia
        global rfid3
        rfid3 = RFID
        global peso3
        peso3 = peso
        global pronta3
        global anterior3
        anterior3 = pronta3
        pronta3 = pronta
        prontas[3] = pronta
        global updated
        updated[3] = 1

    agendamento()

def mqtt_thread():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('localhost', 1883, 60)
    client.loop_forever()

@app.route("/")
def html():
    return render_template('trayker-2.html')

@app.route("/API", methods=['GET'])
def index():
    resposta = {
        'mesa1': {
            'ultrassonico': distancia1,
            'rfid': rfid1,
            'peso': peso1,
            'pronta': pronta1,
            'idade': vida_tt[1]
        },
        'mesa2': {
            'ultrassonico': distancia2,
            'rfid': rfid2,
            'peso': peso2,
            'pronta': pronta2,
            'idade': vida_tt[2]
        },
        'mesa3': {
            'ultrassonico': distancia3,
            'rfid': rfid3,
            'peso': peso3,
            'pronta': pronta3,
            'idade': vida_tt[3]
        },
        'fila': fila.get_fila(),
        'atendendo': atendendo
    }
    return jsonify(resposta)

def agendamento():
#    while True:
    global fila
    if(pronta1 != anterior1):
        if(pronta1 == '1' and atendendo != 'MESA1' and fila.presente('MESA1') == False):
            print('Fila: Inserindo mesa 1')
            fila.insere('MESA1')
            print(fila.get_fila())
        elif(fila.presente('MESA1') == True):
#            if(atendendo != 'MESA1'):
            print('Fila: Removendo mesa 1')
            fila.remove('MESA1')
            print(fila.get_fila())
    if(pronta2 != anterior2):
        if(pronta2 == '1' and atendendo != 'MESA2' and fila.presente('MESA2') == False):
            print('Fila: Inserindo mesa 2')
            fila.insere('MESA2')
            print(fila.get_fila())
        elif(fila.presente('MESA2') == True):
#            if(atendendo != 'MESA2'):
            print('Fila: Removendo mesa 2')
            fila.remove('MESA2')
            print(fila.get_fila())
    if(pronta3 != anterior3 and atendendo != 'MESA3' and fila.presente('MESA3') == False):
        if(pronta3 == '1'):
            print('Fila: Inserindo mesa 3')
            fila.insere('MESA3')
            print(fila.get_fila())
        elif(fila.presente('MESA3') == True):
#            if(atendendo != 'MESA3'):
            print('Removendo mesa 3')
            fila.remove('MESA3')
            print(fila.get_fila())
#    if(atendendo == 'NENHUMA'):
#        if(len(fila.get_fila()) > 0):
#            atendendo = fila.pop

def teste():
    while True:
        sleep(3)
        #print('1. {} {} {}'.format(distancia1, rfid1, peso1))
        #print('2. {} {} {}'.format(distancia2, rfid2, peso2))
        #print('3. {} {} {}'.format(distancia3, rfid3, peso3))
        #print(fila.get_fila())

        global vida_tt
        for i in range(1, 4):
            if (updated[i] == 1):
                vida_tt[i] = 0
                global updated
                updated[i] = 0
            elif (vida_tt[i] < 10):
                vida_tt[i] += 1

def flask():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=8080, debug=False)

def filter():
    data = bs.read()
    if(data.match() i

def read_blue():
    data = bs.read()
    print("Valor lido no bluetooth: {0}".format(data))
    if(data == 'K' or data == 'A' or data == ''
    # iniciativa
    if(data == b'K'): # robo na cozinha E livre
        global atendendo
        atendendo = 'NENHUMA'

    elif(data == b'A'): # robo avisa que ira tirar a bandeja
        mesa_num = bs.read() # aguarda que o robo confirme numero da bandeja
        print("Valor lido no bluetooth: {0}".format(mesa_num))
        print('prontas[{0}]: {1}'.format(mesa_num, prontas[int(mesa_num)]))
        if (prontas[int(mesa_num)] == '1'):
            bs.write(b'B') # confirma
            confirma = bs.read()
            print('Recebido: {}'.format(confirma))
            if(confirma == b'B'):
                print('Mesa {} confirmada.'.format(mesa_num))
                confirma = bs.read()
                if (confirma == b'S'): # robo conseguiu tirar
                    print('Bandeja da Mesa {} removida com sucesso.'.format(mesa_num))
                elif(confirma == b'N'):
                    print('Falhou em retirar bandeja da Mesa {}. Readicionando na fila.'.format(mesa_num))
                    fila.insere('MESA{}'.format(mesa_num.decode("utf-8")))
                    print('Fila: {}'.format(fila.get_fila()))
                else:
                    print('Valor invalido recebido no Bluetooth: {}'.format(confirma))
        else:
            bs.write(b'0') # cancela
            confirma = bs.read()
            print('Recebido: {}'.format(confirma))
            if(confirma == b'0'):
                print('Mesa {} cancelada.'.format(mesa_num))

    # resposta
    elif(data == atendendo[4]): # Traykson ecoa confirmando recebimento
        a = 0 # Este eh o fluxo desejado
    else:
        a = 0 # Estah com algum problema!

def main():
    global atendendo
    atendendo = 'INICIALIZANDO...'
    while (atendendo == 'INICIALIZANDO...'):
        #bs.write(b'T')
        #print('Enviei a letra T')
        read_blue()

    while True:
        global atendendo
        if (atendendo == 'NENHUMA'):
            if(len(fila.get_fila()) > 0):
                atendendo = fila.pop()
                bs.write(bytes(atendendo[4], 'utf-8'))
                print('Enviando novo objetivo: {0}'.format(atendendo[4]))
                read_blue()
        else:
            read_blue()

_thread.start_new_thread(teste, ())
_thread.start_new_thread(mqtt_thread, ())
_thread.start_new_thread(main, ())

flask()
