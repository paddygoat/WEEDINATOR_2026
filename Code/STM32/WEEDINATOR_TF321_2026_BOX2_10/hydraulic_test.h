
/*
 * Board is STM 144 Nucleo H723ZG
 * ls sudo /dev/tty*
 * sudo usermod -a -G dialout <username>
 * Connect STM board
 * ls sudo /dev/tty*
 * sudo chmod 777 /dev/ttyACM0
 * restart
 */

#include <Arduino.h>
#include "pins.h"

int count = 0;

void setup()
{
  setUpPins();

  buzz();
  buzz();

  digitalWrite(LED_PIN_GREEN, !digitalRead(LED_PIN_GREEN));
  delay(100);
  digitalWrite(LED_PIN_BLUE, !digitalRead(LED_PIN_BLUE));
  delay(100);
  digitalWrite(LED_PIN_RED, !digitalRead(LED_PIN_RED));
  delay(100);
  digitalWrite(LED_PIN_GREEN, !digitalRead(LED_PIN_GREEN));
  delay(100);
  digitalWrite(LED_PIN_BLUE, !digitalRead(LED_PIN_BLUE));
  delay(100);
  digitalWrite(LED_PIN_RED, !digitalRead(LED_PIN_RED));
  delay(100);
  
  // Serial3.begin(115200);
  Serial.begin(115200);
  delay(1000);
  Serial.println("System Starting...");
}

// the loop function runs over and over again forever
void loop() 
{
  buzz();

  Serial.println("hyd_actuators_master_valve_Pin PB8 BLINK! ");
  digitalWrite(hyd_actuators_master_valve_Pin,HIGH);
  buzz();
  delay(1000);
  digitalWrite(hyd_actuators_master_valve_Pin,LOW);
  // Tested OK

  Serial.println("LH_wheel_up_Pin PG8 BLINK! ");
  digitalWrite(LH_wheel_up_Pin,HIGH);
  buzz();
  delay(1000);
  digitalWrite(LH_wheel_up_Pin,LOW);
  // Tested OK

  Serial.println("LH_wheel_down_Pin PE0 BLINK! ");
  digitalWrite(LH_wheel_down_Pin,HIGH);
  buzz();
  delay(1000);
  digitalWrite(LH_wheel_down_Pin,LOW);
  // Tested OK

  Serial.println("RH_wheel_up_Pin PF11 BLINK! ");
  digitalWrite(RH_wheel_up_Pin,HIGH);
  buzz();
  delay(1000);
  digitalWrite(RH_wheel_up_Pin,LOW);
  // Tested OK


  Serial.println("RH_wheel_down_Pin PF15 BLINK! ");
  digitalWrite(RH_wheel_down_Pin,HIGH);
  buzz();
  delay(1000);
  digitalWrite(RH_wheel_down_Pin,LOW);
  // Tested OK


  Serial.println("LH_horiz_hyd_activator_Pin PF14 BLINK! ");
  digitalWrite(LH_horiz_hyd_activator_Pin,HIGH);
  buzz();
  delay(1000);
  digitalWrite(LH_horiz_hyd_activator_Pin,LOW);
  // Tested OK


  Serial.println("RH_horiz_hyd_activator_Pin PD15 BLINK! ");
  digitalWrite(RH_horiz_hyd_activator_Pin,HIGH);
  buzz();
  delay(1000);
  digitalWrite(RH_horiz_hyd_activator_Pin,LOW);
  // Tested OK


  Serial.println("upper_vert_hyd_activator_Pin PD14 BLINK! ");
  digitalWrite(upper_vert_hyd_activator_Pin,HIGH);
  buzz();
  delay(1000);
  digitalWrite(upper_vert_hyd_activator_Pin,LOW);
  // Tested OK
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
  Serial.println("lower_vert_hyd_activator_Pin PE7 BLINK! ");
  digitalWrite(lower_vert_hyd_activator_Pin,HIGH);
  buzz();
  delay(1000);
  digitalWrite(lower_vert_hyd_activator_Pin,LOW);
  // Tested OK


  Serial.println("drawbar_extend_pin PF4, BLINK! ");
  digitalWrite(drawbar_extend_pin,HIGH);
  buzz();
  delay(1000);
  digitalWrite(drawbar_extend_pin,LOW);
  // Tested OK

  Serial.println("drawbar_retract_pin PF5, BLINK! ");
  digitalWrite(drawbar_retract_pin,HIGH);
  buzz();
  delay(1000);
  digitalWrite(drawbar_retract_pin,LOW);
  // Tested OK

  Serial.print("Blinking loop finished! ");Serial.println(count);
  count = count +1;
}

void buzz()
{
  for(int i = 350; i > 0 ; --i)
  {
    digitalWrite(buzzer_pin, HIGH);
    delayMicroseconds(400);
    digitalWrite(buzzer_pin, LOW);
    delayMicroseconds(400);
  }
  for(int i = 250; i > 0 ; --i)
  {
    digitalWrite(buzzer_pin, HIGH);
    delayMicroseconds(600);
    digitalWrite(buzzer_pin, LOW);
    delayMicroseconds(600);
  }
}
