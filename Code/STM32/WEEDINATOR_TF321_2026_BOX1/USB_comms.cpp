#include <STM32FreeRTOS.h>
#include "task.h"
#include <Arduino.h>
#include "USB_comms.h"
#include <ArduinoJson.h>
#include "globals.h"

// --- Configuration ---
#define LED_PIN_ORANGE PB14
#define MAX_BUFFER_SIZE 1024 // 1KB Buffer as requested

// 1. "From_MCU1" (Root)
// 2. "To_MCU0" (Nested)
// 3. Inner keys: sensor, time, illuminate_orange_LED, dataArray (4 keys)
// 4. dataArray: 2 elements
const size_t INPUT_JSON_CAPACITY = 
    JSON_OBJECT_SIZE(1) +      // For "From_MCU1"
    JSON_OBJECT_SIZE(1) +      // For "To_MCU0"
    JSON_OBJECT_SIZE(5) +      // For the internal keys
    JSON_ARRAY_SIZE(2) +       // For the number of GPS doubles in the array.
    200;                       // Buffer for string values ("gps", "false", numbers)

/*
      ch0_data = 1028;  // Center position steering.
      ch1_data = 1029;  // throtA
      ch2_data = 1029;  // throtB
      ch3_data = 1029;  // manual / auto
      ch4_data = 0;  // Manual throttle / GPS throttle switch.
      ch5_data = 0;  // GPS throttle adjust.
      ch6_data = 0;  // Hydraulics multiplexer (variable knob VRA on Flysky) changes from front loader to rear weeding frame allowing same joystick to be used for both functions.
      ch7_data = 0;  // Engine start
      ch8_data = 0;  // Engine on / off.
      ch9_data = 0;  // LH_WHEEL hydraulic actuator.
      ch10_data = 0;  // RH_WHEEL hydraulic actuator.
      ch11_data = 0;  // hyd_motors_master_valve.
      ch12_data = 0;  // horizontal hydraulic actuator. Joystick.
      ch13_data = 0;  // vertical hydraulic actuator. Joystick.
      ch14_data = 0;  // drawbar actuator.
      ch15_data = 0;  // Nano shutdown.
*/

/* 
To add more output keys:
1. Increase internal keys JSON_OBJECT_SIZE()
2. Add key to void serializeAndPrintStatus_1() line.
3. Add key to void serializeAndPrintStatus_1() content.
4. Add key to serializeAndPrintStatus_1() line.
*/

const size_t OUTPUT_JSON_CAPACITY = 
    JSON_OBJECT_SIZE(1) +      // For "From_MCU0"
    JSON_OBJECT_SIZE(1) +      // For "To_MCU1"
    JSON_OBJECT_SIZE(13) +      // For the internal keys
    JSON_ARRAY_SIZE(2) +       // For the number of GPS doubles in the array.
    200;                       // Buffer for string values ("gps", "false", numbers)

// --- Global Buffer for DMA/High-Speed Logic ---
static char dmaBuffer[MAX_BUFFER_SIZE];
static volatile int writeIdx = 0;
static int readIdx = 0;
int lastSwitchState = HIGH; 
int currentSwitchState;
int BROADCAST_RATE = 10;    // Hertz

void vTaskDelayMS_USBcomms(int ms) 
{
    vTaskDelay(ms / portTICK_PERIOD_MS);
}

/**
 * @brief Sends JSON status updates to the Python hub.
 * Structure: {"From_MCU0": {"To_MCU1": {...}}}
 */



void serializeAndPrintStatus_1(int ch15_data, int ch14_data, int ch13_data, int ch12_data, int ch11_data, int ch10_data, int ch9_data,  int ch6_data, const char* sensor, long time, double dataArray[], size_t arraySize, const char* ledState) 
{
    StaticJsonDocument<OUTPUT_JSON_CAPACITY> doc;          // Dont forget to increase capacity as more variables added !!!
    JsonObject root = doc.createNestedObject("From_MCU0");
    JsonObject sub_root = root.createNestedObject("To_MCU1");

    sub_root["ch15_data"] = ch15_data;  // // Nano shutdown.
    sub_root["ch14_data"] = ch14_data;  // drawbar actuator.
    sub_root["ch13_data"] = ch13_data;  // vertical hydraulic actuator. Joystick.
    sub_root["ch12_data"] = ch12_data;  // horizontal hydraulic actuator. Joystick.
    sub_root["ch11_data"] = ch11_data;  // hyd_motors_master_valve.
    sub_root["ch10_data"] = ch10_data;  // RH_WHEEL hydraulic actuator.
    sub_root["ch9_data"] = ch9_data;    // LH_WHEEL hydraulic actuator.
    sub_root["ch6_data"] = ch6_data;    // hydraulic multiplexor.
    sub_root["illuminate_blue_LED"] = ledState;
    
    JsonArray data = sub_root.createNestedArray("dataArray");
    for (size_t i = 0; i < arraySize; i++) 
    {
        data.add(dataArray[i]);
    }

    serializeJson(doc, Serial);
    Serial.println(""); 
}

