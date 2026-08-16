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

HardwareTimer *encSteer;
HardwareTimer *encThrotA;
HardwareTimer *encThrotB;

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

  // ---------------------------------------------------------
  // HARDWARE ENCODER SETUP (USING STM32 HAL)
  // ---------------------------------------------------------
  
  // --- 1. Encoder Steer Initialization on PA0 and PA1 ---
  encSteer = new HardwareTimer(TIM5);

  // force 32-bit hardware wrapping:
  encSteer->setOverflow(0xFFFFFFFF, TICK_FORMAT);

  // Map pins to timer hardware
  encSteer->setMode(1, TIMER_INPUT_CAPTURE_RISING, encSteer_PIN_X);
  encSteer->setMode(2, TIMER_INPUT_CAPTURE_RISING, encSteer_PIN_Y);

  
  // --- Force internal pull-ups on PA0 and PA1 ---
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  GPIO_InitStruct.Pin = GPIO_PIN_0 | GPIO_PIN_1;
  GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;     // Alternate Function Push-Pull
  GPIO_InitStruct.Pull = GPIO_PULLUP;         // Turn on the pull-up resistor
  GPIO_InitStruct.Alternate = GPIO_AF2_TIM5;  // Map back to TIM5
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
  // -------------------------------------------------------
  
  
  TIM_HandleTypeDef *htim5 = encSteer->getHandle();
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

  // --- 2. Encoder ThrotA Initialization on PE9 and PE11 ---
  encThrotA = new HardwareTimer(TIM1);
  encThrotA->setMode(1, TIMER_INPUT_CAPTURE_RISING, encThrotA_PIN_X);
  encThrotA->setMode(2, TIMER_INPUT_CAPTURE_RISING, encThrotA_PIN_Y);
  
  TIM_HandleTypeDef *htim1 = encThrotA->getHandle();
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
  Serial.println("Hardware Encoder TIM1 (ThrotA) Initialized.");

  // --- 3. Encoder ThrotB Initialization on PD12 and PD13 ---
  encThrotB = new HardwareTimer(TIM4);
  encThrotB->setMode(1, TIMER_INPUT_CAPTURE_RISING, encThrotB_PIN_X);
  encThrotB->setMode(2, TIMER_INPUT_CAPTURE_RISING, encThrotB_PIN_Y);
  
  TIM_HandleTypeDef *htim4 = encThrotB->getHandle();
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
  Serial.println("Hardware Encoder TIM4 (ThrotB ) Initialized.");
  


  buzz();
  flash_all_LEDs();
  encoderThrotBVal = 0;

  // 5 = highest priority
  xTaskCreate(TaskReadGPS, "ReadGPS", 1024, NULL, 4, NULL);
  xTaskCreate(TaskReadSBUS, "ReadSBUS", 1024, NULL, 3, NULL);
  xTaskCreate(TaskStart_engine, "Start_engine", 1024, NULL, 2, NULL);

  // xTaskCreate(TaskDebug, "Debug", 1024, NULL, 2, NULL);
  xTaskCreate(TaskEncoders, "Encoders", 1024, NULL, 4, NULL);
  xTaskCreate(TaskControlRobotMan, "Robot manual control", 1024, NULL, 5, NULL);
  xTaskCreate(TaskControlRobotAuto, "Robot auto control", 1024, NULL, 5, NULL);
  xTaskCreate(TaskHydraulics, "Hydraulics", 1024, NULL, 2, NULL);
  xTaskCreate(TaskUSBComms, "USB_Comms", 1024, NULL, 4, NULL);

  Serial.println("Setup completed.");
 
  vTaskStartScheduler();
  Serial.println("Insufficient RAM");
  while (1);

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

    // Cast raw uint16 hardware counts to signed int16
    encoderSteerVal  = (int32_t)encSteer->getCount();
    encoderThrotAVal = (int16_t)encThrotA->getCount();
    encoderThrotBVal = (int16_t)encThrotB->getCount();

    // Reset steering count when straight ahead at the inductive sensor
    if (inductSensSteerVal == true)  
    {
      encSteer->setCount(0);
      adjustEncodeSteerVal = 0;
      encoderSteerVal = 0;
    }
  }
}

void loop() 
{

}
