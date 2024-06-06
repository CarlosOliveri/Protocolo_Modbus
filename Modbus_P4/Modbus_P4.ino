/*
Facultad de Ingenieria de la Universidad Nacional de Asuncion
Asignatura: Proyecto 4
Programa de demostracion del protocolo de comunicacion serial MODBUS RTU
Autor: Francisco Nazario Duarte Rodriguez
Ciclo: 1/2024
Ref.: https://docs.arduino.cc/learn/communication/modbus/
Ref.: https://www.arduino.cc/reference/en/libraries/arduinomodbus/
*/
#include <ArduinoModbus.h>
void setup() {
 //Configuracion del Server=Esclavo
 ModbusRTUServer.begin(1,9600);
 //Configuracion de 3 coils para el esclavo
 ModbusRTUServer.configureCoils(0,3);
 //configuracion del holding register para el esclavo
 ModbusRTUServer.configureHoldingRegisters(0,1);
 //
 pinMode(13, OUTPUT);
 pinMode(12, OUTPUT);
 pinMode(11, OUTPUT);
 //
 digitalWrite(13, LOW);
 digitalWrite(12, LOW);
 digitalWrite(11, LOW);

}

void loop() {
// asignacion de valor del puerto analogico A0 al holding Register configurado
int val = analogRead(A0);
ModbusRTUServer.holdingRegisterWrite(0, val);
//Master pregunta 
ModbusRTUServer.poll();
//verificar el estado del Coil0
if(ModbusRTUServer.coilRead(0))
  digitalWrite(13, HIGH);
else
  digitalWrite(13, LOW);
//verificar el estado del Coil1
if(ModbusRTUServer.coilRead(1))
  digitalWrite(12, HIGH);
else
  digitalWrite(12, LOW);
  //verificar el estado del Coil2
if(ModbusRTUServer.coilRead(2))
  digitalWrite(13, HIGH);
else
  digitalWrite(13, LOW);


}
