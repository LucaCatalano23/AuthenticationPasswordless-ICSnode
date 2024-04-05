from flask import Flask, request, render_template, jsonify
from pyModbusTCP.client import ModbusClient
from Configs import TAG, Controllers

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
        client.write_single_coil(TAG.TAG_LIST[TAG.TANK_FLOW_ACTIVE]["id"], value)
    if name == "drain":
        client.write_single_coil(TAG.TAG_LIST[TAG.TANK_DRAIN_ACTIVE]["id"], value)
    
    return 'OK', 200

# Funzione che mi permette di monitorare il livello dell'acqua, il flusso e il deflusso
@app.route('/monitor', methods=['GET'])
def monitor():
    level = client.read_holding_registers(TAG.TAG_LIST[TAG.TANK_LEVEL]["id"])[0]
    flow_rate = client.read_holding_registers(TAG.TAG_LIST[TAG.TANK_FLOW_RATE]["id"])[0]
    drain_rate = client.read_holding_registers(TAG.TAG_LIST[TAG.TANK_DRAIN_RATE]["id"])[0]
    values = {'level': level, 'flow_rate': flow_rate, 'drain_rate': drain_rate}
    return jsonify(values)

# Funzione per aggiornare la velocità di flusso 
@app.route('/flowUpdate', methods=['POST'])
def flowUpdate():
    data = request.json
    value = data.get('value')
    client.write_single_register(TAG.TAG_LIST[TAG.TANK_FLOW_RATE]["id"], int(value))
    return 'OK', 200

# Funzione per aggiornare la velocità di deflusso
@app.route('/drainUpdate', methods=['POST'])
def drainUpdate():
    data = request.json
    value = data.get('value')
    client.write_single_register(TAG.TAG_LIST[TAG.TANK_DRAIN_RATE]["id"], int(value))
    return 'OK', 200

if __name__ == "__main__":
    try:
        client = ModbusClient(Controllers.PLC_CONFIG[1]["ip"], Controllers.PLC_CONFIG[1]["port"])
        client.open()
        app.run(debug=True)
    except Exception as e:
        print(f"Errore durante la comunicazione con il server: {e}")
    finally:
        client.close()