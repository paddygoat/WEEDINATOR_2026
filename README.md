# 🤖 WEEDINATOR Control Hardware

The WEEDINATOR Control Hardware is a collection of customizable hardware units forming the electric and electronic building blocks for an agricultural robot. It offers a highly flexible, low-effort entry pathway for both beginners and experts, with the Main Control Units (MCUs) codable in popular IDEs like Arduino and STM Cube.

The system is designed like an extremely sophisticated breadboard, where connections are mostly left unrouted, providing an almost infinite number of configuration options by connecting wires to the onboard WAGO spring lever terminal blocks.

## ✨ Key Features and Design Philosophy

* **Flexibility & Customization:** The design prioritizes flexibility to avoid constantly redesigning PCBs, allowing control boxes to be quickly removed and reconfigured between different prototypes. Most PCBs contain very few set circuits, enabling users to create their own systems.
* **Easy Prototyping:** The system is intended as a toolkit for rapid and efficient prototyping of agricultural robots.
* **Control Capabilities:** Units can manage steering, throttles, engine start/stop, glow plugs, warning beacons, sounders, and dozens of hydraulic solenoids, while also receiving cm-level GPS coordinates.
* **Simple Coding Start:** Users are strongly advised to start with a blank canvas, beginning with blinking the onboard LEDs, progressing to using an RC module to control the LEDs, and eventually controlling rotary motors for steering and linear actuators for throttles.

## 📦 WEEDINATOR Hardware Units

The control system has been developed through building several agri robots from Iseki and Ransomes tractors and mowers, aiming to create an autonomous weeding/cultivation machine.

| Unit | Primary Function | Details |
| :--- | :--- | :--- |
| **Box 1** | Primary robot control | Includes RC (Radio Control) and GPS functionality. Designed to control steering, throttles, engine start/stop, glow plugs, warning beacons, sounders, and hydraulic solenoids.  |
| **Box 2** | Communication and Sensing | Typically used to add extra encoder channels, a small board computer (SBC) like a Jetson Orin Nano, and a multi-camera deserializer board. Enables communication with the Internet via 4G and supports multiple cameras for crop detection. |
| **Safety Cameras** | AI Object Detection | A 3-camera set-up based on Raspberry Pis (one set at the front, one at the back). Uses AI object detection to help the robot avoid collisions, especially with people. |

## ⚙️ Assembly Instructions: Box 1 (Control Panel)

Box 1 is the recommended starting point and should be viewed as a toolkit. The system is designed to enable small hydrostatically driven agricultural vehicles such as mowers and tractors to be controlled by RC (Radio Control) and 4G derived instructions by interacting with online databases.

### 1. Base Board PCB

This board is the first in the stack and sits in the bottom of the control panel enclosure.

#### Features:
* **Relays:** 8 x 40A removable automotive relays for operating glow plugs, starter motor relays, etc.
* **Switches:** 8 x High side switches (HS) for actuating hydraulic solenoids, signal beacons, etc.
* **Current Sensor:** 4 channel digital current sensor.
* **Motor Control:** Stackable 2 channel 20A motor controllers.
* **Power:** Automotive style 10-way fuse box with LED blown fuse warnings and heavy-duty 12V bus bars.



#### Assembly Notes:
* The relays are driven by 4-channel L293D chips, receiving 3.3V logic signals directly from the MCU.
* **High Current Modification:** The PCB is not designed for high current but is upgraded by soldering **heavy copper wires** on the reverse side.
* **Soldering:** Soldering these heavy copper wires requires a heavy-duty iron, typically at least 300W of power.
* **Preparation:** Before the next PCB in the stack is screwed on, all wiring underneath it must be completed, as there will be no further access to this layer.
* **Wiring:** Thin pink wires going up to the MCU level should be meticulously labeled (e.g., 'RELAY1') and must be long enough to connect anywhere on the MCU PCB. Heavy cable connections exit the enclosure via 12mm or 16mm nylon glands and should also be labeled to match the thin wire that activates them.
* **Mounting:** Ensure the correct metal standoffs are screwed in before securing the base board, as they cannot be changed later without disassembling the whole system.

### 2. High Side Switch Board (Optional)

This board is typically required for agri-robots with complex hydraulic equipment.

#### Features:
* Provides an additional 20 channels of high side switching.
* Perfect for hydraulic solenoids and 12V beacons.
* Requires no additional components on the PCB other than connectors, making them extremely easy to use.



#### Assembly Notes:
* If the MCU board is the next layer, the standoffs selected must be long enough to allow clearance for the MCU, which under-hangs the board.

### 3. MCU Board (Typically at the Top of the LHS Stack)

This is the central control unit.

#### Features & Details:
* The MCU PCB has dedicated circuits only for 3 LEDs, an SBUS connection for the RC, and a 5V power bus for the MCU itself.
* An onboard 3V3 regulator powers a GPS daughter board.
* Includes "helper" circuits like a bank of voltage dividers (useful for 12V sensors) and logic level shifters (essential for reading 5V quadrature encoders).

#### Quadrature Encoder Pin Assignments (Recommended):
Due to the minimal set connections on the 144 pins of the MCU, there is no sample code available. However, it is advisable to use the following pins for quadrature encoders:
* **TIM7:** PD12 and PD13
* **TIM6:** PE9 and PE11
* **TIM5:** PA0 and PA1

### 4. Enclosure Configuration

* **Fans:** Note the positions of the two fans in the enclosure; they should not be changed as they can interfere with electrical signals if relocated.
* **USB:** The enclosure requires at least one external USB connection for programming and serial communication with SBCs in other control boxes.
* **Connectors:** Always use external inline connectors instead of connectors that fix onto the enclosure, as they are more practical and easier to use.
