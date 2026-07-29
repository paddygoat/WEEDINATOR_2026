#ifndef GPS_GSM
#define GPS_GSM


#include "pins.h"
#include <Arduino.h>
#include "TinyGPS++.h"
#include <SparkFun_u-blox_GNSS_Arduino_Library.h>
#include <EEPROM.h>


#define Serial_GPS Serial1
SFE_UBLOX_GNSS myGNSS;


#define TINY_GSM_MODEM_SIM7600
// #define Serial3_TX_PIN PA9
// #define Serial3_RX_PIN PA10
#define BUILTIN_LED_PIN D13
#define LED_ORANGE D12
#define LED_GREEN D11
#define LED_RED D10
#define TINY_GSM_TEST_GSM_LOCATION false
#define TINY_GSM_TEST_GPS true

HardwareSerial SerialAT(Serial3_RX_PIN, Serial3_TX_PIN);

// Set serial for debug console (to the Serial Monitor, default speed 115200)
#define SerialMon Serial
// #define SerialAT Serial3

// Increase RX buffer to capture the entire response
// Chips without internal buffering (A6/A7, ESP8266, M590)
// need enough space in the buffer for the entire response
// else data will be lost (and the http library will fail).
#if !defined(TINY_GSM_RX_BUFFER)
#define TINY_GSM_RX_BUFFER 650
#endif

// See all AT commands, if wanted
// #define DUMP_AT_COMMANDS

// Define the serial console for debug prints, if needed
#define TINY_GSM_DEBUG SerialMon

// Range to attempt to autobaud
// NOTE:  DO NOT AUTOBAUD in production code.  Once you've established
// communication, set a fixed baud rate using modem.setBaud(#).
#define GSM_AUTOBAUD_MIN 230400
#define GSM_AUTOBAUD_MAX 250000

// Add a reception delay, if needed.
// This may be needed for a fast processor at a slow baud rate.
// #define TINY_GSM_YIELD() { delay(2); }

// Uncomment this if you want to use SSL
// #define USE_SSL

// Define how you're planning to connect to the internet.
// This is only needed for this example, not in other code.
#define TINY_GSM_USE_GPRS true
#define TINY_GSM_USE_WIFI false

// set GSM PIN, if any
#define GSM_PIN ""


// Your GPRS credentials, if any
// const char apn[]      = "soracom.io";
// const char gprsUser[] = "sora";
// const char gprsPass[] = "sora";

const char apn[]      = "MY.INTERNET";
const char gprsUser[] = "wap";
const char gprsPass[] = "wap";


// Server details
// const char server[]   = "goatindustries.co.uk/bat_detector/send.php";
const char server[]   = "goatindustries.co.uk";      // Works !!
// const char server[]   = "vsh.pp.ua";
const char resource[] = "/TinyGSM/logo.txt";

#include <TinyGsmClient.h>
#include <ArduinoHttpClient.h>
// #include <ArduinoJson.h>

// Just in case someone defined the wrong thing..
#if TINY_GSM_USE_GPRS && not defined TINY_GSM_MODEM_HAS_GPRS
#undef TINY_GSM_USE_GPRS
#undef TINY_GSM_USE_WIFI
#define TINY_GSM_USE_GPRS false
#define TINY_GSM_USE_WIFI true
#endif
#if TINY_GSM_USE_WIFI && not defined TINY_GSM_MODEM_HAS_WIFI
#undef TINY_GSM_USE_GPRS
#undef TINY_GSM_USE_WIFI
#define TINY_GSM_USE_GPRS true
#define TINY_GSM_USE_WIFI false
#endif

#ifdef DUMP_AT_COMMANDS
#include <StreamDebugger.h>
StreamDebugger debugger(SerialAT, SerialMon);
TinyGsm        modem(debugger);
#else
TinyGsm        modem(SerialAT);
#endif

#ifdef USE_SSL
TinyGsmClientSecure client(modem);
const int           port = 443;
#else
TinyGsmClient  client(modem);
const int      port = 80;
HttpClient    http(client, server, port);
#endif

// Define a structure to hold id, latitude, and longitude
struct LatLonData 
{
  int id;
  float lat;
  float lon;
};

extern void TaskReadGPS(void *pvParameters);
extern LatLonData* extractLatLon(String dataString);
extern unsigned long myReadEEPROM(int eepromAddress);
extern void myWriteToEEPROM(unsigned long val, int eepromAddress);


#endif