/*
MCU0 also needs to send the following data to Nano:
    act_lat (double d_lat)
    act_lon (double d_lon)
    act_steer_angle (int actSteerAngle)
    act_throtA_val (int encoderThrotAVal)
    act_heading (double actHeading)
    mySpeed (double myGPSspeed_calc)
    GPSspeed_calc (double mySpeedGPS)
    encoderSteerVal (long encoderSteerVal)
    NOT GSM_session_num
    NOT carrierSolutionType
    GPSFixTime (long GPSFixTime)
    myRelPosAcc (float myRelPosAcc)
*/

void serializeAndPrintStatus_2(double d_lat, double d_lon, int actSteerAngle, int encoderThrotAVal, int encoderThrotBVal, double actHeading, double mySpeedGPS, long encoderSteerVal, int ch15_data, float myRelPosAcc, long accuracyMM, String carrierSolutionType) 
{
    StaticJsonDocument<OUTPUT_JSON_CAPACITY> doc;          // Dont forget to increase capacity as more variables added !!!
    JsonObject root = doc.createNestedObject("From_MCU0");
    JsonObject sub_root = root.createNestedObject("To_NANO");

    sub_root["act_lat"] = d_lat;
    sub_root["act_lon"] = d_lon;
    sub_root["act_steer_angle"] = actSteerAngle;
    sub_root["act_throtA_val"] = encoderThrotAVal;
    sub_root["act_throtB_val"] = encoderThrotBVal;
    sub_root["act_heading"] = actHeading;
    sub_root["GPSspeed_calc"] = mySpeedGPS;
    sub_root["encoderSteerVal"] = encoderSteerVal;
    sub_root["Nano_Shutdown"] = ch15_data;
    sub_root["accuracy_MM"] = accuracyMM;
    sub_root["relPosAcc"] = myRelPosAcc;
    sub_root["carrierSolutionType"] = carrierSolutionType;

    // myRelPosAcc needs to be added to this code and the nano code too.
    // Look at line 118 and 225 and make additions.

    serializeJson(doc, Serial);
    Serial.println("");
}

void TaskUSBComms(void *pvParameters) 
{
    pinMode(LED_PIN_ORANGE, OUTPUT);
    unsigned long lastStatusTime = 0;
    
    // Match the 500,000 baud rate required by the Python script [cite: 1, 4]
    Serial.begin(500000); 
    vTaskDelayMS_USBcomms(1000);

    while(1)
    {
        // --- 1. HIGH-SPEED DATA INGESTION ---
        // Mimics DMA behavior by clearing the hardware FIFO as fast as possible
        while (Serial.available() > 0) 
        {
            char c = Serial.read();
            int nextWrite = (writeIdx + 1) % MAX_BUFFER_SIZE;
            
            if (nextWrite != readIdx) 
            { // Prevent overflow
                dmaBuffer[writeIdx] = c;
                writeIdx = nextWrite;
            }
        }

        // --- 2. ASYNCHRONOUS JSON PROCESSING ---
        // Look for the newline character '\n' sent by the Python script 
        static char processingBuffer[MAX_BUFFER_SIZE];
        static int procIdx = 0;

        while (readIdx != writeIdx) 
        {
            char c = dmaBuffer[readIdx];
            readIdx = (readIdx + 1) % MAX_BUFFER_SIZE;

            if (c == '\n' || c == '\r') 
            {
                if (procIdx > 0) 
                {
                    processingBuffer[procIdx] = '\0';
                    
                    StaticJsonDocument<INPUT_JSON_CAPACITY> commandDoc;
                    if (deserializeJson(commandDoc, processingBuffer) == DeserializationError::Ok)
                    {
                        // Check for targeted commands 
                        if (commandDoc.containsKey("To_MCU0")) 
                        {
                            bool turnOn = commandDoc["To_MCU0"]["illuminate_orange_LED"];
                            digitalWrite(LED_PIN_ORANGE, turnOn ? HIGH : LOW);
                            des_lat = commandDoc["To_MCU0"]["des_lat"];
                            des_lon = commandDoc["To_MCU0"]["des_lon"];
                            // Serial.print("des_lon: ");Serial.println(des_lon,9);
                        }
                    }
                    procIdx = 0; // Reset for next message
                }
            }
            else if (procIdx < MAX_BUFFER_SIZE - 1) 
            {
                processingBuffer[procIdx++] = c;
            }
        }

        // --- 3. PERIODIC SENSOR BROADCAST (1Hz) ---
        if (millis() - lastStatusTime >= 1000/BROADCAST_RATE) 
        {
            currentSwitchState = !currentSwitchState;

            if (currentSwitchState != lastSwitchState) 
            {
                const char* ledState = (currentSwitchState == LOW) ? "true" : "false";
                const char* sensorName = "gps";
                long timestamp = 7888768744;
                double coordinates[] = {46.89797999797, -5.68768768768};
                size_t coordsSize = sizeof(coordinates) / sizeof(coordinates[0]);

                serializeAndPrintStatus_1(ch15_data, ch14_data, ch13_data, ch12_data, ch11_data, ch10_data, ch9_data, ch6_data, sensorName, timestamp, coordinates, coordsSize, ledState);
                serializeAndPrintStatus_2(d_lat, d_lon, actSteerAngle, encoderThrotAVal, encoderThrotBVal, actHeading, mySpeedGPS, encoderSteerVal, ch15_data, myRelPosAcc, accuracyMM, carrierSolutionType);
                lastSwitchState = currentSwitchState;
            }
            lastStatusTime = millis();
        }

        vTaskDelay(10); // Yield to FreeRTOS scheduler 
    }
}