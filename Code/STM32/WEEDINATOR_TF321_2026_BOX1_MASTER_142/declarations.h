#ifndef declarations
#define declarations

// STM 144 H723ZG

#include <STM32FreeRTOS.h>
#include "FastInterruptEncoder.h"
#include "sbus.h"
#include "start.h"
#include "pins.h"
#include "buzzLED.h"
#include <Arduino.h>
#include "TinyGPS++.h"
#include <SparkFun_u-blox_GNSS_Arduino_Library.h>
// #include "wGPS.h"
// #include "wGSM.h"

Encoder encSteer(encSteer_PIN_X, encSteer_PIN_Y, SINGLE /* or HALFQUAD or FULLQUAD */, 250 /* Noise and Debounce Filter (default 0) */); // - Example for STM32, check datasheet for possible Timers for Encoder mode. TIM_CHANNEL_1 and TIM_CHANNEL_2 only
Encoder encThrotA(encThrotA_PIN_X, encThrotA_PIN_Y, SINGLE /* or HALFQUAD or FULLQUAD */, 250 /* Noise and Debounce Filter (default 0) */); // - Example for STM32, check datasheet for possible Timers for Encoder mode. TIM_CHANNEL_1 and TIM_CHANNEL_2 only
Encoder encThrotB(encThrotB_PIN_X, encThrotB_PIN_Y, SINGLE /* or HALFQUAD or FULLQUAD */, 250 /* Noise and Debounce Filter (default 0) */); // - Example for STM32, check datasheet for possible Timers for Encoder mode. TIM_CHANNEL_1 and TIM_CHANNEL_2 only

// void TaskReadGPS(void *pvParameters);
void TaskReadSBUS(void *pvParameters);
// void TaskReadWriteGSM(void *pvParameters);
void TaskControlRobot(void *pvParameters);
void TaskDebug(void *pvParameters);
void TaskReadGPS(void *pvParameters);
void TaskHydraulics(void *pvParameters);
void TaskComms(void *pvParameters);
void TaskUSBComms(void *pvParameters);

QueueHandle_t my_queue = xQueueCreate(10, sizeof(int));
QueueHandle_t my_queue2 = xQueueCreate(10, sizeof(int));

unsigned long encodertimer = 0;
unsigned long debugTimer = 0;
unsigned long GPSTimer1 = 0;
unsigned long GPSTimer2 = 0;
unsigned long GSMTimer1 = 0;
unsigned long GSMTimer2 = 0;

// HardwareSerial Serial1(Serial1_RX_PIN, Serial1_TX_PIN);
// HardwareSerial Serial2(Serial2_RX_PIN, Serial2_TX_PIN);

// SBUS:
HardwareSerial Serial2(Serial2_RX_PIN, Serial2_TX_PIN);

// GSM:
// HardwareSerial Serial99(Serial3_RX_PIN, Serial3_TX_PIN);

// GPS SETUP
HardwareSerial Serial1(Serial1_RX_PIN, Serial1_TX_PIN);

// Comms with Jetson Nano:
// HardwareSerial Serial9(Serial9_RX_PIN, Serial9_TX_PIN);

// Comms with box 2 STM32 board:
// HardwareSerial Serial5(Serial5_RX_PIN, Serial5_TX_PIN);

#define Serial_GPS Serial1
// SFE_UBLOX_GNSS myGNSS;
uint32_t timestamp;
// double latitude = 999;
// double longitude = 999;

// Encoder wheel:
long encoderWheelVal = 0;

// High precision coords:
double d_lat = 0.0;
double d_lon = 0.0;

double des_lat = 0.0;
double des_lon = 0.0;

double speed = 100.00001;
double course = 0;
long lastGPSFixTime = 0;
long GPSFixTime =0;

int rtkDistance = 0;  // distance between base and rover antennas
unsigned long lastFixTime = 0; // system time when last fix occured using millis()
unsigned long lastRtkValidTime = 0; // system time when last valid rtk distanceoccured using millis()
int fixAge = -100;    // time since last fix in seconds
int validRtkAge = -100; //time since last valid rtk distance
TinyGPSPlus gps;      // used to calculate the distance and heading from one waypoint to another

int myLength = 0;


unsigned long previousMillisDIR = 0;

long PWMsmoothing = 0;
float PWMsmoothingThrotA = 0;
float DIRsmoothingThrotA = 0;
float throtA_differential = 0;
float encoderThrotAValSmoothing = 0;
bool motor_steering_DIR = false;
bool motor_throtA_DIR = false;
bool motor_throtB_DIR = false;
bool prev_motor_steering_DIR = false;

bool Man_Auto = true;    // ie Manual.

int ch0_data = 992;  // Steering. J1.
int ch1_data = 1029;  // Throttle A. VRD.
int ch2_data = 1029;  // Throttle B. VRE.
int ch3_data = 0;  // Man / Auto switch
int ch4_data = 0;  // GPS Speed Limiter switch. SWC.
int ch5_data = 0;  // GPS Speed Limiter. VRA.
int ch6_data = 0;  // GSM data send session = true. SWD.
int ch7_data = 0;  // Engine start stop.
int ch8_data = 0;  // Engine on off.
int ch9_data = 0;
int ch10_data = 0;
int ch11_data = 0;
int ch12_data = 0;
int ch13_data = 0;
int ch14_data = 0;
int ch15_data = 0;
int ch16_data = 0;
int ch17_data = 0;

int x = 0;
int y = 0;
int a = 0;
float b = 0.0;
int c = 0;
int d = 0;

int GSM_session_num = 0;   // Created by the WEEDINTAOR.
int session_num_d = 0;       // Downloaded from database.

int actSteerAngle = 0;       // Derived from encoder.
double actSteerAngleAdj = 0.0; // Derived from actSteerAngle.
int delta_angle = 0;         // No longer used.
double heading_delta = 0.0;
double heading_deltaABC = 0.0;

int encoderThrotAVal = 0;
int encoderThrotBVal = 0;
long encoderSteerVal = 0;
long adjustEncodeSteerVal = 0;
bool inductSensSteerVal = false;

double actHeading = 0.0;
float GPSspeedlimit = 0.0;
double myGPSspeed_calc = 100.00001;
double mySpeedGPS = 100.00001;

double myLongitude;
double myLatitude;
// double testDesLatLonArray[200][3];  // 3D array to store desired lat/lon pairs and ids, 10 rows.
double myGPSdata_array[5][2];  // 2D array to store act_lat and act_lon.
int latLonCount = 0;  // Number of lat/lon pairs found
int numWayPointsLeft = 0;
int wayPointNum = 0;
bool dataDownloadedLatch = false;
double myDist = 0.0;
int num_waypoints = 0;

float myRelPosAcc = 0.0;
String carrierSolutionType = "";
long accuracyMM = 999;

bool GPS_GSM_flag = false; // GPS = true.

int eepromAddress = 0;
int GSM_session_data = 0;

bool drawbarLimitSwitch = false;
bool SBUS_disconnect_flag = false;

#endif
