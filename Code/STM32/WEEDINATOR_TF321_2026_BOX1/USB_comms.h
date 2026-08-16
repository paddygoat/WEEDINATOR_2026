#ifndef USBCOMMS
#define USBCOMMS
#include "pins.h"
#include <Arduino.h>

extern void TaskUSBComms(void *pvParameters);

/*
      ch0_data = 1028;  // Center position steering.
      ch1_data = 1029;  // throtA
      ch2_data = 1029;  // throtB
      ch3_data = 1029;  // manual / auto
      ch4_data = 0;  // Manual throttle / GPS throttle switch.
      ch5_data = 0;  // GPS throttle adjust.
      ch6_data = 0;  // Hydraulics multiplexer (variable knob VRA on Flysky) changes from front loader to rear weeding frame allowing same joystick to be used for both functions.
      ch7_data = 0;  // Engine start
      ch8_data = 0;  // Engine on / off.
      ch9_data = 0;  // LH_WHEEL hydraulic actuator.
      ch10_data = 0;  // RH_WHEEL hydraulic actuator.
      ch11_data = 0;  // hyd_motors_master_valve.
      ch12_data = 0;  // horizontal hydraulic actuator. Joystick.
      ch13_data = 0;  // vertical hydraulic actuator. Joystick.
      ch14_data = 0;  // drawbar actuator.
      ch15_data = 0;  // Nano shutdown button.
*/


#endif