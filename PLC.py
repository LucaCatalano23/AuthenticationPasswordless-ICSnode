from pyModbusTCP.server import ModbusServer
import threading
from time import sleep

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 502

# Definisco la classe PLC
class PLC:
    def __init__(self):
        self.server = ModbusServer(SERVER_HOST, SERVER_PORT, no_block=True)
        self.water_level = 0  # Livello dell'acqua nel tank
        self.flow_rate = 5  # Flusso d'acqua in unità al secondo
        self.drain_rate = 10 # Velocità di deflusso dell'acqua in unità al secondo
        self.limit = 1000  # Limite massimo del tank
        self.flow_active = False  # Flag per indicare se il flusso è attivo
        self.drain_active = False  # Flag per indicare se il deflusso è attivo
        self.set_registers()

    def set_registers(self):
        self.server.data_bank.set_holding_registers(0, [self.water_level])
        self.server.data_bank.set_holding_registers(1, [self.flow_rate])
        self.server.data_bank.set_holding_registers(2, [self.drain_rate])
        
    # Funzione per avviare il flusso d'acqua
    def start_flow(self):
        while self.water_level < self.limit and self.flow_active:
            self.water_level += 1
            sleep(1/self.flow_rate)
        self.flow_active = False

    # Funzione per fermare il flusso d'acqua
    def stop_flow(self):
        self.flow_active = False

    # Funzione per far defluire l'acqua dal tank
    def start_drain(self):
        while self.water_level > 0 and self.drain_active:
            self.water_level -= 1
            sleep(1/self.drain_rate)
        self.drain_active = False
        
    # Funzione per fermare il deflusso dell'acqua
    def stop_drain(self):
        self.drain_active = False

    # Funzione per impostare la velocità di flusso
    def set_flow_rate(self, flow_rate):
        self.flow_rate = flow_rate
    
    # Funzione per impostare la velocità di deflusso 
    def set_drain_rate(self, drain_rate):
        self.drain_rate = drain_rate
        
    def main(self):      
        
        try:
            self.server.start()
            while True:
                # Controllo lo stato dei coil per avviare o fermare il flusso e il deflusso
                self.flow_active = self.server.data_bank.get_coils(1)[0]
                if self.flow_active:
                    threading.Thread(target=self.start_flow).start()
                else:   
                    threading.Thread(target=self.stop_flow).start()
                    
                self.drain_active = self.server.data_bank.get_coils(2)[0]
                if self.drain_active:
                    threading.Thread(target=self.start_drain).start()
                else:
                    threading.Thread(target=self.stop_drain).start()
                
                # Controllo se la velocità di flusso o deflusso è stata modificata ed aggiorno i valori
                flow_rate = self.server.data_bank.get_holding_registers(1)[0]
                if flow_rate != self.flow_rate:
                    self.set_flow_rate(flow_rate)
                drain_rate = self.server.data_bank.get_holding_registers(2)[0]
                if drain_rate != self.drain_rate:
                    self.set_drain_rate(drain_rate)
                    
                # Aggiorno il valore del livello dell'acqua
                self.server.data_bank.set_holding_registers(0,[self.water_level])
                print(self.water_level)
           
                sleep(0.5)
        except Exception as e:
            print(e)
            self.server.stop()
            
if __name__ == "__main__":
    # Creo un'istanza del PLC e avvio la funzione main
    plc = PLC()
    plc.main()



