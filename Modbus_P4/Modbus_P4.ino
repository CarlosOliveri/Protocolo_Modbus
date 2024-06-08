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
//definicion de coils del esclavo
int coil0 = 12;
int coil1 = 11;
int coil2 = 10;

void setup() {
  //Configuracion del Server=Esclavo
  ModbusRTUServer.begin(1,9600);
  //Configuracion de 3 coils para el esclavo
  ModbusRTUServer.configureCoils(0,3);
  //configuracion del holding register para el esclavo
  ModbusRTUServer.configureHoldingRegisters(0,1);
  //
  pinMode(coil0, OUTPUT);
  pinMode(coil1, OUTPUT);
  pinMode(coil2, OUTPUT);
  
  // tiramos a cero la salida
  digitalWrite(coil0, LOW);
  digitalWrite(coil1, LOW);
  digitalWrite(coil2, LOW);

}

void loop() {
  // asignacion de valor del puerto analogico A0 al holding Register configurado
  int val = analogRead(A0);
  //Serial.println(val);
  val = map(val, 0, 1023, 0, 65535); // Escala a 16 bits
  ModbusRTUServer.holdingRegisterWrite(0, val);
  
  //Lee las solicitudes del maestro 
  ModbusRTUServer.poll();
  //verificar el estado del Coil0
  if(ModbusRTUServer.coilRead(0))
    digitalWrite(coil0, HIGH);
  else
    digitalWrite(coil0, LOW);
  //verificar el estado del Coil1
  if(ModbusRTUServer.coilRead(1))
    digitalWrite(coil1, HIGH);
  else
    digitalWrite(coil1, LOW);
    //verificar el estado del Coil2
  if(ModbusRTUServer.coilRead(2))
    digitalWrite(coil2, HIGH);
  else
    digitalWrite(coil2, LOW);
}
