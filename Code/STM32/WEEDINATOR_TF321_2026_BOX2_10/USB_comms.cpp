#include <STM32FreeRTOS.h>
#include "task.h"
#include <Arduino.h>
#include "USB_comms.h"
#include <ArduinoJson.h>
#include "globals.h"

// --- Configuration ---
#define LED_PIN_BLUE PB0
#define LED_PIN_WHITE PB14
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
2. Add key to void serializeAndPrintStatus() line.
3. Add key to void serializeAndPrintStatus() content.
4. Add key to serializeAndPrintStatus() line.
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
int BROADCAST_RATE = 3;    // Hertz
long encImplWheelVal = 0;
long encHorizActVal = 0;
long encDrawbarActVal = 0;

void vTaskDelayMS_USBcomms(int ms) 
{
    vTaskDelay(ms / portTICK_PERIOD_MS);
}

/**
 * @brief Serializes the current status into a nested JSON object and prints it.
 * * The JSON structure generated is:
 * {"From_MCU1": {
 * "To_MCU0": {
 * "sensor": "gps",
 * "time": 7888768744,
 * "dataArray": [46.89797999797, -5.68768768768],
 * "illuminate_orange_LED": "true" 
 * }
 * }}
 * * @param sensor The sensor type string (e.g., "gps").
 * @param time The timestamp value (e.g., 7888768744).
 * @param dataArray The array of double values.
 * @param illuminate_orange_LED The state of the orange LED as a string ("true" or "false").
 */
void serializeAndPrintStatus
(
    const char* sensor, 
    long time, 
    double dataArray[], 
    size_t arraySize,
    const char* illuminate_orange_LED,
    long encImplWheelVal,
    long encHorizActVal,
    long encDrawbarActVal
)
{
    // Allocate JSON document for the status message
    StaticJsonDocument<OUTPUT_JSON_CAPACITY> outerDoc;
    
    // Create the outer root object {"From_MCU1": ...}
    JsonObject rootObject = outerDoc["From_MCU1"].to<JsonObject>();

    // Create a temporary document for the inner command structure
    StaticJsonDocument<OUTPUT_JSON_CAPACITY> innerDoc; 
    
    // Create the inner object {"To_MCU0": ...}
    JsonObject mcuDoc = innerDoc["To_MCU0"].to<JsonObject>();

    // Add required sensor data
    mcuDoc["sensor"] = sensor;
    mcuDoc["time"] = time;
    
    // Add the LED command derived from the switch state
    mcuDoc["illuminate_orange_LED"] = illuminate_orange_LED;
    mcuDoc["encImplWheelVal"] = encImplementWheelVal;
    mcuDoc["encHorizActVal"] = encHorizActuatorVal;
    mcuDoc["encDrawbarActVal"] = encDrawbarActuatorVal;
    
    // Add the data array
    JsonArray array = mcuDoc["dataArray"].to<JsonArray>();
    for (size_t i = 0; i < arraySize; i++) {
        array.add(dataArray[i]);
    }

    // Nest the inner object under the root object
    rootObject.set(innerDoc.as<JsonObject>());

    // Print the minified JSON to the serial port
    serializeJson(outerDoc, Serial);
    Serial.println(""); // Add newline character
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void TaskUSBComms(void *pvParameters) 
{
    pinMode(LED_PIN_BLUE, OUTPUT);
    pinMode(LED_PIN_WHITE, OUTPUT);

    digitalWrite(LED_PIN_BLUE, LOW);
    digitalWrite(LED_PIN_WHITE, LOW); 
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
                        if (commandDoc.containsKey("To_MCU1"))
                        {
                            bool turnOn = commandDoc["To_MCU1"]["illuminate_blue_LED"];
                            digitalWrite(LED_PIN_BLUE, turnOn ? HIGH : LOW);
                            ch6_data = commandDoc["To_MCU1"]["ch6_data"];
                            ch9_data = commandDoc["To_MCU1"]["ch9_data"];
                            ch10_data = commandDoc["To_MCU1"]["ch10_data"];
                            ch11_data = commandDoc["To_MCU1"]["ch11_data"];
                            ch12_data = commandDoc["To_MCU1"]["ch12_data"];
                            ch13_data = commandDoc["To_MCU1"]["ch13_data"];
                            ch14_data = commandDoc["To_MCU1"]["ch14_data"];
                            ch15_data = commandDoc["To_MCU1"]["ch15_data"];
                            slider1_val = commandDoc["To_MCU1"]["slider1val"];
                            slider2_val = commandDoc["To_MCU1"]["slider2val"];
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
                encImplWheelVal;
                encHorizActVal;
                encDrawbarActVal;
                double coordinates[] = {46.89797999797, -5.68768768768};
                size_t coordsSize = sizeof(coordinates) / sizeof(coordinates[0]);

                serializeAndPrintStatus(sensorName, timestamp, coordinates, coordsSize, ledState, encImplWheelVal, encHorizActVal, encDrawbarActVal);
                lastSwitchState = currentSwitchState;
            }
            lastStatusTime = millis();
        }

        vTaskDelay(5); // Yield to FreeRTOS scheduler 
    }
}