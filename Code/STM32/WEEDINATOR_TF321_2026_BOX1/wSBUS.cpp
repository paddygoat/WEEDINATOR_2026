#include <STM32FreeRTOS.h>
#include "task.h"
#include <Arduino.h>
#include "globals.h"
#include "sbus.h"
#include "pins.h"

void vTaskDelayMS_SBUS(int ms)
{
  vTaskDelay(ms / portTICK_PERIOD_MS);
}

void TaskReadSBUS(void *pvParameters)
{
  /* SBUS object, reading SBUS */
  bfs::SbusRx sbus_rx(&Serial2);
  /* SBUS object, writing SBUS */
  bfs::SbusTx sbus_tx(&Serial2);
  /* SBUS data */
  bfs::SbusData data;
  /* Begin the SBUS communication */
  sbus_rx.Begin();
  sbus_tx.Begin();

  // Set safe startup defaults BEFORE the loop begins
  ch0_data = 992;  // Center position steering.
  ch1_data = 1029; // throtA (Zero)
  ch2_data = 229;  // throtB (Zero)
  ch3_data = 1029; // manual / auto
  ch4_data = 0;  // Manual throttle / GPS throttle switch.
  ch5_data = 0;  // GPS throttle adjust.
  ch6_data = 0;  // Hydraulics multiplexer
  ch7_data = 0;  // Engine start
  ch8_data = 0;  // Engine on / off.
  ch9_data = 0;  // LH_WHEEL hydraulic actuator.
  ch10_data = 0; // RH_WHEEL hydraulic actuator.
  ch11_data = 0; // hyd_motors_master_valve.
  ch12_data = 0; // horizontal hydraulic actuator. Joystick.
  ch13_data = 0; // vertical hydraulic actuator. Joystick.
  ch14_data = 0; // drawbar actuator.
  ch15_data = 0; // Nano shutdown button.

  while (1)
  {
    vTaskDelayMS_SBUS(50);
    
    // ONLY process data if a new frame was successfully read
    if (sbus_rx.Read())
    {
      // Grab the received data
      data = sbus_rx.data();

      // 1. Check if the radio is off or signal is lost
      if (data.failsafe || data.lost_frame) 
      {
         // Transceiver is off or lost signal. Force neutral states!
         ch0_data = 992;   // Center steering
         // ch1_data = 1029;  // Force Throttle A to 0
         // ch2_data = 229;   // Force Throttle B to 0
         SBUS_disconnect_flag = true;
      }
      // 2. Otherwise, map the live data
      else 
      {
        SBUS_disconnect_flag = false;
        for (int8_t i = 0; i < data.NUM_CH; i++) 
        {
          // String myData = String(data.ch[i]);
          
          // if (i == 15) ch15_data = myData.toInt();
          // if (i == 14) ch14_data = myData.toInt();
          // if (i == 13) ch13_data = myData.toInt();
          // if (i == 12) ch12_data = myData.toInt();
          // if (i == 11) ch11_data = myData.toInt();
          // if (i == 10) ch10_data = myData.toInt();
          // if (i == 9)  ch9_data = myData.toInt();
          // if (i == 8)  ch8_data = myData.toInt();
          // if (i == 7)  ch7_data = myData.toInt();
          // if (i == 6)  ch6_data = myData.toInt();
          // if (i == 5)  ch5_data = myData.toInt();
          // if (i == 4)  ch4_data = myData.toInt();
          // if (i == 3)  ch3_data = myData.toInt();
          // if (i == 2)  ch2_data = myData.toInt();
          // if (i == 1)  ch1_data = myData.toInt();
          // if (i == 0)  ch0_data = myData.toInt();
          if (i == 15) ch15_data = data.ch[i];
          if (i == 14) ch14_data = data.ch[i];
          if (i == 13) ch13_data = data.ch[i];
          if (i == 12) ch12_data = data.ch[i];
          if (i == 11) ch11_data = data.ch[i];
          if (i == 10) ch10_data = data.ch[i];
          if (i == 9)  ch9_data = data.ch[i];
          if (i == 8)  ch8_data = data.ch[i];
          if (i == 7)  ch7_data = data.ch[i];
          if (i == 6)  ch6_data = data.ch[i];
          if (i == 5)  ch5_data = data.ch[i];
          if (i == 4)  ch4_data = data.ch[i];
          if (i == 3)  ch3_data = data.ch[i];
          if (i == 2)  ch2_data = data.ch[i];
          if (i == 1)  ch1_data = data.ch[i];
          if (i == 0) ch0_data = data.ch[i];
        }
        
        // Set the SBUS TX data to the received data
        sbus_tx.data(data);
        // Write the data to the servos
        sbus_tx.Write();
      } // End of else block
    } // End of if(sbus_rx.Read()) block
  } // End of while(1)
}
