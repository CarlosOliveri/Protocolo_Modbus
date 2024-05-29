#include <ModbusMaster.h>

// Crear una instancia del objeto ModbusMaster
ModbusMaster node;

void setup() {
  // Inicializar la comunicación serie a 9600 baudios
  Serial.begin(9600);

  // Inicializar el objeto ModbusMaster
  node.begin(1, Serial);
}

void loop() {
  // Intentar leer desde la dirección 0x00 de los registros de entrada
  uint8_t result;
  result = node.readInputRegisters(0x00, 1);

  // Si la lectura fue exitosa, imprimir el valor leído
  if (result == node.ku8MBSuccess) {
    Serial.print("Lectura de registro: ");
    Serial.println(node.getResponseBuffer(0x00));
  } else {
    Serial.print("Error de comunicación: ");
    Serial.println(result, HEX);
  }

  // Esperar 1 segundo antes de la siguiente lectura
  delay(1000);
}
