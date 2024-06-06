import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
#from pymodbus.client import ModbusSerialClient as ModbusClient
import pymodbus.client as ModbusClient
from pymodbus import pymodbus_apply_logging_config
import serial

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
        self.connectButton.clicked.connect(self.connect_modbus)
        self.layout.addWidget(self.connectButton)
        
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
        
        self.setLayout(self.layout)
        self.client = None
        
        self.styleGeneral()

    #funcion para enviar mensaje al puerto serial
    def send_message(self):
        if self.client and self.client.is_socket_open():
            message = self.msgBox.text()
            try:
                result = self.client.write_coil(1, True, slave = 1)
                if result.isError():
                    self.responseLabel.setText('Error al enviar el mensaje',result)
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
        """)
            
#Funcion principal 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ModbusApp()
    ex.show()
    sys.exit(app.exec_())
