/*
 * Board is STM 144 Nucleo H723ZG
 * ls sudo /dev/tty*
 * sudo usermod -a -G dialout <username>
 * Connect STM board
 * ls sudo /dev/tty*
 * sudo chmod 777 /dev/ttyACM0
 * restart
 */

#include "declarations.h"
#include "globals.h"
#include "wDebug.h"
#include "control_man.h"
#include "control_auto.h"
#include <EEPROM.h>


void setup()
{
  setUpPins();

  // Initialize Serial port
  // Note: Using 500000 baud for high-speed communication
  Serial.begin(500000);
  // Serial.begin(115200);

  // while (!Serial);
  // Serial1.begin(115200);
  delay(1000);
  Serial.println("");
  Serial.println("");
  Serial.println("System Starting...");

  digitalWrite(beacon_buzz_pin,HIGH);
  delay(1000);
  digitalWrite(beacon_buzz_pin,LOW);

  // Make sure throttle B is set to minimum:
  digitalWrite(motor_throtB_DIR_pin,(true));
  analogWrite(motor_throtB_PWM_pin,250);


  buzz();
  flash_all_LEDs();
  buzz();
  flash_all_LEDs();

  
  if (encSteer.init()) {
    Serial.println("Encoder Steer Initialization OK");
  } else {
    Serial.println("Encoder Steer Initialization Failed");
    while(1);
  }

  if (encThrotA.init()) {
    Serial.println("Encoder ThrotA Initialization OK");
  } else {
    Serial.println("Encoder ThrotA Initialization Failed");
    while(1);
  }

  if (encThrotB.init()) {
    Serial.println("Encoder ThrotB Initialization OK");
  } else {
    Serial.println("Encoder ThrotB Initialization Failed");
    while(1);
  }

  TIM_TypeDef *Instance3 = TIM7;
  HardwareTimer *MyTim3 = new HardwareTimer(Instance3);
  MyTim3->setOverflow(100, HERTZ_FORMAT); // 100 Hz
  MyTim3->attachInterrupt(Update_IT_callback_throtB);
  MyTim3->resume();

  TIM_TypeDef *Instance2 = TIM6;
  HardwareTimer *MyTim2 = new HardwareTimer(Instance2);
  MyTim2->setOverflow(100, HERTZ_FORMAT); // 100 Hz
  MyTim2->attachInterrupt(Update_IT_callback_throtA);
  MyTim2->resume();
  
  TIM_TypeDef *Instance1 = TIM5;
  HardwareTimer *MyTim1 = new HardwareTimer(Instance1);
  MyTim1->setOverflow(100, HERTZ_FORMAT); // 100 Hz
  MyTim1->attachInterrupt(Update_IT_callback_steer);
  MyTim1->resume();
  


  buzz();
  flash_all_LEDs();
  encoderThrotBVal = 0;

  // 5 = highest priority
  xTaskCreate(TaskReadGPS, "ReadGPS", 1024, NULL, 4, NULL);
  xTaskCreate(TaskReadSBUS, "ReadSBUS", 1024, NULL, 3, NULL);
  xTaskCreate(TaskStart_engine, "Start_engine", 1024, NULL, 2, NULL);

  // xTaskCreate(TaskDebug, "Debug", 1024, NULL, 2, NULL);
  xTaskCreate(TaskEncoders, "Encoders", 1024, NULL, 3, NULL);
  xTaskCreate(TaskControlRobotMan, "Robot manual control", 1024, NULL, 5, NULL);
  xTaskCreate(TaskControlRobotAuto, "Robot auto control", 1024, NULL, 5, NULL);
  xTaskCreate(TaskHydraulics, "Hydraulics", 1024, NULL, 2, NULL);
  xTaskCreate(TaskUSBComms, "USB_Comms", 1024, NULL, 4, NULL);

  Serial.println("Setup completed.");
 
  vTaskStartScheduler();
  Serial.println("Insufficient RAM");
  while (1);

}


void Update_IT_callback_steer(void)
{ 
  encSteer.loop();
}

void Update_IT_callback_throtA(void)
{ 
  // Serial.print(".");
  encThrotA.loop();
}

void Update_IT_callback_throtB(void)
{ 
  // Serial.print(".");
  encThrotB.loop();
}

void vTaskDelayMS(int ms)
{
  vTaskDelay(ms / portTICK_PERIOD_MS);
}

void TaskDebug(void *pvParameters);
void TaskStart_engine(void *pvParameters);
// void TaskReadWriteGSM(void *pvParameters);
// void TaskReadGPS(void *pvParameters);
void TaskReadSBUS(void *pvParameters);
void TaskControlRobotMan(void *pvParameters);
void TaskControlRobotAuto(void *pvParameters);
void TaskReadGPS_GSM(void *pvParameters);
// void Task Hydraulics is missing - it's in 'declarations'!

void TaskEncoders(void *pvParameters)
{
  while (1)
  {
    vTaskDelayMS(20);
    encoderSteerVal = encSteer.getTicks();
    // Prevent uncontrolled overflow of unsigned long when steering is conveniently straight ahead.
    // Test this by temperorarily setting relevant variable to int. Not yet tested !!
    if((encoderSteerVal > 4000000000)&&(inductSensSteerVal == true))  // unsigned long 4294967295
    {
      encSteer.init();
      adjustEncodeSteerVal = 0;
      encoderSteerVal = 0;
    }
    encoderThrotAVal= encThrotA.getTicks();
    encoderThrotBVal= encThrotB.getTicks();
  }
}

void loop() 
{

}
