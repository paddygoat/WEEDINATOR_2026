// This sketch demonstrates how to nest an entire JSON payload 
// under a single root key ("From_MCU0"), where "From_MCU0" itself contains 
// another nested object ("To_MCU1"). It also includes functionality
// to read and process incoming JSON commands via the Serial port, 
// specifically looking for commands nested under "To_MCU1".

#include "declarations.h"
#include <ArduinoJson.h>
#include <STM32FreeRTOS.h>
#include "USB_comms.h"


void setup()
{
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

  setUpPins(); 
  Serial.println("Pins initialized.");

  digitalWrite(LED_PIN_WHITE,HIGH);
  delay(1000);
  digitalWrite(LED_PIN_WHITE,LOW);



  void TaskUSBComms(void *pvParameters);

  if (encImplementWheel.init()) 
  {
    Serial.println("Encoder encImplementWheel Initialization OK");
  } 
  else 
  {
    Serial.println("Encoder encImplementWheel Initialization Failed");
    while(1);
  }


  if (encHorizActuator.init()) 
  {
    Serial.println("Encoder   encHorizActuator Initialization OK");
  } 
  else 
  {
    Serial.println("Encoder   encHorizActuator Initialization Failed");
    while(1);
  }

  if (encDrawbarActuator.init()) 
  {
    Serial.println("Encoder   encDrawbarActuator Initialization OK");
  } 
  else 
  {
    Serial.println("Encoder   encDrawbarActuator Initialization Failed");
    while(1);
  }


  TIM_TypeDef *Instance1 = TIM5;
  HardwareTimer *MyTim1 = new HardwareTimer(Instance1);
  MyTim1->setOverflow(100, HERTZ_FORMAT); // 100 Hz
  MyTim1->attachInterrupt(Update_IT_callback_wheel);
  MyTim1->resume();


  // TIM_TypeDef *Instance2 = TIM1;
  TIM_TypeDef *Instance2 = TIM7;
  HardwareTimer *MyTim2 = new HardwareTimer(Instance2);
  MyTim2->setOverflow(100, HERTZ_FORMAT); // 100 Hz
  MyTim2->attachInterrupt(Update_IT_callback_horiz);
  MyTim2->resume();

  TIM_TypeDef *Instance3 = TIM6;
  HardwareTimer *MyTim3 = new HardwareTimer(Instance3);
  MyTim3->setOverflow(100, HERTZ_FORMAT); // 100 Hz
  MyTim3->attachInterrupt(Update_IT_callback_drawbar);
  MyTim3->resume();


  // 5 = highest priority
  xTaskCreate(TaskUSBComms, "USB_Comms", 1024, NULL, 5, NULL);
  xTaskCreate(TaskHydraulics, "Hydraulics", 1024, NULL, 2, NULL);
  // xTaskCreate(TaskDebug, "Debug", 1024, NULL, 2, NULL);
  xTaskCreate(TaskEncoders, "Encoders", 1024, NULL, 3, NULL);

  Serial.println("Setup completed.");
 
  vTaskStartScheduler();
  Serial.println("Insufficient RAM");
  while (1);

}

void vTaskDelayMS(int ms)
{
  vTaskDelay(ms / portTICK_PERIOD_MS);
}

void TaskEncoders(void *pvParameters)
{
  while (1)
  {
    vTaskDelayMS(20);
    encImplementWheelVal = encImplementWheel.getTicks();
    encHorizActuatorVal =   encHorizActuator.getTicks();
    encDrawbarActuatorVal = encDrawbarActuator.getTicks();
    // Prevent uncontrolled overflow of unsigned long when steering is conveniently straight ahead.
    // Test this by temperorarily setting relevant variable to int. Not yet tested !!
  }
}

void Update_IT_callback_wheel(void)
{ 
  encImplementWheel.loop();
}

void Update_IT_callback_horiz(void)
{ 
  encHorizActuator.loop();
}

void Update_IT_callback_drawbar(void)
{ 
  encDrawbarActuator.loop();
}

void loop() 
{
}
