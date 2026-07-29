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

void vTaskDelayMS_start(int ms)
{
  vTaskDelay(ms / portTICK_PERIOD_MS);
}

void TaskStart_engine(void *pvParameters)
{
  int engineStartCountDown = 200;
  while (1)
  {
    vTaskDelayMS_start(50);
    // The engine start momentary switch is held closed for 10 seconds to activate glow plugs and fuel pump:
    if ((ch7_data > 1000)&&(engineStartCountDown > 0))
    {
      digitalWrite(fuelPumpAndAltPin,HIGH);
      digitalWrite(glowPlugsPin,HIGH);
      engineStartCountDown = engineStartCountDown -1;
    }
    else
    {
      digitalWrite(glowPlugsPin,LOW);
    }

    // Once counter hits 0, start the engine:
    if ((ch7_data > 1000)&&(engineStartCountDown == 0))
    {
      digitalWrite(starterMotorPin,HIGH);
      digitalWrite(glowPlugsPin,LOW);
    }
    else
    {
      digitalWrite(starterMotorPin,LOW);
      // engineStartCountDown = 200;
    }

    // Turn off the engine and reset the counter:
    if (ch8_data > 1000) // Engine on off.
    {
      digitalWrite(engineStopSolenoidPin,HIGH);
      engineStartCountDown = 200;
    }
    else
    {
      digitalWrite(engineStopSolenoidPin,LOW);
    }

  }
}
