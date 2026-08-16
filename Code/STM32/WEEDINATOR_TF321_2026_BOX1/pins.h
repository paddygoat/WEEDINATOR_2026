#ifndef PINS_H
#define PINS_H


extern void setUpPins();

#define encSteer_PIN_X PA0  // These timer pins have been swapped with encThrotA !!
#define encSteer_PIN_Y PA1

#define encThrotA_PIN_X PE9
#define encThrotA_PIN_Y PE11

#define encThrotB_PIN_X PD12    // was PA6 .... check this pin for solder bridge. PD12 = TIM4.
#define encThrotB_PIN_Y PD13    // was PA7 .... check this pin for solder bridge. PD13 = TIM4.

#define motor_steering_PWM_pin PE4    // was PE5, which causes unstability during bootup.
#define motor_steering_DIR_pin PB11

#define motor_throtA_PWM_pin PA5      // Was PA6
#define motor_throtA_DIR_pin PB10

#define motor_throtB_PWM_pin PC7      // was PB4
#define motor_throtB_DIR_pin PF2

#define inductSensSteerPin PC8
#define inductSensThrotAPin PC6

#define LED_PIN_BLUE PB0
#define LED_PIN_RED PE1
#define LED_PIN_GREEN PB14  // CORRECT !!

#define buzzer_pin PC9
#define beacon_buzz_pin PC5

#define fuelPumpAndAltPin PG4
#define glowPlugsPin PG5
#define starterMotorPin PG6
#define engineStopSolenoidPin PG7

#define hyd_actuators_master_valve_Pin PB8
#define hyd_motors_master_valve_Pin PB9

#define LH_wheel_up_Pin PG8
#define LH_wheel_down_Pin PE0
#define RH_wheel_up_Pin PF11
#define RH_wheel_down_Pin PF15

#define LH_horiz_hyd_activator_Pin PF14
#define RH_horiz_hyd_activator_Pin PD15
#define upper_vert_hyd_activator_Pin PD14
#define lower_vert_hyd_activator_Pin PE7

//////////////////////////////////////////////////////////////////////////////////////////////

#define loader_hyd_actuators_master_valve_Pin PG4

#define tilt_up_hyd_activator_Pin PE13
#define tilt_down_hyd_activator_Pin PF13
#define load_up_hyd_activator_Pin PG14
#define load_down_hyd_activator_Pin PF12

/////////////////////////////////////////////////////////////////////////////////////////////

#define drawbar_extend_pin PF4
#define drawbar_retract_pin PF5

#define drawbar_limit_switch_pin PB1

#define Serial1_RX_PIN PA10
#define Serial1_TX_PIN PA9

#define Serial2_RX_PIN PA3
#define Serial2_TX_PIN PA2

#define Serial3_TX_PIN PC10
#define Serial3_RX_PIN PC11

#define Serial5_TX_PIN PB12
#define Serial5_RX_PIN PB12

#define Serial9_TX_PIN PG0
#define Serial9_RX_PIN PG1

#endif
