#include <STM32FreeRTOS.h>
#include "task.h"
#include <Arduino.h>
#include "globals.h"
#include "control_auto.h"

double LHcementMixerLat = 53.3027227;
double LHcementMixerLon = -4.2399658;
double RHcementMixerLat = 53.3027266;
double RHcementMixerLon = -4.2399166;   
double cementMixerLat = 53.302725379;
double cementMixerLon = -4.239941972;
double my_workshop_lat = 53.3026159;
double my_workshop_lon = -4.2398365;

double testLat = cementMixerLat;
double testLon = cementMixerLon;

// int wayPointNum =0;
// double des_lat;
// double des_lon;

double curr_lat = 0.0;
double curr_lon = 0.0;
double prev_lat = 0.0;
double prev_lon = 0.0;

long prevLastGPSFixTime = 0;

void vTaskDelayMS_auto(int ms)
{
  vTaskDelay(ms / portTICK_PERIOD_MS);
}

void TaskControlRobotAuto(void *pvParameters)
{
  Man_Auto = true;    // ie Manual.
  vTaskDelayMS_auto(1000);

  while (1)
  {
    // Calculate vehicle speed:
    curr_lat = myLatitude; // was d_lat;
    curr_lon = myLongitude;
    if(lastGPSFixTime != prevLastGPSFixTime)
    {
      // double GPS_read_time = millis();
      double GPS_interval = (lastGPSFixTime - prevLastGPSFixTime);
      double distTravelled = calculateDistance(curr_lon, curr_lat, prev_lon, prev_lat);
      myGPSspeed_calc = (distTravelled/GPS_interval)*1000.0*5.0;
      
      prev_lat = curr_lat;
      prev_lon = curr_lon; 
      prevLastGPSFixTime = lastGPSFixTime;
    }
    
    vTaskDelayMS_auto(50);

    // Distance stuff:
    // Get the relevant row in the waypoints array, myGPSdata_array:
    // des_lat = myGPSdata_array[wayPointNum][0]; Now done on the Nano
    // des_lon = myGPSdata_array[wayPointNum][1]; Now done on the Nano

    double act_lat = myLatitude;  // Was d_lat
    double act_lon = myLongitude;  // Was d_lon

    // myDist = calculateDistance(des_lon, des_lat, act_lon, act_lat);
    myDist = calculateDistance(curr_lon, curr_lat, des_lon, des_lat);

    // Arrival at a new way point, used for tight turn detection.
    if((myDist < 2.0)&&(Man_Auto == false))  // ie Auto. Was 3.0
    {
      wayPointNum = wayPointNum + 1;          // Starts at 0.
      numWayPointsLeft = numWayPointsLeft -1;
    }

    double des_heading = mycourseTo(act_lat, act_lon, des_lat, des_lon);

    // int delta_angle = (int(cementMixerCourse) - int(actHeading) + 540) % 360 - 180;
    // delta_angle = (int(des_heading) - int(actHeading) + 540) % 360 - 180;    // No longer used.
    heading_delta = myCalc_2(actHeading,des_heading);

/////////////////////////////////////////////////////////////////////////////////////////////////////

    // Checking SBUS reading for manual or auto steering:
    bool motor_steering_DIR = false;
    int myPWM = 250;
    // if((ch3_data < 1029) && (actHeading < 361) && (numWayPointsLeft > 0)) // Replaced '&& (numWayPointsLeft > 0)'.
    if((ch3_data > 1029)) // Replaced '&& (numWayPointsLeft > 0)'.
    {
      Man_Auto = false;  // ie Auto.
      // Serial.println("Man_Auto = false ie Auto.");
    }
    else
    {

      Man_Auto = true;
    }

/////////////////////////////////////////////////////////////////////////////////////////////////////
/*
    // Upcoming tight turn detection:
    if((wayPointNum > 0) && (Man_Auto == false)) // ie Auto.
    {
      double latA = myGPSdata_array[wayPointNum-1][0];  // Prev.
      double lonA = myGPSdata_array[wayPointNum-1][1];  // Prev.
      double latB = myGPSdata_array[wayPointNum][0];    // Curr.
      double lonB = myGPSdata_array[wayPointNum][1];    // Curr.
      double latC = myGPSdata_array[wayPointNum+1][0];  // Fut.
      double lonC = myGPSdata_array[wayPointNum+1][1];  // Fut. 
      double headingAB = mycourseTo(latA, lonA, latB, lonB);
      double headingBC = mycourseTo(latB, lonB, latC, lonC);
      heading_deltaABC = abs(myCalc_2(headingAB,headingBC));         // If there is a tight turn coming up, this value will be relatively high eg 40.0. Ignore anything above 50.
    }
*/

    // Turn encoder reading into degrees (roughly):
    actSteerAngleAdj = actSteerAngle * -0.01;        // was * -0.01
    if(Man_Auto == false) // ie Auto.
    {
      // Start to remedy over steering when close to way point:
      // This block below makes steering less sensitive when closer to way point, but makes cornering bad (understeer):
      // Need to look ahead to future waypoints to anticipate cornering.
      if(myDist >= 5.0)
      {
        actSteerAngleAdj = actSteerAngleAdj*0.5;
      }
      if((myDist < 5.0)&&(myDist >= 4.0))
      {
        actSteerAngleAdj = actSteerAngleAdj*0.7;
      }
      if((myDist < 4.0)&&(myDist >= 3.0))
      {
        actSteerAngleAdj = actSteerAngleAdj*0.9;
      }
      if((myDist < 3.0)&&(myDist >= 2.0))
      {
        actSteerAngleAdj = actSteerAngleAdj*1.0;
      }
      if(myDist < 2.0)
      {
        actSteerAngleAdj = actSteerAngleAdj*1.2;
      }

/*
      // heading_deltaABC:
      // float headDeltaFactor = 0.8;
      // if((heading_deltaABC < 5.0)&&(heading_deltaABC >= 0.0))
      // {
      //  actSteerAngleAdj = actSteerAngleAdj/0.6;
      // }
      if((heading_deltaABC < 10.0)&&(heading_deltaABC >= 5.0))
      {
        actSteerAngleAdj = actSteerAngleAdj/1.0;
      }
      if((heading_deltaABC < 20.0)&&(heading_deltaABC >= 10.0))
      {
        actSteerAngleAdj = actSteerAngleAdj/1.4;
      }
      if((heading_deltaABC < 30.0)&&(heading_deltaABC >= 20.0))
      {
        actSteerAngleAdj = actSteerAngleAdj/1.8;
      }
      if((heading_deltaABC < 40.0)&&(heading_deltaABC >= 30.0))
      {
        actSteerAngleAdj = actSteerAngleAdj/2.2;
      }
      if((heading_deltaABC < 50.0)&&(heading_deltaABC >= 40.0))
      {
        actSteerAngleAdj = actSteerAngleAdj/2.6;
      }
      if(heading_deltaABC >= 50.0)
      {
        actSteerAngleAdj = actSteerAngleAdj/3.0;
      }
*/

      if(heading_delta < actSteerAngleAdj)
      {
        motor_steering_DIR = true;
      }
      if(heading_delta > actSteerAngleAdj)
      {
        motor_steering_DIR = false;
      }


      // Create very basic PID for steering:
      float steeringDifferential_auto = abs(heading_delta - actSteerAngleAdj);

      if(steeringDifferential_auto > 20.0)
      {
        myPWM = 250;
      }
      if(steeringDifferential_auto <= 10.0)
      {
        myPWM = 200;
      }
      if(steeringDifferential_auto <= 5.0)
      {
        myPWM = 150;
      }
      if(steeringDifferential_auto <= 1.0)
      {
        myPWM = 100;
      }
      // Dead zone:
      if(steeringDifferential_auto <= 0.1)
      {
        myPWM = 0;
      }


    } // if(Man_Auto == false) // ie Auto.

    // Limit the travel off the steering on both locks, accounting for adjustments when starting up with steering not central:
    // actual range is-2650 to +3100
    if((actSteerAngle < -3500 ) && (motor_steering_DIR == false))  // Turn RIGHT.
    {
      //Serial.print("ARRIVED!!");
      myPWM = 0;
    }

    if((actSteerAngle > 2500 ) && (motor_steering_DIR == true))  // Turn LEFT.
    {
      myPWM = 0;
    }

    if(Man_Auto == false)  // ie Auto.
    {
      digitalWrite(motor_steering_DIR_pin,(motor_steering_DIR));
      analogWrite(motor_steering_PWM_pin,myPWM);
    }

    // digitalWrite(LED_PIN_GREEN, !digitalRead(LED_PIN_GREEN));    // Check how fast this loop is working.
///////////////////////////////////////////////////////////////////////////////////////////////////
  }
}


