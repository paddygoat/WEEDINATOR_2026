#include <Arduino.h>
#include "buzzLED.h"
#include <STM32FreeRTOS.h>

unsigned long previousMillisRED = 0;
unsigned long previousMillisGREEN = 0;
unsigned long previousMillisBLUE = 0;
unsigned long previousMillisTEXT = 0;

void vTaskDelayMS2(int ms)
{
  vTaskDelay(ms / portTICK_PERIOD_MS);
}

void blink_red_LED()
{
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillisRED >= 500) 
  {
    previousMillisRED = currentMillis;
    digitalWrite(LED_PIN_RED, !digitalRead(LED_PIN_RED));
  }
}

void blink_blue_LED()
{
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillisBLUE >= 500) 
  {
    previousMillisBLUE = currentMillis;
    digitalWrite(LED_PIN_BLUE, !digitalRead(LED_PIN_BLUE));
  }
}

void blink_green_LED()
{
  vTaskDelayMS2(200);
  digitalWrite(LED_PIN_GREEN, !digitalRead(LED_PIN_GREEN));
  vTaskDelayMS2(200);
  digitalWrite(LED_PIN_GREEN, !digitalRead(LED_PIN_GREEN));
}

void buzz()
{
  for(int i = 700; i > 0 ; --i)
  {
    digitalWrite(buzzer_pin, !digitalRead(buzzer_pin));
    delayMicroseconds(400);
  }
  for(int i = 500; i > 0 ; --i)
  {
    digitalWrite(buzzer_pin, !digitalRead(buzzer_pin));
    delayMicroseconds(600);
  }
}

void beep()
{
  for(int i = 200; i > 0 ; --i)
  {
    digitalWrite(buzzer_pin, !digitalRead(buzzer_pin));
    delayMicroseconds(400);
  }
}

void flash_all_LEDs()
{
  digitalWrite(LED_PIN_GREEN, !digitalRead(LED_PIN_GREEN));
  delay(100);
  digitalWrite(LED_PIN_BLUE, !digitalRead(LED_PIN_BLUE));
  delay(100);
  digitalWrite(LED_PIN_RED, !digitalRead(LED_PIN_RED));
  delay(100);
  digitalWrite(LED_PIN_GREEN, !digitalRead(LED_PIN_GREEN));
  delay(100);
  digitalWrite(LED_PIN_BLUE, !digitalRead(LED_PIN_BLUE));
  delay(100);
  digitalWrite(LED_PIN_RED, !digitalRead(LED_PIN_RED));
  delay(100);
}

void delay_with_text_1sec()
{
  digitalWrite(LED_PIN_GREEN, !digitalRead(LED_PIN_GREEN));
  delay(1000);
  Serial.print(" .. ");
}

void delay_with_text_10sec()
{
  for(int i = 10; i > 0 ; --i)
  {
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillisTEXT >= 1000) 
    {
      previousMillisTEXT = currentMillis;
      digitalWrite(LED_PIN_GREEN, !digitalRead(LED_PIN_GREEN));
      Serial.print(" ... ");
    }
  }
  Serial.println(" ... ");
}
