// Board is STM 144 Nucleo H723ZG

#include "declarations.h"
#include <ArduinoJson.h>
#include <STM32FreeRTOS.h>
#include "USB_comms.h"

HardwareTimer *encoderWheel;
HardwareTimer *encoderHoriz;
HardwareTimer *encoderDrawbar;


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

  digitalWrite(beacon_buzz_pin,HIGH);
  delay(1000);
  digitalWrite(beacon_buzz_pin,LOW);



  void TaskUSBComms(void *pvParameters);

  // ---------------------------------------------------------
  // HARDWARE ENCODER SETUP (USING STM32 HAL)
  // ---------------------------------------------------------
  
  // --- 1. Implement Wheel (TIM5, PA0, PA1) ---
  encoderWheel = new HardwareTimer(TIM5);

  // force 32-bit hardware wrapping:
  encoderWheel->setOverflow(0xFFFFFFFF, TICK_FORMAT);

  // Map pins to timer hardware
  encoderWheel->setMode(1, TIMER_INPUT_CAPTURE_RISING, encImplementWheel_PIN_X);
  encoderWheel->setMode(2, TIMER_INPUT_CAPTURE_RISING, encImplementWheel_PIN_Y);

  // --- Force internal pull-ups on PA0 and PA1 ---
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  GPIO_InitStruct.Pin = GPIO_PIN_0 | GPIO_PIN_1;
  GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;     // Alternate Function Push-Pull
  GPIO_InitStruct.Pull = GPIO_PULLUP;         // Turn on the pull-up resistor
  GPIO_InitStruct.Alternate = GPIO_AF2_TIM5;  // Map back to TIM5
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
  // -------------------------------------------------------
  
  TIM_HandleTypeDef *htim5 = encoderWheel->getHandle();
  TIM_Encoder_InitTypeDef sConfig5 = {0};
  sConfig5.EncoderMode = TIM_ENCODERMODE_TI12; // Count on both channels (4x resolution)
  sConfig5.IC1Polarity = TIM_ICPOLARITY_RISING;
  sConfig5.IC1Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig5.IC1Prescaler = TIM_ICPSC_DIV1;
  sConfig5.IC1Filter = 10; // Hardware debounce filter (0 to 15)
  sConfig5.IC2Polarity = TIM_ICPOLARITY_RISING;
  sConfig5.IC2Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig5.IC2Prescaler = TIM_ICPSC_DIV1;
  sConfig5.IC2Filter = 10;
  
  HAL_TIM_Encoder_Init(htim5, &sConfig5);
  HAL_TIM_Encoder_Start(htim5, TIM_CHANNEL_ALL);
  Serial.println("Hardware Encoder TIM5 (Wheel) Initialized.");

  // --- 2. Horizontal Actuator (TIM1, PE9, PE11) ---
  encoderHoriz = new HardwareTimer(TIM1);
  encoderHoriz->setMode(1, TIMER_INPUT_CAPTURE_RISING, encHorizActuator_PIN_X);
  encoderHoriz->setMode(2, TIMER_INPUT_CAPTURE_RISING, encHorizActuator_PIN_Y);
  
  TIM_HandleTypeDef *htim1 = encoderHoriz->getHandle();
  TIM_Encoder_InitTypeDef sConfig1 = {0};
  sConfig1.EncoderMode = TIM_ENCODERMODE_TI12; 
  sConfig1.IC1Polarity = TIM_ICPOLARITY_RISING;
  sConfig1.IC1Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig1.IC1Prescaler = TIM_ICPSC_DIV1;
  sConfig1.IC1Filter = 10; 
  sConfig1.IC2Polarity = TIM_ICPOLARITY_RISING;
  sConfig1.IC2Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig1.IC2Prescaler = TIM_ICPSC_DIV1;
  sConfig1.IC2Filter = 10;
  
  HAL_TIM_Encoder_Init(htim1, &sConfig1);
  HAL_TIM_Encoder_Start(htim1, TIM_CHANNEL_ALL);
  Serial.println("Hardware Encoder TIM1 (Horiz) Initialized.");

  // --- 3. Drawbar Actuator (TIM4, PD12, PD13) ---
  encoderDrawbar = new HardwareTimer(TIM4);
  encoderDrawbar->setMode(1, TIMER_INPUT_CAPTURE_RISING, encDrawbarActuator_PIN_X);
  encoderDrawbar->setMode(2, TIMER_INPUT_CAPTURE_RISING, encDrawbarActuator_PIN_Y);
  
  TIM_HandleTypeDef *htim4 = encoderDrawbar->getHandle();
  TIM_Encoder_InitTypeDef sConfig4 = {0};
  sConfig4.EncoderMode = TIM_ENCODERMODE_TI12; 
  sConfig4.IC1Polarity = TIM_ICPOLARITY_RISING;
  sConfig4.IC1Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig4.IC1Prescaler = TIM_ICPSC_DIV1;
  sConfig4.IC1Filter = 10; 
  sConfig4.IC2Polarity = TIM_ICPOLARITY_RISING;
  sConfig4.IC2Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig4.IC2Prescaler = TIM_ICPSC_DIV1;
  sConfig4.IC2Filter = 10;
  
  HAL_TIM_Encoder_Init(htim4, &sConfig4);
  HAL_TIM_Encoder_Start(htim4, TIM_CHANNEL_ALL);
  Serial.println("Hardware Encoder TIM4 (Drawbar) Initialized.");

  // 5 = highest priority
  xTaskCreate(TaskUSBComms, "USB_Comms", 1024, NULL, 5, NULL);
  xTaskCreate(TaskHydraulics, "Hydraulics", 1024, NULL, 4, NULL);
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
    
    // Fetch the current hardware counter values directly
    encImplementWheelVal  = (int32_t)encoderWheel->getCount();
    encHorizActuatorVal   = (int16_t)encoderHoriz->getCount();
    encDrawbarActuatorVal = (int16_t)encoderDrawbar->getCount();
  }
}

void loop() 
{
}
