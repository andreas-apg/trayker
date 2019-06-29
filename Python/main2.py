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

num_mesas = 3
pronta_array =       ['0', '0', '0', '0']
peso_array =         ['0', '0', '0', '0']
distancia_array =    ['0', '0', '0', '0']
anterior_array =    ['0', '0', '0', '0']
rfid_array =         ['[0, 0, 0, 0]', '[0, 0, 0, 0]', '[0, 0, 0, 0]', '[0, 0, 0, 0]']
updated_array = [0, 0, 0, 0]
vida_tt_array = [0, 0, 0, 0]

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
    global pronta_array
    global peso_array
    global distancia_array
    global anterior_array
    global rfid_array
    global updated_array
    print('Mensagem de: {}'.format(mesa))
    #print('distancia_array')
    distancia_array[int(mesa[4])] = distancia
    #print('rfid_array')
    rfid_array[int(mesa[4])] = RFID
    #print('peso_array')
    peso_array[int(mesa[4])] = peso
    #print('anterior_array')
    anterior_array[int(mesa[4])] = pronta_array[int(mesa[4])]
    #print('pronta_array')
    if(int(pronta) < 2):
        pronta_array[int(mesa[4])] = pronta
        print('Pronta = {}. Dados vieram da funcao de estado.'.format(pronta))
    else:
        print('Pronta == Dados vieram da funcao de leitura.')
    #print('updated_array')
    updated_array[int(mesa[4])] = 1
    #print('agendando')
    agendamento()

def mqtt_thread():
    client = mqtt.Client(clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('localhost', 1883, 60)
    client.loop_forever()

@app.route("/")
def html():
    return render_template('trayker-2.html')

@app.route("/API", methods=['GET'])
def index():
    global distancia_array
    global rfid_array
    global peso_array
    global pronta_array
    global vida_tt_array
    resposta = {
        'mesa1': {
            'ultrassonico': distancia_array[1],
            'rfid': rfid_array[1],
            'peso': peso_array[1],
            'pronta': pronta_array[1],
            'idade': vida_tt_array[1]
        },
        'mesa2': {
            'ultrassonico': distancia_array[2],
            'rfid': rfid_array[2],
            'peso': peso_array[2],
            'pronta': pronta_array[2],
            'idade': vida_tt_array[2]
        },
        'mesa3': {
            'ultrassonico': distancia_array[3],
            'rfid': rfid_array[3],
            'peso': peso_array[3],
            'pronta': pronta_array[3],
            'idade': vida_tt_array[3]
        },
        'fila': fila.get_fila(),
        'atendendo': atendendo
    }
    return jsonify(resposta)

# funcao que realiza o agendamento de mesas para a fila de tarefas
def agendamento():
    global fila
    global pronta_array
    global anterior_array
    global num_mesas
    for i in range(1, num_mesas+1):
        if(pronta_array[i] != anterior_array[i]):
            if(pronta_array[i] == '1' and atendendo != ('MESA{}'.format(i)) and fila.presente('MESA{}'.format(i)) == False):
                print('Fila: Inserindo mesa {}'.format(i))
                fila.insere('MESA{}'.format(i))
                print(fila.get_fila())
            elif(fila.presente('MESA{}'.format(i)) == True):
                print('Fila: Removendo mesa {}'.format(i))
                fila.remove('MESA{}'.format(i))
                print(fila.get_fila())

    #if(pronta_array[1] != anterior_array[1]):
    #    if(pronta_array[1] == '1' and atendendo != 'MESA1' and fila.presente('MESA1') == False):
    #        print('Fila: Inserindo mesa 1')
    #        fila.insere('MESA1')
    #        print(fila.get_fila())
    #    elif(fila.presente('MESA1') == True):
    #        print('Fila: Removendo mesa 1')
    #        fila.remove('MESA1')
    #        print(fila.get_fila())
    #if(pronta_array[2] != anterior_array[2]):
    #    if(pronta_array[2] == '1' and atendendo != 'MESA2' and fila.presente('MESA2') == False):
    #        print('Fila: Inserindo mesa 2')
    #        fila.insere('MESA2')
    #        print(fila.get_fila())
    #    elif(fila.presente('MESA2') == True):
    #        print('Fila: Removendo mesa 2')
    #        fila.remove('MESA2')
    #        print(fila.get_fila())
    #if(pronta_array[3] != anterior_array[3] and atendendo != 'MESA3' and fila.presente('MESA3') == False):
    #    if(pronta_array[3] == '1'):
    #        print('Fila: Inserindo mesa 3')
    #        fila.insere('MESA3')
    #        print(fila.get_fila())
    #    elif(fila.presente('MESA3') == True):
    #        print('Removendo mesa 3')
    #        fila.remove('MESA3')
    #        print(fila.get_fila())

# funcao utilizada para determinar quando uma mesa esta sem
# atualizar ha muito tempo
def mesa_ociosa():
    while True:
        sleep(3)
        global vida_tt_array
        global updated_array
        for i in range(1, 4):
            if (updated_array[i] == 1):
                vida_tt_array[i] = 0
                updated_array[i] = 0
            elif (vida_tt_array[i] < 10):
                vida_tt_array[i] += 1

def flask():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=8080, debug=False)

def read_blue():
    data = bs.read()
    print("Valor lido no bluetooth: {0}".format(data))
    global atendendo
    # iniciativa
    if(data == b'K'): # robo na cozinha E livre
        atendendo = 'NENHUMA'

    elif(data == b'A'): # robo avisa que ira tirar a bandeja
        mesa_num = bs.read() # aguarda que o robo confirme numero da bandeja
        print("Valor lido no bluetooth: {0}".format(mesa_num))
        print('pronta_array[{0}]: {1}'.format(mesa_num, pronta_array[int(mesa_num)]))
        if (pronta_array[int(mesa_num)] == '1'):
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
        if (atendendo == 'NENHUMA'):
            if(len(fila.get_fila()) > 0):
                atendendo = fila.pop()
                bs.write(bytes(atendendo[4], 'utf-8'))
                print('Enviando novo objetivo: {0}'.format(atendendo[4]))
                read_blue()
        else:
            read_blue()

sleep(5)
_thread.start_new_thread(mesa_ociosa, ())
_thread.start_new_thread(mqtt_thread, ())
_thread.start_new_thread(main, ())

flask()

