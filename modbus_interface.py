import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
#from pymodbus.client import ModbusSerialClient as ModbusClient
import pymodbus.client as ModbusClient
from pymodbus import pymodbus_apply_logging_config
import serial
import time
import logging

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
        
        self.setLayout(self.layout) # aplicar posicionamiento de elementos
        self.client = None #objeto cliente inicializado como vacio
        
        self.styleGeneral() # aplicar estilos
        
        # Configuración del temporizador para actualizar el valor periódicamente
        self.timer = QTimer(self)
        #self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.readAnalog)
        
        
    def bolear(self,x): #metodo para convertir una variable string en boleano
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
        self.setup_logging() #Configuracion del logger para recuperar la trama
        if self.client and self.client.is_socket_open():
            message = self.msgBox.text()
            message = message.split() #Convierte a un vector de los caract6eres recibidos
            try:
                message[1] = self.bolear(message[1]) # convierte a boleano el segundo caracter
                print('mensaje enviado: ', message)
                result = self.client.write_coil(int(message[0]),message[1], slave = 1) # hace request al esclavo
                if result.isError(): #verificar errores
                    self.responseLabel.setText('Error al enviar el mensaje')
                    print(result)
                    self.responseLabel.setObjectName("errorReturnLabel")
                    self.styleGeneral()
                else:
                    mensaje = self.message_filter.get_sent_message()
                    print("mensaje enviado",mensaje) #Mostrar Trama enviad en el terminal y en interface
                    self.responseLabel.setText(f'Mensaje enviado correctamente: {str(mensaje)}')
                    print(result)
                    self.responseLabel.setObjectName("okReturnLabel")
                    self.styleGeneral()
    
            except Exception as e: #captura excepciones de envio
                self.responseLabel.setText(f'Error: {str(e)}')
                self.responseLabel.setObjectName("errorReturnLabel")
                self.styleGeneral()
        else:
            self.responseLabel.setText('No conectado')
            self.responseLabel.setObjectName("NCReturnLabel")
            self.styleGeneral()
    
    #Funcion para conectar al cliente
    def connect_modbus(self):
        port = self.portBox.text()
        baudrate = int(self.baudBox.text())
        # Se instancia el objeto cliente modbus
        self.client = ModbusClient.ModbusSerialClient(method='rtu', port=port, baudrate=baudrate,bytesize= 8, parity= "N", stopbits=1,timeout=1)
        #se establece conexion con el esclavo y se valida la respuesta de la conexion
        if self.client.connect():
            self.connectedLabel.setText(f'Conectado a {port} a {baudrate} baudios')
            self.connectedLabel.setObjectName("okReturnLabel")
            self.styleGeneral()
        else:
            self.connectedLabel.setText('Error al conectar')
            self.connectedLabel.setObjectName("errorReturnLabel")
            self.styleGeneral()
        #Se espera 2 segundo para establecer conexion correctamente
        time.sleep(2)
        self.timer.start(100)  # se inicializa el contador enlazado a la lectura del holding register encargado de
        #actualizar los valores del la barra de progreso cada 100 ms
    
    #cambia la funcion que se ejecuta cuando el enlace esta en linea o no
    #cuando esta desconectado se ejecuta conectar(), y cuando esta conectado se ejecuta desconectar()
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
            
    #Desconectarse del puerto serial
    def disconnect_modbus(self):
        self.client.close()
    
    #Lectura del holding register que almacena las lecturas del potenciometro en el esclavo
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
        # Se setea el valor de la barra de progreso
        val = 100*val/65535
        self.pbar.setValue(int(val)) 
        #print(int(val)  )
    
########################################################################################
#Todo este bloque se encarga de recuperar la trama generada antes del envio
    def setup_logging(self):
        self.log_handler = logging.StreamHandler(sys.stdout)
        self.log_handler.setLevel(logging.DEBUG)
        self.log_handler.setFormatter(self.CustomFormatter())

        self.logger = logging.getLogger("pymodbus")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.log_handler)

        # Añadir el filtro para mostrar solo las líneas que contienen "SEND:"
        self.message_filter = self.MessageFilter()
        self.log_handler.addFilter(self.message_filter)
        

    class CustomFormatter(logging.Formatter):
        def format(self, record):
            return record.msg

    class MessageFilter(logging.Filter):
        def __init__(self):
            super().__init__()
            self.lastMessage = None
            self.sent_message = None
            
        def filter(self, record):
            if "SEND:" in record.msg:
                if record.msg == self.lastMessage:
                    pass
                else:
                    #print(record.msg)
                    self.lastMessage = record.msg
                    self.sent_message = self.lastMessage
                    return self.sent_message #Imprime en la terminal
            return False
        def get_sent_message(self):
            message = self.sent_message
            #self.sent_message = None  # Vacía la variable después de acceder a ella
            return message
########################################################################################
    
    #definicion de Estilos
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
