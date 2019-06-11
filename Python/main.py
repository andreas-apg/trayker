import os
import queue
from time import sleep
from flask import Flask, jsonify
from flask_cors import CORS

from mqtt_mesaX import mqtt_mesa

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(20)
CORS(app)

mesa1_distancia = 100
mesa1_rfid = [10,10,10,10]
mesa1_peso = 200

@app.route("/", methods=['GET'])
def index():
    resposta = {
        'mesa1': {
            'ultrassonico': mesa1_distancia,
            'rfid': mesa1_rfid,
            'peso': mesa1_peso
#        },
#        'mesa2': {
#            'ultrassonico': mesa2.distancia,
#            'rfid': mesa2.rfid,
#            'peso': mesa2.peso
#        },
#        'mesa3': {
#            'ultrassonico': mesa3.distancia,
#            'rfid': mesa3.rfid,
#            'peso': mesa3.peso
        }
    }
    return jsonify(resposta)

def flask():
    app.run(host='0.0.0.0', port=8080, debug=True)

if __name__ == '__main__':
#    q = queue.Queue(maxsize=0)
#    q.put(mesa)
#    while not q.empty():
#        bluetooth(mesa)
    flask()

# while True:
#     pass
