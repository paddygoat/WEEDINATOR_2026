#ifndef CONTROLAUTO
#define CONTROLAUTO
#include "pins.h"
#include <Arduino.h>

extern void TaskControlRobotAuto(void *pvParameters);
extern double mycourseTo(double lat1_l, double long1_l, double lat2_l, double long2_l);
extern double calculateDistance(double lon1, double lat1, double lon2, double lat2);
extern double deg2rad(double deg);
extern double degTorad(double deg);
extern double rad2deg(double rad);
extern double myCalc_2(double act_head_deg , double des_head_deg);
extern void angleToNormalizedVector(double angleDeg, double& x, double& y);


// Earth's radius in meters (replace with a more precise value if needed)
const double EARTH_RADIUS = 6364581;


/*
 * Earth radius at sea level is 6378137 m at the equator. It is 6356752 m at the poles and 6371001 m on average.
 * 6364581 for llanbedrgoch calculated from https://rechneronline.de/earth-radius/ 
 */


#endif
