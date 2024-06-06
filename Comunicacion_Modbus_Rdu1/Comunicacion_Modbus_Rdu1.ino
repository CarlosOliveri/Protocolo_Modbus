#include <ModbusMaster.h>

// Instancia del objeto ModbusMaster
ModbusMaster node;

// Pin para controlar un LED (por ejemplo)
const int ledPin = 13;

void preTransmission() {
  // Puedes usar esta función para habilitar la transmisión
  // digitalWrite(SSerialTxControl, HIGH);
}

void postTransmission() {
  // Puedes usar esta función para deshabilitar la transmisión
  // digitalWrite(SSerialTxControl, LOW);
}

void setup() {
  // Inicializar comunicación serial
  Serial.begin(9600);

  // Inicializar el pin del LED como salida
  pinMode(ledPin, OUTPUT);

  // Comunicar el objeto ModbusMaster con el puerto serial
  node.begin(1, Serial);  // El ID del esclavo es 1

  // Configurar las funciones de pre y post transmisión
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);
}

void loop() {
  uint8_t result;
  uint16_t data[2];

  // Leer el valor del registro 0
  result = node.readHoldingRegisters(0, 1);
  if (result == node.ku8MBSuccess) {
    uint16_t value = node.getResponseBuffer(0);
    if (value == 1) {
      digitalWrite(ledPin, HIGH);  // Encender LED
    } else {
      digitalWrite(ledPin, LOW);   // Apagar LED
    }
    node.setTransmitBuffer(0, 12345);  // Valor de confirmación
    node.writeSingleRegister(1, 12345);
    // Escribir una confirmación en el registro 1
  }

  delay(1000);  // Esperar 1 segundo antes de la próxima iteración
}