// Calculate distance (in meters) between two points using Haversine formula
double calculateDistance(double lon1, double lat1, double lon2, double lat2) 
{
  // Convert coordinates to radians
  double lat1Rad = deg2rad(lat1);
  double lon1Rad = deg2rad(lon1);
  double lat2Rad = deg2rad(lat2);
  double lon2Rad = deg2rad(lon2);

  // Apply Haversine formula
  double dlon = lon2Rad - lon1Rad;
  double dlat = lat2Rad - lat1Rad;
  double a = sin(dlat / 2) * sin(dlat / 2) + cos(lat1Rad) * cos(lat2Rad) * sin(dlon / 2) * sin(dlon / 2);
  double c = 2 * atan2(sqrt(a), sqrt(1 - a));

  return c * EARTH_RADIUS;
}

double mycourseTo(double lat1_l, double long1_l, double lat2_l, double long2_l)
{
  // returns course in degrees (North=0, West=270) from position 1 to position 2,
  // both specified as signed decimal-degrees latitude and longitude.
  // Because Earth is no exact sphere, calculated course may be off by a tiny fraction.
  // Courtesy of Maarten Lamers
  double lat1 = (double)lat1_l;
  double long1 = (double)long1_l;
  double lat2 = (double)lat2_l;
  double long2 = (double)long2_l;
  double dlon = radians(long2-long1);
  lat1 = radians(lat1);
  lat2 = radians(lat2);
  double a1 = sin(dlon) * cos(lat2);
  double a2 = sin(lat1) * cos(lat2) * cos(dlon);
  a2 = cos(lat1) * sin(lat2) - a2;
  a2 = atan2(a1, a2);
  if (a2 < 0.0)
  {
    a2 += TWO_PI;
  }
  return degrees(a2);
}

