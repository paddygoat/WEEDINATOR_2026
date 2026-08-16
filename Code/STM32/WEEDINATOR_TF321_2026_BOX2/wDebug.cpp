#include <STM32FreeRTOS.h>
#include "task.h"
#include <Arduino.h>
#include "globals.h"

void vTaskDelayMS_debug(int ms)
{
  vTaskDelay(ms / portTICK_PERIOD_MS);
}

void TaskDebug(void *pvParameters)
{
  vTaskDelayMS_debug(1000);
  while (1)
  {
    vTaskDelayMS_debug(1000);
    Serial.println("");
    // Serial.println("");
    Serial.print("\033[95m"); // Python prints this as magenta.
    // print(f"\033[96mdistance_to_go:  {distance_to_go} meters\033[0m")
    /*
    Serial.print("x:");
    Serial.print(x);
    Serial.print("x:");
    Serial.print(x);
    Serial.print(", PWMsmoothing:");
    Serial.print(PWMsmoothing);
    */
    // Serial.print(" ,PWMsmoothingThrotA:");
    // Serial.print(PWMsmoothingThrotA);
    // Serial.print(", DIRsmoothingThrotA:");
    // Serial.print(DIRsmoothingThrotA*100);
    
    // Serial.print("SBUS_disconnect_flag: ");
    // Serial.print(SBUS_disconnect_flag);
    // Serial.print(",throtA_differential: ");
    // Serial.print(throtA_differential);
    // Serial.print(", motor_throtA_DIR:");
    // Serial.print(motor_throtA_DIR);

    
     
  
    // Serial.print(", y:");
    // Serial.print(y);
    // Serial.print(", a:");
    // Serial.print(a);

    // Serial.print(", b:");
    // Serial.print(b);

    // Serial.print(", GPSFixTime:");
    // Serial.print(GPSFixTime);

    // Serial.print(", carrierSolutionType:");
    // Serial.print(carrierSolutionType);


    /*
    Serial.print(", c:");
    Serial.print(c);
    Serial.print(", d:");
    Serial.print(d);

    Serial.print(", encoderSteerVal:");
    Serial.print(encoderSteerVal);
    */

    // Serial.print(", GSM_session_data:");
    // Serial.print(GSM_session_data);

    // Serial.print("encImplementWheelVal: ");
    // Serial.print(encImplementWheelVal);

    // Serial.print(", encHorizActuatorVal: ");
    // Serial.print(encHorizActuatorVal);

    // Serial.print(", encDrawbarActuatorVal: ");
    // Serial.print(encDrawbarActuatorVal);

    // Serial.print(", slider1_val: ");
    // Serial.print(slider1_val);

    // Serial.print(", slider2_val: ");
    // Serial.print(slider2_val);

    // Serial.print(", actSteerAngle:");
    // Serial.print(actSteerAngle);

    // Serial.print(", adjustEncodeSteerVal:");
    // Serial.print(adjustEncodeSteerVal);

    // Serial.print(", actSteerAngleAdj:");
    // Serial.print(actSteerAngleAdj,4);

    // Serial.print(", delta_angle:"); // No longer used.
    // Serial.print(delta_angle); // No longer used.

    // Serial.print(", heading_delta:");
    // Serial.print(heading_delta,4);

    // Serial.print(", myDist =");
    // Serial.print(myDist,3);

    // Serial.print(", wayPointNum: ");
    // Serial.print(wayPointNum);

    // Serial.print("numWayPointsLeft: ");
    // Serial.print(numWayPointsLeft);

    // Serial.print(", EncoderThrotA:");
    // Serial.print(encoderThrotAVal);

    // Serial.print(", encoderThrotAValSmoothing:");
    // Serial.print(encoderThrotAValSmoothing);


    // Serial.print(", EncoderThrotB:");
    // Serial.print(encoderThrotBVal);

    // Serial.print(", Ch4(man thrott / GPS thrott:");
    // Serial.print(ch4_data);

    // Serial.print(", Ch3:");
    // Serial.print(ch3_data);

    Serial.print(", Hydraulic multiplexer:");
    Serial.print(ch6_data);

    Serial.print(", Drawbar Ch14:");
    Serial.print(ch14_data);

    Serial.print(", Vertical Ch13:");
    Serial.print(ch13_data);

    Serial.print(", Motors Ch11:");
    Serial.print(ch11_data);
    
    // Serial.print(", drawbarLimitSwitch: ");
    // Serial.print(drawbarLimitSwitch);

    // Serial.print(", Ch9:");
    // Serial.print(ch9_data);

    // Serial.print(", Ch6:");
    // Serial.println(ch6_data);

    // Serial.print(", Ch3:");
    // Serial.print(ch3_data);

    // Print the high precsion lat and lon:
    // Serial.print(", Act Lat: ");
    // Serial.print(d_lat, 9);
    // Serial.print(", Act Lon: ");
    // Serial.print(d_lon, 9);

    // Serial.print(", des_lat: ");
    // Serial.print(des_lat, 9);
    // Serial.print(", des_lon: ");
    // Serial.print(des_lon, 9);

    // Serial.print(", longitude: ");
    // Serial.print(myLongitude,9);  // 7 for PVT.
    // Serial.print(", latitude: ");
    // Serial.print(myLatitude,9); // 7 for PVT.

    // Serial.print(", speed(MPH):");
    // Serial.print(mySpeedGPS);

    // Serial.print(", myGPSspeed_calc:");
    // Serial.print(myGPSspeed_calc,10);

    // Serial.print(", GPS Speed Limit:");
    // Serial.print(GPSspeedlimit);

    // Serial.print(", relPosHeading: ");
    // Serial.print(actHeading);
    // Serial.print(", relPosLength: ");
    // Serial.print(myLength);

    // Serial.print(", relPosAccuracy: ");
    // Serial.print(myRelPosAcc,3);

    // Serial.print("myGPSdata_array[0][0]: ");
    // Serial.print(myGPSdata_array[0][0],9);          // 9 for high precision.
    // Serial.print(", myGPSdata_array[0][1]: ");
    // Serial.print(myGPSdata_array[0][1],9);          // 9 for high precision.

    // Serial.print(", d_lat: ");
    // Serial.print(d_lat,9);                // 7 for PVT.
    // Serial.print(", d_lon: ");
    // Serial.print(d_lon,9);                // 7 for PVT.

    // Serial.print(", heading_deltaABC: ");
    // Serial.print(heading_deltaABC);

    // Serial.print(", Ch0 Steering:");
    // Serial.print(ch0_data);

    // Serial.print(", Ch7 Engine Start:");
    // Serial.print(ch7_data);


    // Serial.print(", myGPSdata_array[10][0]: ");
    // Serial.print(myGPSdata_array[10][0],7);
    // Serial.print(", myGPSdata_array[10][1]: ");
    // Serial.print(myGPSdata_array[10][1],7);
    /* Serial.print(", relPosAccuracy: ");
    Serial.print(myRelPosAcc,3);
    Serial.print(", numWayPointsLeft: ");
    Serial.print(numWayPointsLeft);
    Serial.print(", latLonCount:");Serial.print(latLonCount);
    Serial.print(", wayPointNum:");Serial.print(wayPointNum);

    // Print the extracted lat/lon pairs
    Serial.println("Now print the desLatlon array from debug.cpp ... ");
    for (int i = 0; i < latLonCount; i++) 
    {
      Serial.print("id: ");Serial.print(testDesLatLonArray[i][0]);
      Serial.print(", des Latitude: ");Serial.print(testDesLatLonArray[i][1],8);
      Serial.print(", des Longitude: ");Serial.println(testDesLatLonArray[i][2],8);
    }
    */
    Serial.println("\033[0m");
  }
}

