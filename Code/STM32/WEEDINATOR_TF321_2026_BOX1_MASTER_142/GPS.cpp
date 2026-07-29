#include <STM32FreeRTOS.h>
#include "task.h"
#include <Arduino.h>
#include "globals.h"
#include "GPS.h"
#include "buzzLED.h"

const int MAX_LINES = 5;  // Adjust this value based on the expected number of lines
// Currently, the interaction with the Jetson Orin Nano means only one line is received at a time.
const int MAX_VALUE_LENGTH = 24;  // Adjust this based on the expected length of latitude/longitude values

// myGPSdata_array[200][2];  // 2D array to store act_lat and act_lon
bool new_GSM_session = false;

int8_t  prev_latitudeHp = 0;
long prevTimeSinceLastGPSFix = 0;
long prevMillisGPS_GSM = 0;

bool test = false;

static char downloadedData[1024];


void parseLinesA(const char* line, int line_num) 
{
  if (line_num >= MAX_LINES) return;

  // Use strstr() to find the "pointer" to the start of the data
  const char* latPtr = strstr(line, "act_lat:");
  const char* lonPtr = strstr(line, "act_lon:");

  if (latPtr == NULL || lonPtr == NULL) return;

  // atof() converts a string to a double directly starting from the pointer.
  // We add 8 to the pointer to skip past the characters "act_lat:"
  myGPSdata_array[line_num][0] = atof(latPtr + 8);
  myGPSdata_array[line_num][1] = atof(lonPtr + 8);
}


void vTaskDelayMS_GPS(int ms)
{
  vTaskDelay(pdMS_TO_TICKS(ms));
}

void TaskReadGPS(void *pvParameters)
{
  Serial_GPS.begin(460800);
  // Serial_GPS.begin(115200);
  // bool _printDebug = false;        // Flag to print the serial commands we are sending to the Serial port for debug
  // bool _printLimitedDebug = false; // Flag to print limited debug messages. Useful for I2C debugging or high navigation rates
  // myGNSS.enableDebugging(Serial,true);  ... to get more debug info, second arg should be 'false'.
  if (!myGNSS.begin(Serial_GPS, 460800, false))
  {
    Serial.println("GPS 460800 might have failed");
  }
//////////////////////////////////////////////////////////////////////////////////////////////
  // GSM stuff:
  // Download some data. Currently there is no other command to do this, which will probably be implemented in near future,
  // so data is arbitarily downloaded just once when machine is turned on for now.
  char path[64] = ""; 
  // char downloadedData[1024]; // Pre-allocate the maximum size you expect
  String contentType = "text/plain";
  // GSM_session_data = 72;  // Was 47. Was 62. Was 65.
  uint32_t timeout = millis();
  String myGPSdata = "";
  latLonCount = 0;

  myGNSS.setAutoHPPOSLLH(true); // Tells F9P to send HP data automatically
  myGNSS.setAutoPVT(true);
  myGNSS.setAutoRELPOSNED(true);

  // Now enter the GPS loop:
  while (1)
  {
    vTaskDelayMS_GPS(185);  // Approx 5 Hertz.
    myGNSS.checkUblox(); // Process all incoming UART bytes instantly
    
    // Check HPPOSLLH
    if (myGNSS.getHPPOSLLH())
    {
      // Extract directly from the struct to prevent polling!
      int32_t latitude = myGNSS.packetUBXNAVHPPOSLLH->data.lat;
      int8_t latitudeHp = myGNSS.packetUBXNAVHPPOSLLH->data.latHp;
      int32_t longitude = myGNSS.packetUBXNAVHPPOSLLH->data.lon;
      int8_t longitudeHp = myGNSS.packetUBXNAVHPPOSLLH->data.lonHp;
      
      // Assemble the high precision latitude and longitude
      d_lat = ((double)latitude) / 10000000.0; 
      d_lat += ((double)latitudeHp) / 1000000000.0; 
      d_lon = ((double)longitude) / 10000000.0; 
      d_lon += ((double)longitudeHp) / 1000000000.0; 
      
      myLatitude = d_lat;            
      myLongitude = d_lon;           
    }

    // Check RELPOSNED (For Moving Base Heading)
    if (myGNSS.getRelPosN()) 
    {
      // Extract directly from the struct
      actHeading = (myGNSS.packetUBXNAVRELPOSNED->data.relPosHeading) / 100000.0;
      myLength = myGNSS.packetUBXNAVRELPOSNED->data.relPosLength;
      
      float myRelPosAccN = myGNSS.packetUBXNAVRELPOSNED->data.accN;
      float myRelPosAccE = myGNSS.packetUBXNAVRELPOSNED->data.accE;
      float myRelPosAccD = myGNSS.packetUBXNAVRELPOSNED->data.accD;
      myRelPosAcc = sqrt(sq(myRelPosAccN) + sq(myRelPosAccE) + sq(myRelPosAccD))/1000.0;
    }

    // Check PVT (Run this ONCE per loop)
    if (myGNSS.getPVT())
    {
      accuracyMM = myGNSS.packetUBXNAVPVT->data.hAcc; // Direct struct access
      
      long currMillisGPSFix = millis();
      GPSFixTime = currMillisGPSFix - prevTimeSinceLastGPSFix;
      prevTimeSinceLastGPSFix = currMillisGPSFix;

      // 1. Check the general Fix Type
      if (myGNSS.packetUBXNAVPVT->data.fixType == 3) 
      {
        byte carrSoln = myGNSS.packetUBXNAVPVT->data.flags.bits.carrSoln;
        if (carrSoln == 2) {
          carrierSolutionType = "RTK Fixed (Cm Prec)";
        } else if (carrSoln == 1) {
          carrierSolutionType = "RTK Float (Dm Prec)";
        } else {
          carrierSolutionType = "3D Fix (No Radio)";
        }
      } 
      else if (myGNSS.packetUBXNAVPVT->data.fixType == 2) 
      {
        carrierSolutionType = "2D fix";
      } 
      else 
      {
        carrierSolutionType = "No Fix";
      }

      mySpeedGPS = myGNSS.packetUBXNAVPVT->data.gSpeed * 2.2369e-5 * 100; // mph
      
      // OPTIONAL: Trigger your steering control update flag here! 
      // Because PVT is the last packet in the burst, you know you have fresh Lat/Lon/Heading.
    }
  } // End while(1)
} // void TaskReadGPS(void *pvParameters)




unsigned long myReadEEPROM(int eepromAddress) 
{
  unsigned long readVal = 0;

  // Read each byte and combine them into the unsigned long
  for (int i = 0; i < sizeof(readVal); i++) 
  {
    readVal |= ((unsigned long)EEPROM.read(eepromAddress + i)) << (i * 8);
  }

  return readVal;
}

void myWriteToEEPROM(unsigned long val, int eepromAddress) 
{
  // Write the value to EEPROM byte by byte (4 bytes for unsigned long)
  for (int i = 0; i < sizeof(val); i++) 
  {
    byte byteToWrite = (val >> (i * 8)) & 0xFF; // Extract each byte
    EEPROM.write(eepromAddress + i, byteToWrite);
  }

  Serial.println("Value written to EEPROM!");
}
