# 🤖 WEEDINATOR Control Hardware

**[WEEDINATOR Homepage](https://weedinator.uk)**

The WEEDINATOR Control Hardware is a collection of customizable hardware units forming the electric and electronic building blocks for an agricultural robot. It offers a highly flexible, low-effort entry pathway for both beginners and experts, with the Main Control Units (MCUs) able to be coded in popular IDEs such as Arduino and STM Cube.

The system is designed like an extremely sophisticated breadboard, where connections are mostly left unrouted, providing an almost infinite number of configuration options, just by connecting wires to the onboard WAGO spring lever terminal blocks.

## ✨ Key Features and Design Philosophy

* **Flexibility & Customization:** The design prioritizes flexibility to avoid constantly redesigning PCBs, allowing control boxes to be quickly removed from one prototype and quickly reconfigured for another one. Most PCBs contain very few set circuits, offering the very greatest flexibility for people to create their own systems.
* **Easy Prototyping:** The system is intended as a toolkit for rapid and efficient prototyping of agricultural robots.
* **Control Capabilities:** Units can manage steering, throttles, engine start/stop, glow plugs, warning beacons, sounders, and dozens of hydraulic solenoids, while also receiving cm-level GPS coordinates.
* **Simple Coding Start:** Users are strongly advised to start with a completely blank canvas, beginning with blinking the onboard LEDs and progressing through logical self-guided steps until they can control rotary motors for steering and linear actuators for throttles.

## 📦 WEEDINATOR Hardware Units

The control system was developed through building several agri robots from Iseki and Ransomes tractors and mowers, aiming to create an autonomous weeding/cultivation machine.

| Unit | Primary Function | Details |
| :--- | :--- | :--- |
| **Box 1** | Primary robot control | Includes RC (Radio Control) and GPS functionality. Designed to control steering, throttles, engine start/stop, glow plugs, warning beacons, sounders, and hydraulic solenoids. |
| **Box 2** | Communication and Sensing | Typically used to add extra encoder channels, a small board computer (SBC) such as a Jetson Orin Nano, and a multi-camera deserialiser board. Enables communication with the Internet via 4G and supports multiple cameras for crop detection. |
| **Safety Cameras** | AI Object Detection | A 3-camera set-up based on Raspberry Pis (one set at the front, one at the back). Uses Ai object detection to help the robot avoid collision with a large set of defined objects, especially people. |

## ⚙️ Assembly Instructions: Box 1 (Control Panel)

Box 1 is the recommended starting point and should be viewed as a toolkit. The system is designed to enable small hydrostatically driven agricultural vehicles such as mowers and tractors to be controlled by RC (Radio Control) and 4G derived instructions by interacting with online databases.

### 1. Base Board PCB

This board is the first in the stack and sits neatly in the bottom of the control panel enclosure. 

#### Features:
* **Relays:** 8 x 40A removable automotive relays for operating glow plugs, starter motor relays etc.
* **Switches:** 8 x High side switches (HS) for actuating hydraulic solenoids, signal beacons etc.
* **Current Sensor:** 4 channel digital current sensor.
* **Motor Control:** Stackable 2 channel 20A motor controllers.
* **Power:** Automotive style 10-way fuse box with LED blown fuse warnings and heavy-duty 12V bus bars.

#### Assembly Notes:
* The relays are driven by 4-channel L293D chips, which themselves receive 3.3V logic signals direct from the MCU.
* **High Current Modification:** The PCB is not designed for high current, but is upgraded by soldering **heavy copper wires** on the reverse side. 
* **Soldering:** Soldering these heavy copper wires requires a heavy-duty iron, typically requiring at least 300W of power.
* **Preparation:** Before the next PCB in the stack can be screwed on, all the wiring underneath this next PCB must be completed as there will be no further access to this layer.
* **Wiring:** Thin pink wires going up to the MCU level need to be long enough to connect anywhere on the MCU PCB and should be meticulously labeled with its function (e.g., 'RELAY1'). Heavy cable connections exit the enclosure via either 12mm or 16mm nylon glands.
* **Mounting:** Ensure the correct sized metal standoffs are screwed in before screwing the base board into the enclosure.

### 2. High Side Switch Board (Optional)

This board offers an addition 20 channels of switching that is typically required for agri-robots with complex hydraulic equipment. 

#### Features:
* Provides an addition 20 channels of switching that is perfect for hydraulic solenoids and 12V beacons.
* Requires no additional components on the PCBs other than connectors and makes them extremely easy to use.

#### Assembly Notes:
* If the next layer in the stack is to be the MCU board, then the standoffs selected should be long enough to allow clearance for the MCU, which under-hangs this next board.

### 3. MCU Board (Typically at the Top of the LHS Stack)

This is the central control unit.

#### Features & Details:
* The MCU PCB has dedicated circuits only for 3 LEDs, an SBUS connection for the RC, and a 5V power bus for the MCU itself.
* There is an onboard 3V3 regulator that powers a GPS daughter board.
* Includes "helper" circuits such as a bank of voltage dividers (useful when using 12V sensors) and logic level shifters (essential for reading 5V quadrature encoders).

#### Quadrature Encoder Pin Assignments (Recommended):
Due to the minimal set connections on the 144 pins of the MCU, there is no sample code available. However, it is advisable to use the following pins for quadrature encoders:
* **TIM7:** PD12 and PD13
* **TIM6:** PE9 and PE11
* **TIM5:** PA0 and PA1

### 4. Enclosure Configuration

* **Fans:** The positions of the two fans in the enclosure should not be changed as they can interfere with electrical signals if they are in other locations.
* **USB:** The enclosure requires at least one USB connection to the outside, which is used for programming and serial communication with small board computers (SBCs) in other control boxes.
* **Connectors:** Always use external inline connectors instead of connectors that fix onto the enclosure—the external inline connectors are much more practical and easier to use.