// Convert degrees to radians
double deg2rad(double deg) 
{
  return deg * M_PI / 180.0;
}

// Function to convert degrees to radians
double degToRad(double deg) 
{
  return deg * M_PI / 180.0;
}

// Convert radians to degrees
double rad2deg(double rad) 
{
  return rad * 180.0 / M_PI;
}

double myCalc_2(double act_head_deg , double des_head_deg)
{
    double x, y;
    angleToNormalizedVector(act_head_deg, x, y);

    // Serial.print("Normalized vector for act heading, ");
    // Serial.print(act_head_deg);
    // Serial.print(" degrees: (");
    // Serial.print(x,6);
    // Serial.print(", ");
    // Serial.print(y,6);
    // Serial.println(")");

    double myArray_act[2];
    myArray_act[0] = x;
    myArray_act[1] = y;

    angleToNormalizedVector(des_head_deg, x, y);

    // Serial.print("Normalized vector for des heading, ");
    // Serial.print(des_head_deg);
    // Serial.print(" degrees: (");
    // Serial.print(x,6);
    // Serial.print(", ");
    // Serial.print(y,6);
    // Serial.println(")");

    double myArray_des[2]; 
    myArray_des[0] = x;
    myArray_des[1] = y;
    
    double myMatrix[2][2];

    myMatrix[0][0] = myArray_act[0]; // act heading 0
    myMatrix[0][1] = myArray_act[1]; // act heading 1
    myMatrix[1][0] = myArray_des[0]; // desired heading 0
    myMatrix[1][1] = myArray_des[1]; // desired heading 1

    // Calculate the determinant:
    double det = (myMatrix[0][0] * myMatrix[1][1]) - (myMatrix[0][1] * myMatrix[1][0]);
    // Serial.print("det: ");
    // Serial.println(det,6);

    // Calculate the dot product:
    double dot = myMatrix[1][0] * myMatrix[0][0] + myMatrix[1][1] * myMatrix[0][1];
    // Serial.print("dot: ");
    // Serial.println(dot,6);

    // Use atan2f to produce correct results in all quadrants
    double angle_rads = atan2f(det, dot);

    // Convert to degrees and return
    double delta_angle_degrees = degrees(angle_rads);
    // Serial.print("delta_angle_degrees: ");
    // Serial.println(delta_angle_degrees,6);
    return delta_angle_degrees;
}

// Function to calculate normalized vector components
void angleToNormalizedVector(double angleDeg, double& x, double& y) 
{
  // Convert angle to radians
  double angleRad = degToRad(angleDeg);

  // Normalize angle to range 0 to 2*PI
  angleRad = fmod(angleRad, 2.0 * M_PI);

  // Calculate normalized vector components
  x = cos(angleRad);
  y = sin(angleRad);
}
