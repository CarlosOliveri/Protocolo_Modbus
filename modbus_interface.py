import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
#from pymodbus.client import ModbusSerialClient as ModbusClient
import pymodbus.client as ModbusClient
from pymodbus import pymodbus_apply_logging_config
import serial
import time

class ModbusApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('MODBUS Interface')
        
        self.layout = QVBoxLayout()
        
        #Entrada de texto para establecer puerto COM
        self.portLabel = QLabel('Puerto COM: ')
        self.layout.addWidget(self.portLabel)
        self.portBox = QLineEdit(self)
        self.layout.addWidget(self.portBox)
        
        #Entrada de texto para establecer baudios
        self.baudLabel = QLabel('Baudrate: ')
        self.layout.addWidget(self.baudLabel)
        self.baudBox = QLineEdit(self)
        self.layout.addWidget(self.baudBox)
        
        #Boton de conexion
        self.connectButton = QPushButton('Conectar', self)
        self.connectButton.clicked.connect(self.connect_toggle)
        self.layout.addWidget(self.connectButton)
        self.connected = False
        
        #Respuestas de conexion o Error
        self.connectedLabel = QLabel('No Conectado')
        self.connectedLabel.setObjectName("returnLabel")
        self.layout.addWidget(self.connectedLabel)

        self.msgLabel = QLabel('Mensaje a enviar: ')
        self.layout.addWidget(self.msgLabel)
        
        #Entrada de texto para mensaje a enviar
        self.msgBox = QLineEdit(self)
        self.layout.addWidget(self.msgBox)
        
        #Boton de enviar mensaje al puerto serial
        self.sendButton = QPushButton('Enviar', self)
        self.sendButton.clicked.connect(self.send_message)
        self.layout.addWidget(self.sendButton)
        
        #Respuesta de recepcion o error de envio
        self.responseLabel = QLabel('Respuesta: ')
        self.responseLabel.setObjectName("returnLabel")
        self.layout.addWidget(self.responseLabel)
        
        #Titulo de barra de progreso
        self.pBarLabel = QLabel('Estado del potenciometro: ')
        self.layout.addWidget(self.pBarLabel)
        self.pbar = QProgressBar(self)
        self.pbar.setObjectName("progresBar")
        self.layout.addWidget(self.pbar)
        #self.pbar.setGeometry(100, 100, 225, 50)
        #self.doAction()
        
        self.setLayout(self.layout)
        self.client = None
        
        self.styleGeneral()
        
        # Configuración del temporizador para actualizar el valor periódicamente
        self.timer = QTimer(self)
        #self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.readAnalog)
        
        
    def bolear(self,x):
        if x == 'true' or x == 'True' or int(x) == 1:
            return True
        elif x == 'false' or x == 'False' or int(x) == 0:
            return False
        else:
            self.responseLabel.setText('Formato de mensaje no valido')
            self.responseLabel.setObjectName("errorReturnLabel")
            self.styleGeneral()  

    #funcion para enviar mensaje al puerto serial
    def send_message(self):
        if self.client and self.client.is_socket_open():
            message = self.msgBox.text()
            message = message.split()
            try:
                message[1] = self.bolear(message[1])
                print('mensaje enviado: ', message)
                result = self.client.write_coil(int(message[0]),message[1], slave = 1)
                if result.isError():
                    self.responseLabel.setText('Error al enviar el mensaje')
                    print(result)
                    self.responseLabel.setObjectName("errorReturnLabel")
                    self.styleGeneral()
                else:
                    self.responseLabel.setText('Mensaje enviado correctamente')
                    print(result)
                    self.responseLabel.setObjectName("okReturnLabel")
                    self.styleGeneral()
            except Exception as e:
                self.responseLabel.setText(f'Error: {str(e)}')
                self.responseLabel.setObjectName("errorReturnLabel")
                self.styleGeneral()
        else:
            self.responseLabel.setText('No conectado')
            self.responseLabel.setObjectName("NCReturnLabel")
            self.styleGeneral()
        #self.readAnalog()
        #self.timer.start(1000)
    
    #Funcion para conectar al cliente
    def connect_modbus(self):
        pass
        port = self.portBox.text()
        baudrate = int(self.baudBox.text())
        self.client = ModbusClient.ModbusSerialClient(method='rtu', port=port, baudrate=baudrate,bytesize= 8, parity= "N", stopbits=1,timeout=1)
        if self.client.connect():
            self.connectedLabel.setText(f'Conectado a {port} a {baudrate} baudios')
            self.connectedLabel.setObjectName("okReturnLabel")
            self.styleGeneral()
        else:
            self.connectedLabel.setText('Error al conectar')
            self.connectedLabel.setObjectName("errorReturnLabel")
            self.styleGeneral()
        time.sleep(2)
        self.timer.start(100)  # Actualizar cada 1 segundo
        
    def connect_toggle(self):
        if not self.connected:
            self.connect_modbus()
            self.connectButton.setText("Desconectar")
            self.connected = True
        else:
            self.timer.stop()
            self.client.close()
            self.connectButton.setText("Conectar")
            self.connected = False
            self.connectedLabel.setText('No conectado')
            self.connectedLabel.setObjectName("returnLabel")
            self.styleGeneral()
            
    
    def disconnect_modbus(self):
        self.client.close()
        
    def readAnalog(self):
        #response = self.client.read_holding_registers(0, 1)
        try:
            response = self.client.read_holding_registers(address = 0, slave = 1)
            self.doAction(response.registers[0])
            """ if not response.isError():
                pot_value = response.registers[0]
                print(f'Valor del potenciómetro: {pot_value}')
            else:
                print(f'Error al leer el registro: {response}') """
        except Exception as error:
            print('Error en la lectura: ',error)
    
    def doAction(self,val):
        # setting value to progress bar 
        val = 100*val/65535
        self.pbar.setValue(int(val)) 
        print(int(val)  )
            
    def styleGeneral(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                font-size: 14px;
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            #returnLabel{
                background-color: #4CAF50;
                padding: 10px;
                border-radius: 5px;
            }
            #errorReturnLabel{
                background-color: #900000;
                padding: 10px;
                border-radius: 5px;
            }
            #okReturnLabel{
                background-color: #45a049;
                padding: 10px;
                border-radius: 5px;
            }
            #NCReturnLabel{
                background-color: #909000;
                padding: 10px;
                border-radius: 5px;
            }
            #progresBat{
                margin-Top: 20px;
            }
        """)
            
#Funcion principal 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ModbusApp()
    ex.show()
    sys.exit(app.exec_())
