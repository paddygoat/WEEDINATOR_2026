#include <STM32FreeRTOS.h>
#include "task.h"
#include <Arduino.h>
#include "globals.h"
#include "sbus.h"
#include "pins.h"
#include "buzzLED.h"

/*
fuelPumpAndAltPin PG4
glowPlugsPin PG5
starterMotorPin PG6
engineStopSolenoidPin PG7
*/

bool wheels_flag = false;
bool buzz_flag = false;
bool drawbarLimitSwitchFlag = false;

void vTaskDelayMS_hydraulics(int ms)
{
  vTaskDelay(ms / portTICK_PERIOD_MS);
}

// TODO: When the transceiver is first turned on it expects all switches to be in upright position, yet we would ideally like some switches to be in the middle position.
// Account for this fact when dealing with the wheel hydraulic actuators. We dont the actuators to come on when the system starts, so the switch must cycle to mid position before anything else gets done.
// Maybe do this with some kind of flag.

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

void TaskHydraulics(void *pvParameters)
{
  while (1)
  {

    vTaskDelayMS_hydraulics(50);
    // Make sure the wheels and drawbar switches start in neutral position:
    if ((ch9_data == 992)&&(ch10_data == 992)&&(ch14_data == 992))
    {
      wheels_flag = true;
      // Serial.print("Hydraulics working!!!");
      // wheels_flag now stays true forever more.
    }

    // Make a one off buzz when wheel swithces are in neutral position:
    if((wheels_flag == true)&&(buzz_flag == false))
    {
      digitalWrite(beacon_buzz_pin,HIGH);
      vTaskDelayMS_hydraulics(500);
      digitalWrite(beacon_buzz_pin,LOW);
      // Stop any more buzzes:
      buzz_flag = true;
    }

    if((wheels_flag == true)&&(ch6_data < 992))
    {
      // LH Wheel:
      // Serial.print(", Ch9:");
      // Serial.print(ch9_data);
      // Ch6_data is the multiplexer VRA knob on Flysky.
      if ((ch9_data > 992)&&(ch6_data < 992))
      {
        // Serial.print("Ch9 is greater than 992 !!!");
        digitalWrite(LH_wheel_up_Pin,HIGH);
        digitalWrite(LH_wheel_down_Pin,LOW);
        // The hyd actuators master valve must act simultaneously:
        digitalWrite(hyd_actuators_master_valve_Pin,HIGH);
      }
      if ((ch9_data < 992)&&(ch6_data < 992))
      {
        digitalWrite(LH_wheel_down_Pin,HIGH);
        digitalWrite(LH_wheel_up_Pin,LOW);
        digitalWrite(hyd_actuators_master_valve_Pin,HIGH);
      }
      if ((ch9_data == 992)&&(ch6_data < 992))
      {
        digitalWrite(LH_wheel_up_Pin,LOW);
        digitalWrite(LH_wheel_down_Pin,LOW);
        // digitalWrite(hyd_actuators_master_valve_Pin,LOW);
      }

      // RH Wheel:
      if ((ch10_data > 992)&&(ch6_data < 992))
      {
        digitalWrite(RH_wheel_up_Pin,HIGH);
        digitalWrite(RH_wheel_down_Pin,LOW);
        digitalWrite(hyd_actuators_master_valve_Pin,HIGH);
      }
      if ((ch10_data < 992)&&(ch6_data < 992))
      {
        digitalWrite(RH_wheel_down_Pin,HIGH);
        digitalWrite(RH_wheel_up_Pin,LOW);
        digitalWrite(hyd_actuators_master_valve_Pin,HIGH);
      }
      if ((ch10_data == 992)&&(ch6_data < 992))
      {
        digitalWrite(RH_wheel_up_Pin,LOW);
        digitalWrite(RH_wheel_down_Pin,LOW);
        // digitalWrite(hyd_actuators_master_valve_Pin,LOW);
      }



      // horizontal hydraulic actuator:
      if ((ch12_data > 1100)&&(ch6_data < 992))
      {
        digitalWrite(LH_horiz_hyd_activator_Pin,HIGH);
        digitalWrite(RH_horiz_hyd_activator_Pin,LOW);
        // The hyd actuators master valve must act simultaneously:
        digitalWrite(hyd_actuators_master_valve_Pin,HIGH);
      }
      if ((ch12_data < 900)&&(ch6_data < 992))
      {
        digitalWrite(LH_horiz_hyd_activator_Pin,LOW);
        digitalWrite(RH_horiz_hyd_activator_Pin,HIGH);
        digitalWrite(hyd_actuators_master_valve_Pin,HIGH);
      }
      if ((ch12_data > 900)&&(ch12_data < 1100)&&(ch6_data < 992))
      {
        digitalWrite(LH_horiz_hyd_activator_Pin,LOW);
        digitalWrite(RH_horiz_hyd_activator_Pin,LOW);
        // digitalWrite(hyd_actuators_master_valve_Pin,LOW);
      }


      // vertical hydraulic actuator:
      if ((ch13_data > 1100)&&(ch6_data < 992))
      {
        digitalWrite(upper_vert_hyd_activator_Pin,HIGH);
        digitalWrite(lower_vert_hyd_activator_Pin,LOW);
        // The hyd actuators master valve must act simultaneously:
        digitalWrite(hyd_actuators_master_valve_Pin,HIGH);
      }
      if ((ch13_data < 900)&&(ch6_data < 992))
      {
        digitalWrite(upper_vert_hyd_activator_Pin,LOW);
        digitalWrite(lower_vert_hyd_activator_Pin,HIGH);
        digitalWrite(hyd_actuators_master_valve_Pin,HIGH);
      }
      if ((ch13_data > 900)&&(ch13_data < 1100)&&(ch6_data < 992))
      {
        digitalWrite(upper_vert_hyd_activator_Pin,LOW);
        digitalWrite(lower_vert_hyd_activator_Pin,LOW);
        // digitalWrite(hyd_actuators_master_valve_Pin,LOW);
      }

      // Drawbar:
      drawbarLimitSwitch = digitalRead(drawbar_limit_switch_pin);
      if(drawbarLimitSwitch == HIGH)
      {
        // digitalWrite(LED_PIN_RED, HIGH);
      }
      else
      {
        // digitalWrite(LED_PIN_RED, LOW);
      }

      if ((ch14_data > 992)&&(ch6_data < 992))
      {
        digitalWrite(drawbar_extend_pin,HIGH);
        digitalWrite(drawbar_retract_pin,LOW);
        digitalWrite(hyd_actuators_master_valve_Pin,HIGH);
      }

      if ((ch14_data < 992)&&(drawbarLimitSwitch == LOW)&&(ch6_data < 992))
      {
        drawbarLimitSwitchFlag = true;
        digitalWrite(drawbar_retract_pin,HIGH);
        digitalWrite(drawbar_extend_pin,LOW);
        digitalWrite(hyd_actuators_master_valve_Pin,HIGH);
      }

      // One hit logic for the case when switch is activated:
      if ((ch14_data < 992)&&(drawbarLimitSwitch == HIGH)&&(drawbarLimitSwitchFlag == true)&&(ch6_data < 992))
      {
        drawbarLimitSwitchFlag = false;
        digitalWrite(drawbar_retract_pin,LOW);
        digitalWrite(drawbar_extend_pin,LOW);
        digitalWrite(hyd_actuators_master_valve_Pin,LOW);
      }


      if ((ch14_data == 992)&&(ch6_data < 992))
      {
        digitalWrite(drawbar_extend_pin,LOW);
        digitalWrite(drawbar_retract_pin,LOW);
        // digitalWrite(hyd_actuators_master_valve_Pin,LOW);
      }

      if ((ch9_data == 992)&&(ch10_data == 992)&&(ch12_data > 900)&&(ch12_data < 1100)&&(ch13_data > 900)&&(ch13_data < 1100)&&(ch14_data == 992)&&(ch6_data < 992))
      {
        digitalWrite(hyd_actuators_master_valve_Pin,LOW);
      }


    }
    else
    {
      // Turn all valves off:
      digitalWrite(LH_wheel_up_Pin,LOW);
      digitalWrite(LH_wheel_down_Pin,LOW);
      digitalWrite(RH_wheel_up_Pin,LOW);
      digitalWrite(RH_wheel_down_Pin,LOW);

      digitalWrite(LH_horiz_hyd_activator_Pin,LOW);
      digitalWrite(RH_horiz_hyd_activator_Pin,LOW);
      digitalWrite(upper_vert_hyd_activator_Pin,LOW);
      digitalWrite(lower_vert_hyd_activator_Pin,LOW);

      digitalWrite(drawbar_extend_pin, LOW);
      digitalWrite(drawbar_retract_pin, LOW);

      digitalWrite(hyd_actuators_master_valve_Pin,LOW);
    }

    // Hyraulic claw motors:
    if ((ch11_data > 992)&&(ch6_data < 992))
    {
      digitalWrite(hyd_motors_master_valve_Pin,HIGH);
    }
    else
    {
      digitalWrite(hyd_motors_master_valve_Pin,LOW);
    }



    /*
    digitalWrite(loader_hyd_actuators_master_valve_Pin, LOW);

    digitalWrite(tilt_up_hyd_activator_Pin, LOW);
    digitalWrite(tilt_down_hyd_activator_Pin, LOW);
    digitalWrite(load_up_hyd_activator_Pin, LOW);
    digitalWrite(load_down_hyd_activator_Pin, LOW);
    */

    // Loader tilt hydraulic actuators:
    // Set default Diverter valve position:
    digitalWrite(loader_hyd_actuators_master_valve_Pin,LOW);
  
    if ((ch12_data > 1100)&&(ch6_data > 992))
    {
      digitalWrite(tilt_up_hyd_activator_Pin,HIGH);
      digitalWrite(tilt_down_hyd_activator_Pin,LOW);
      // The hyd actuators master valve must act simultaneously:
      digitalWrite(loader_hyd_actuators_master_valve_Pin,HIGH);
    }
    if ((ch12_data < 900)&&(ch6_data > 992))
    {
      digitalWrite(tilt_up_hyd_activator_Pin,LOW);
      digitalWrite(tilt_down_hyd_activator_Pin,HIGH);
      digitalWrite(loader_hyd_actuators_master_valve_Pin,HIGH);
    }
    if ((ch12_data > 900)&&(ch12_data < 1100)&&(ch6_data > 992))
    {
      digitalWrite(tilt_up_hyd_activator_Pin,LOW);
      digitalWrite(tilt_down_hyd_activator_Pin,LOW);
      // digitalWrite(loader_hyd_actuators_master_valve_Pin,LOW);
    }

    //  Loader lift hydraulic actuators:
    if ((ch13_data > 1100)&&(ch6_data > 992))
    {
      digitalWrite(load_up_hyd_activator_Pin,HIGH);
      digitalWrite(load_down_hyd_activator_Pin,LOW);
      // The hyd actuators master valve must act simultaneously:
      digitalWrite(loader_hyd_actuators_master_valve_Pin,HIGH);
    }
    if ((ch13_data < 900)&&(ch6_data > 992))
    {
      digitalWrite(load_up_hyd_activator_Pin,LOW);
      digitalWrite(load_down_hyd_activator_Pin,HIGH);
      digitalWrite(loader_hyd_actuators_master_valve_Pin,HIGH);
    }
    if ((ch13_data > 900)&&(ch13_data < 1100)&&(ch6_data > 992))
    {
      digitalWrite(load_up_hyd_activator_Pin,LOW);
      digitalWrite(load_down_hyd_activator_Pin,LOW);
      // digitalWrite(loader_hyd_actuators_master_valve_Pin,LOW);
    }





  } // while(1)
}
