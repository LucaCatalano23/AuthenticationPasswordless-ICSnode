from flask import Flask, request, render_template, jsonify
from pyModbusTCP.client import ModbusClient

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 502

app = Flask(__name__, static_url_path='/static' , static_folder='static')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Funzione per controllare avvio/arresto del flusso/deflusso d'acqua
@app.route('/control', methods=['POST'])
def control():
    data = request.json
    print(data)
    name = data.get('name')
    value = data.get('value')
    
    if name == "flow":
        client.write_single_coil(1, value)
    if name == "drain":
        client.write_single_coil(2, value)
    
    return 'OK', 200

# Funzione che mi permette di monitorare il livello dell'acqua, il flusso e il deflusso
@app.route('/monitor', methods=['GET'])
def monitor():
    level = client.read_holding_registers(0)[0]
    flow_rate = client.read_holding_registers(1)[0]
    drain_rate = client.read_holding_registers(2)[0]
    values = {'level': level, 'flow_rate': flow_rate, 'drain_rate': drain_rate}
    return jsonify(values)

# Funzione per aggiornare la velocità di flusso 
@app.route('/flowUpdate', methods=['POST'])
def flowUpdate():
    data = request.json
    value = data.get('value')
    client.write_single_register(1, int(value))
    return 'OK', 200

# Funzione per aggiornare la velocità di deflusso
@app.route('/drainUpdate', methods=['POST'])
def drainUpdate():
    data = request.json
    value = data.get('value')
    client.write_single_register(2, int(value))
    return 'OK', 200

if __name__ == "__main__":
    try:
        client = ModbusClient(SERVER_HOST, SERVER_PORT)
        client.open()
        app.run(debug=True)
    except Exception as e:
        print(f"Errore durante la comunicazione con il server: {e}")
    finally:
        client.close()