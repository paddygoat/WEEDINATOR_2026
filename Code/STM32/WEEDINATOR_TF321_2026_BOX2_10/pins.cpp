#include <Arduino.h>
#include "pins.h"

void setUpPins()
{
  pinMode(motor_steering_PWM_pin, OUTPUT);
  pinMode(motor_steering_DIR_pin, OUTPUT);

  pinMode(motor_throtA_PWM_pin, OUTPUT);
  pinMode(motor_throtA_DIR_pin, OUTPUT);

  pinMode(motor_throtB_PWM_pin, OUTPUT);
  pinMode(motor_throtB_DIR_pin, OUTPUT);
      
  analogWrite(motor_throtA_PWM_pin,0);   // What's this for?

  pinMode(LED_PIN_RED, OUTPUT);
  pinMode(LED_PIN_BLUE, OUTPUT);
  pinMode(LED_PIN_WHITE, OUTPUT);
  pinMode(buzzer_pin, OUTPUT);
  pinMode(beacon_buzz_pin, OUTPUT);

  // Stops buzzer from sounding on start up:
  digitalWrite(beacon_buzz_pin,LOW);

  pinMode(inductSensSteerPin, INPUT_PULLUP);
  pinMode(inductSensThrotAPin, INPUT_PULLUP);

  pinMode(fuelPumpAndAltPin, OUTPUT);
  pinMode(glowPlugsPin, OUTPUT);
  pinMode(starterMotorPin, OUTPUT);
  pinMode(engineStopSolenoidPin, OUTPUT);

  pinMode(hyd_actuators_master_valve_Pin, OUTPUT);
  pinMode(hyd_motors_master_valve_Pin, OUTPUT);

  pinMode(LH_wheel_up_Pin, OUTPUT);
  pinMode(LH_wheel_down_Pin, OUTPUT);
  pinMode(RH_wheel_up_Pin, OUTPUT);
  pinMode(RH_wheel_down_Pin, OUTPUT);

  pinMode(LH_horiz_hyd_activator_Pin, OUTPUT);
  pinMode(RH_horiz_hyd_activator_Pin, OUTPUT);
  pinMode(upper_vert_hyd_activator_Pin, OUTPUT);
  pinMode(lower_vert_hyd_activator_Pin, OUTPUT);

  pinMode(drawbar_extend_pin, OUTPUT);
  pinMode(drawbar_retract_pin, OUTPUT);

  pinMode(loader_hyd_actuators_master_valve_Pin, OUTPUT);

  pinMode(tilt_up_hyd_activator_Pin, OUTPUT);
  pinMode(tilt_down_hyd_activator_Pin, OUTPUT);
  pinMode(load_up_hyd_activator_Pin, OUTPUT);
  pinMode(load_down_hyd_activator_Pin, OUTPUT);

  pinMode(drawbar_limit_switch_pin, INPUT);



  digitalWrite(hyd_actuators_master_valve_Pin, LOW);
  digitalWrite(hyd_motors_master_valve_Pin, LOW);

  digitalWrite(LH_wheel_up_Pin, LOW);
  digitalWrite(LH_wheel_down_Pin, LOW);
  digitalWrite(RH_wheel_up_Pin, LOW);
  digitalWrite(RH_wheel_down_Pin, LOW);

  digitalWrite(LH_horiz_hyd_activator_Pin, LOW);
  digitalWrite(RH_horiz_hyd_activator_Pin, LOW);
  digitalWrite(hyd_actuators_master_valve_Pin, LOW);
  digitalWrite(lower_vert_hyd_activator_Pin, LOW);

  digitalWrite(loader_hyd_actuators_master_valve_Pin, LOW);

  digitalWrite(tilt_up_hyd_activator_Pin, LOW);
  digitalWrite(tilt_down_hyd_activator_Pin, LOW);
  digitalWrite(load_up_hyd_activator_Pin, LOW);
  digitalWrite(load_down_hyd_activator_Pin, LOW);

  digitalWrite(drawbar_extend_pin, LOW);
  digitalWrite(drawbar_retract_pin, LOW);

}
