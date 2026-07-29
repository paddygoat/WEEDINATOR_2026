#include <STM32FreeRTOS.h>
#include "task.h"
#include <Arduino.h>
#include "globals.h"
#include "control_man.h"
// #include "declarations.h"
// #include "TinyGPS++.h"



void vTaskDelayMS_man(int ms)
{
  vTaskDelay(ms / portTICK_PERIOD_MS);
}

void TaskControlRobotMan(void *pvParameters)
{
  // long adjustEncodeSteerVal = 20;
  double PWMsmoothing = 0.0;
  bool motor_steering_DIR = false;
  bool motor_throtA_DIR = false;
  bool motor_throtB_DIR = false;
  bool prev_motor_steering_DIR = false;
  bool inductSensSteerInitFlag = false;
  int deltaPWM = 0;
  int prevMyPwm = 0;
  int orangeLampFlasherCount = 0;
  int adjustEncodeSteerValA = 0;
  int adjustEncodeSteerValB = 0;
  int steerCentre = 992;
  int adjSteerCentre = 0;
  int myPWM = 250;
  float ASRC_Steer = 5.0;
  int steeringResetCentrePointCounter = 1000;

  // Serial.print("adjustEncodeSteerVal_1:");
  // Serial.println(adjustEncodeSteerVal);
  // vTaskDelayMS_man(5000);

  inductSensSteerVal = digitalRead(inductSensSteerPin);

  while (1)
  { 

    vTaskDelayMS_man(50);

    // Orange flashing lamp:
    orangeLampFlasherCount = orangeLampFlasherCount +1;
    bool inductSensThrotAVal = digitalRead(inductSensThrotAPin);

    if(orangeLampFlasherCount > 15)
    {
      digitalWrite(LED_PIN_GREEN, !digitalRead(LED_PIN_GREEN));
      orangeLampFlasherCount = 0;
      if(inductSensThrotAVal == false)
      {
        digitalWrite(beacon_buzz_pin, !digitalRead(beacon_buzz_pin));
      }
      else
      {
        digitalWrite(beacon_buzz_pin,LOW);
      }
    }

    if(inductSensThrotAVal == true)
    {
      // digitalWrite(beacon_buzz_pin,HIGH);
      digitalWrite(LED_PIN_BLUE,HIGH);
    }
    else
    {
      // digitalWrite(beacon_buzz_pin,LOW);
      digitalWrite(LED_PIN_BLUE,LOW);
    }

    // Steering:
    inductSensSteerVal = digitalRead(inductSensSteerPin);  // Used only when the inductive sensor is installed.


    // Reset the steering center point adjustment every now and again:
    steeringResetCentrePointCounter = steeringResetCentrePointCounter -1;
    if(steeringResetCentrePointCounter < 0)
    {
      inductSensSteerInitFlag = false;
      steeringResetCentrePointCounter = 1000;
      // Serial.println("");
      // Serial.print("steeringResetCentrePointCounter: ");Serial.println(steeringResetCentrePointCounter);
    }


    // If the steering is travelling from right to left from the RHS:
    // Make the trigger value 20 to avoid the dead spot calculation.
    // Only need to trigger from one direction.
    if((motor_steering_DIR == false)&&((encoderSteerVal > 20)||(encoderSteerVal < 20)))
    {
      // Serial.println("");
      // Serial.print("travellling from right to left on the right hand lock?");
      if((inductSensSteerVal == true)&&(inductSensSteerInitFlag == false))
      {
        adjustEncodeSteerVal = encoderSteerVal;
        inductSensSteerInitFlag = true;  // one hit only.
      }
    }
 
    // Make any corrections necessary:
    actSteerAngle = encoderSteerVal - adjustEncodeSteerVal;

    if(inductSensSteerVal == true)
    {
      // digitalWrite(LED_PIN_RED, HIGH);
      // Serial.print("Inductor steering sensor is high!!");
    }
    else
    {
      // digitalWrite(LED_PIN_RED, LOW);
    }


    myPWM = 250;
    if(Man_Auto == true) // ie Manual mode.
    {
      steerCentre = 992;  // SBUS center point. Was 992,938

      // y is the desired steering angle obtained from radio transmitter via SBUS.
      y = ((ch0_data - steerCentre) * ASRC_Steer);

      // ch3_data is the man-auto switch, SWA. TODO: make this clearer in the code.
      if(y > actSteerAngle)
      {
        // digitalWrite(LED_PIN_BLUE, HIGH);
        // analogWrite(motor_steering_PWM_pin,myPWM);
        motor_steering_DIR = true;
      }
      if(y < actSteerAngle)
      {
        // digitalWrite(LED_PIN_BLUE, LOW);
        //analogWrite(motor_steering_PWM_pin,myPWM);
        motor_steering_DIR = false;
      }


      // Create PID for steering:
      int steeringDifferential = abs(y - actSteerAngle);

      if(steeringDifferential > 1000)
      {
        myPWM = 250;
      }
      if(steeringDifferential <= 1000)
      {
        myPWM = 200;
      }
      if(steeringDifferential <= 750)
      {
        myPWM = 150;
      }
      if(steeringDifferential <= 500)
      {
        myPWM = 100;
      }
      if(steeringDifferential <= 250)
      {
        myPWM = 100;
      }

      // Calculate the acceleration:
      deltaPWM = abs(myPWM - prevMyPwm);
      prevMyPwm = myPWM;



      // Steering dead zone:
      if((y < (actSteerAngle +8)) && (y > (actSteerAngle -8)))
      {
        myPWM = 0;
      }
    } //     if(Man_Auto == true) // ie Manual mode.

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

    if(Man_Auto == true)  // ie Manual.
    {
      digitalWrite(motor_steering_DIR_pin,(motor_steering_DIR));
      analogWrite(motor_steering_PWM_pin,myPWM);
    }


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


    float ASRC_Throt = 0.27;
    b = (ch1_data - 1029) * ASRC_Throt;
    // encoderThrotAVal= encThrotA.getTicks();
    // a is the PWM output. b is from RC minus 1029.
    // a = 120;
    a = 120;
    int ThrotASpeed = 0;
    // float ThrotA_adj = 4.4; // Adjust the throt travel range. Use 1.4 for reansomews mower.
    float ThrotA_adj = 1.6; // Adjust the throt travel range. Use 1.4 for reansomews mower.
    b = b * ThrotA_adj;
    PWMsmoothingThrotA = ((9*PWMsmoothingThrotA) + b)/10;
    int motor_throtA_DIR_int = 0;
    // encoderThrotAValSmoothing = ((9*encoderThrotAValSmoothing) + encoderThrotAVal)/10;


    throtA_differential = PWMsmoothingThrotA - encoderThrotAVal; // Range is -500 to 1000.
    if(PWMsmoothingThrotA > encoderThrotAVal)
    {
      if(throtA_differential> 300)
      {
        ThrotASpeed= 250;
      }
      if(throtA_differential <= 300)
      {
        ThrotASpeed= 200;
      }
      if(throtA_differential <= 200)
      {
        ThrotASpeed= 150;
      }
      if(throtA_differential <= 100)
      {
        ThrotASpeed= 130;
      }
      // if(throtA_differential <= 50)
      // {
      //   ThrotASpeed= 100;
      // }
      // FORWARDS:
      // digitalWrite(LED_PIN_GREEN, HIGH);
      // analogWrite(motor_throtA_PWM_pin,a);
      // ThrotASpeed = 250;
      motor_throtA_DIR = true;
      // motor_throtA_DIR_int = motor_throtA_DIR_int + 1;
    }
    if(PWMsmoothingThrotA < encoderThrotAVal)
    {
      if(throtA_differential < -300)
      {
        ThrotASpeed= 250;
      }
      if(throtA_differential >= -300)
      {
        ThrotASpeed= 200;
      }
      if(throtA_differential >= -200)
      {
        ThrotASpeed= 150;
      }
      if(throtA_differential >= -100)
      {
        ThrotASpeed= 130;
      }
      // if(throtA_differential >= -25)
      // {
      //   ThrotASpeed= 100;
      // }
      // BACKWARDS:
      // digitalWrite(LED_PIN_GREEN, LOW);
      // analogWrite(motor_throtA_PWM_pin,a);
      // ThrotASpeed = 250;
      motor_throtA_DIR = false;
      // motor_throtA_DIR_int = motor_throtA_DIR_int - 1;
    }

    // Throttle dead zone:
      if((throtA_differential >= -40) && (throtA_differential <= 40))
      {
        ThrotASpeed= 0;
      }


    // DIRsmoothingThrotA = ((59*DIRsmoothingThrotA) + motor_throtA_DIR_int)/60;
    /*
    // Set the sensitivity:
    if((PWMsmoothingThrotA < (encoderThrotAVal+3)) && (PWMsmoothingThrotA > (encoderThrotAVal-3)))   // Was 3.
    {
      a = 0;
      // analogWrite(motor_throtA_PWM_pin,0);
      ThrotASpeed = 0;
    }
    */

    // If we lose SBUS data in manual mode:
    if(Man_Auto == true)
    {
      if(SBUS_disconnect_flag == true)
       {
        ThrotASpeed = 0;
        myPWM = 0;
      }
    }
    // motor_throtA_DIR = true;


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/*
    // When SWC button is pressed on RC, GPS based speed limiter is applied: ch4_data
    // ch5_data gives the max GPS speed limit set by user on VRA on transmitter.
    // Typical range for sbus devices is 0 to 2047, but the full range is not available.
    // Checking SBUS reading for manual or auto GPS based throttle:
    bool man_auto_throttleA = false;
    //digitalWrite(LED_PIN_GREEN, LOW);
    if(ch4_data < 1029)
    {
      man_auto_throttleA = true;
      //digitalWrite(LED_PIN_GREEN, HIGH);
    }

    // digitalWrite(LED_PIN_RED, LOW);
    GPSspeedlimit = (ch5_data - 190)/150.0;  // map to approx 0 to 10 MPH.
    if((man_auto_throttleA == true)&&(myGPSspeed_calc > GPSspeedlimit))
    {
      // digitalWrite(LED_PIN_RED, HIGH);
      // Move throttleA backwards to reduce speed detected by GPS:
      ThrotASpeed = 150;
      // motor_throtA_DIR = false;
    }

*/
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


    /*
    // Set the dead zone:
    if((PWMsmoothingThrotA<10) && (PWMsmoothingThrotA>-10) && (encoderThrotAVal<10) && (encoderThrotAVal>-10))
    {
      a = 0;
      // analogWrite(motor_throtA_PWM_pin,0);
      ThrotASpeed = 0;
    }
    */

    /*
    if(DIRsmoothingThrotA > 0.5)
    {
      motor_throtA_DIR = true;
    }
    else
    {
      motor_throtA_DIR = false;
    }
    */


    digitalWrite(motor_throtA_DIR_pin,(motor_throtA_DIR));
    analogWrite(motor_throtA_PWM_pin,ThrotASpeed);



    // ch2 min = 229    
    d = (ch2_data - 229)/5;                   // desired position.
    // encoderThrotBVal= encThrotB.getTicks();   // actual position.
    c = (abs(encoderThrotBVal- d));           // positions delta.
    int ThrotBSpeed = 0;

    if(d > encoderThrotBVal)
    {
      // digitalWrite(LED_PIN_GREEN, HIGH);
      // analogWrite(motor_throtB_PWM_pin,150);
      ThrotBSpeed = 150;
      motor_throtB_DIR = false;             // throttle opens.
    }
    if(d < encoderThrotBVal)
    {
      // digitalWrite(LED_PIN_GREEN, LOW);
      // analogWrite(motor_throtB_PWM_pin,150);
      ThrotBSpeed = 150;
      motor_throtB_DIR = true;
    }
    if((d < (encoderThrotBVal+15)) && (d > (encoderThrotBVal-15)))
    {
      c = 0;
      ThrotBSpeed = 0;
      // analogWrite(motor_throtB_PWM_pin,0);
    }

    analogWrite(motor_throtB_PWM_pin,ThrotBSpeed);
    digitalWrite(motor_throtB_DIR_pin,(motor_throtB_DIR));

    // analogWrite(motor_throtB_PWM_pin,120);
    // digitalWrite(motor_throtB_DIR_pin,true);
  }
}

