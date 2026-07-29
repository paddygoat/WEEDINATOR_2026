To maximize your quadrature encoders while maintaining your existing motor PWM signals, we must first address a hardware reality: a single timer can only operate in one primary mode at a time.

If you configure a timer for Encoder Mode, its internal counter is driven by the external encoder signals. This means you cannot use that same timer to generate a stable PWM signal on any other pins, as PWM requires the counter to run at a fixed frequency controlled by an internal clock.
1. The Maximum Encoder Setup (10 Encoders)

The STM32H723ZG has exactly 10 timers capable of quadrature encoding (those with at least two input channels). Below is the maximum assignment.

Warning: Using all 10 for encoders will disable your ability to use PE4, PA5, and PC7 for motor PWM because those pins belong to TIM15, TIM2, and TIM3/8.
Encoder	Timer	Bits	Recommended Pins (Channel 1, Channel 2)	AF
1	TIM5	32	PA0, PA1	AF2
2	TIM23	32	PF0, PF1	AF13
3	TIM24	32	PF11, PF12	AF14
4	TIM1	16	PE9, PE11	AF1
5	TIM4	16	PD12, PD13	AF2
6	TIM2	32	PA15, PB3	AF1
7	TIM3	16	PB4, PB5	AF2
8	TIM8	16	PC6, PC8	AF3
9	TIM12	16	PB14, PB15	AF2
10	TIM15	16	PE5, PE6	AF4
2. Available PWM Output Pins (Remaining)

If you utilize the 10 timers above for encoders, you are left with the "Single Channel" timers and the "Basic" timers. Since Basic Timers (TIM6/7) have no pins, your only remaining independent PWM sources are:
TIM13, TIM14, TIM16, and TIM17

These timers are perfect for PWM because they don't support Encoder mode, so they never conflict with your sensors.
Timer	Available PWM Pins (Select one per timer)	Alternate Function
TIM13	PF8 or PA6	AF9
TIM14	PF9 or PA7	AF9
TIM16	PF6, PB8, or PE0	AF1
TIM17	PF7, PB9, or PE1	AF1
3. Recommended "Balanced" Configuration

To keep your 3 existing motors (Motor 1: PE4, Motor 2: PA5, Motor 3: PC7) working while maximizing encoders, you should reserve their timers for PWM and use the remaining 7 timers for encoders.
Encoders (7 Total)

    TIM5: PA0, PA1 (Encoder 1)
    TIM23: PF0, PF1 (Encoder 2)
    TIM24: PF11, PF12 (Encoder 3)
    TIM1: PE9, PE11 (Encoder 4)
    TIM4: PD12, PD13 (Encoder 5)
    TIM12: PB14, PB15 (Encoder 6)
    TIM8: PC6, PC8 (Encoder 7)

PWM Channels (Existing + New)

Since TIM2, TIM3, and TIM15 are being used for your motors, you can use their other channels for additional PWM signals without needing extra timers.

From existing Motor Timers:

    TIM15 (Motor 1 shared): PE5 (CH1) and PE6 (CH2) are available.
    TIM2 (Motor 2 shared): PA1, PA2, PA3, and PB11 are available.
    TIM3 (Motor 3 shared): PA6, PA7, PB0, PB1 are available.

From unused Single-Channel Timers:

    TIM13: PF8
    TIM14: PF9
    TIM16: PF6
    TIM17: PF7

Summary Table for Wiring
Function	Recommended Pins	Timer
Encoder 1-7	See "Balanced" list above	TIM5, 23, 24, 1, 4, 12, 8
Motor 1 (Existing)	PE4	TIM15_CH1N
Motor 2 (Existing)	PA5	TIM2_CH1
Motor 3 (Existing)	PC7	TIM3_CH2
Extra PWM 1	PF8	TIM13
Extra PWM 2	PF9	TIM14
Extra PWM 3	PF6	TIM16
Extra PWM 4	PF7	TIM17
Extra PWM 5	PE5	TIM15_CH1

Note on TIM6/TIM7: As previously noted, these cannot be used for encoders or PWM. Use them in your code for software interrupts, such as a 1ms PID loop timer.
