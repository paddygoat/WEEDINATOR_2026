#ifndef GLOBALS
#define GLOBALS


extern int x;
extern int y;
extern int a;
extern float b;
extern int c;
extern int d;

extern long PWMsmoothing;
extern float PWMsmoothingThrotA;
extern float DIRsmoothingThrotA;
extern float encoderThrotAValSmoothing;

extern bool motor_throtA_DIR;

extern int actSteerAngle;          // Derived from encoder.
extern double actSteerAngleAdj;
extern int delta_angle;            // No longer used.
extern double heading_delta;
extern double heading_deltaABC;

extern int encoderThrotAVal;
extern int encoderThrotBVal;
extern long encoderSteerVal;
extern long encoderWheelVal;
extern long adjustEncodeSteerVal;
extern bool inductSensSteerVal;

extern long encImplementWheelVal;
extern long encHorizActuatorVal;
extern long encDrawbarActuatorVal;

extern int ch2_data;
extern double myLongitude;
extern double myLatitude;

// High precision coords:
extern double d_lat;
extern double d_lon;

extern double des_lat;
extern double des_lon;


// extern double testDesLatLonArray[200][3];   // 3D array to store desired lat/lon pairs and ids, 10 rows.
extern double myGPSdata_array[500][2];  // 2D array to store act_lat and act_lon
extern int latLonCount;  // Number of lat/lon pairs found
extern int numWayPointsLeft;
extern int wayPointNum;
extern bool dataDownloadedLatch;
extern double myDist;
extern int num_waypoints;

extern double actHeading;
extern int myLength;
extern long lastGPSFixTime;
extern float GPSspeedlimit;
extern double myGPSspeed_calc;
extern double mySpeedGPS;
extern float myRelPosAcc;
extern String carrierSolutionType;
extern long GPSFixTime;

extern int ch0_data;   // Steering.
extern int ch1_data;   // throtA
extern int ch2_data;   // throtB
extern int ch3_data;   // manual / auto
extern int ch4_data;
extern int ch5_data;
extern int ch6_data;
extern int ch7_data;    // Engine start stop.
extern int ch8_data;    // Engine on off.
extern int ch9_data;    // LH_WHEEL hydraulic actuator.
extern int ch10_data;   // RH_WHEEL hydraulic actuator.
extern int ch11_data;
extern int ch12_data;
extern int ch13_data;
extern int ch14_data;
extern int ch15_data;
extern int ch16_data;
extern int ch17_data;

extern int GSM_session_num;

extern bool Man_Auto;
extern bool GPS_GSM_flag; // GPS = true.
extern int eepromAddress;
extern int GSM_session_data;    // Created by WEEDINATOR.
extern int session_num_d;       // Downloaded from database.

extern bool drawbarLimitSwitch;

extern int slider1_val;
extern int slider2_val;

#endif
