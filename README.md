# WEEDINATOR_2026
# 🤖 WEEDINATOR Control Hardware

[cite_start]The WEEDINATOR Control Hardware is a collection of customizable hardware units forming the electric and electronic building blocks for an agricultural robot[cite: 3]. [cite_start]It offers a highly flexible, low-effort entry pathway for both beginners and experts, with the Main Control Units (MCUs) codable in popular IDEs like Arduino and STM Cube[cite: 7].

[cite_start]The system is designed like an extremely sophisticated breadboard, where connections are mostly left unrouted, providing an almost infinite number of configuration options by connecting wires to the onboard WAGO spring lever terminal blocks[cite: 8].

## ✨ Key Features and Design Philosophy

* [cite_start]**Flexibility & Customization:** The design prioritizes flexibility to avoid constantly redesigning PCBs, allowing control boxes to be quickly removed and reconfigured between different prototypes[cite: 17]. [cite_start]Most PCBs contain very few set circuits, enabling users to create their own systems[cite: 35].
* [cite_start]**Easy Prototyping:** The system is intended as a toolkit for rapid and efficient prototyping of agricultural robots[cite: 9, 15].
* [cite_start]**Control Capabilities:** Units can manage steering, throttles, engine start/stop, glow plugs, warning beacons, sounders, and dozens of hydraulic solenoids, while also receiving cm-level GPS coordinates[cite: 4].
* [cite_start]**Simple Coding Start:** Users are strongly advised to start with a blank canvas, beginning with blinking the onboard LEDs, progressing to using an RC module to control the LEDs, and eventually controlling rotary motors for steering and linear actuators for throttles[cite: 9, 10, 11].

## 📦 WEEDINATOR Hardware Units

[cite_start]The control system has been developed through building several agri robots from Iseki and Ransomes tractors and mowers, aiming to create an autonomous weeding/cultivation machine[cite: 16].

| Unit | Primary Function | Details |
| :--- | :--- | :--- |
| **Box 1** | [cite_start]Primary robot control [cite: 20] | [cite_start]Includes RC (Radio Control) and GPS functionality[cite: 20]. [cite_start]Designed to control steering, throttles, engine start/stop, glow plugs, warning beacons, sounders, and hydraulic solenoids[cite: 4].  |
| **Box 2** | [cite_start]Communication and Sensing [cite: 21] | [cite_start]Typically used to add extra encoder channels, a small board computer (SBC) like a Jetson Orin Nano, and a multi-camera deserializer board[cite: 5]. [cite_start]Enables communication with the Internet via 4G and supports multiple cameras for crop detection[cite: 21]. |
| **Safety Cameras** | AI Object Detection | [cite_start]A 3-camera set-up based on Raspberry Pis (one set at the front, one at the back)[cite: 22]. [cite_start]Uses AI object detection to help the robot avoid collisions, especially with people[cite: 6]. |

## ⚙️ Assembly Instructions: Box 1 (Control Panel)

[cite_start]Box 1 is the recommended starting point and should be viewed as a toolkit[cite: 9]. [cite_start]The system is designed to enable small hydrostatically driven agricultural vehicles (mowers and tractors) to be controlled by RC and 4G derived instructions[cite: 31].

### 1. Base Board PCB (M0020A)

[cite_start]This board is the first in the stack and sits in the bottom of the control panel enclosure[cite: 67].

#### Features:
* [cite_start]**Relays:** 8 x 40A removable automotive relays for operating glow plugs, starter motor relays, etc.[cite: 69].
* [cite_start]**Switches:** 8 x High side switches (HS) for actuating hydraulic solenoids, signal beacons, etc.[cite: 70].
* [cite_start]**Current Sensor:** 4 channel digital current sensor[cite: 71].
* [cite_start]**Motor Control:** Stackable 2 channel 20A motor controllers[cite: 72].
* [cite_start]**Power:** Automotive style 10-way fuse box with LED blown fuse warnings [cite: 73] [cite_start]and heavy-duty 12V bus bars[cite: 74].


#### Assembly Notes:
* [cite_start]The relays are driven by 4-channel L293D chips, receiving 3.3V logic signals directly from the MCU[cite: 76].
* [cite_start]**High Current Modification:** The PCB is not designed for high current but is upgraded by soldering **heavy copper wires** on the reverse side[cite: 77].
* [cite_start]**Soldering:** Soldering these heavy copper wires requires a heavy-duty iron, typically at least 300W of power[cite: 85].
* [cite_start]**Preparation:** Before the next PCB in the stack is screwed on, all wiring underneath it must be completed, as there will be no further access to this layer[cite: 86].
* [cite_start]**Wiring:** Thin pink wires going up to the MCU level should be meticulously labeled (e.g., 'RELAY1') and must be long enough to connect anywhere on the MCU PCB[cite: 89]. [cite_start]Heavy cable connections exit the enclosure via 12mm or 16mm nylon glands and should also be labeled to match the thin wire that activates them[cite: 90, 92].
* [cite_start]**Mounting:** Ensure the correct metal standoffs are screwed in before securing the base board, as they cannot be changed later without disassembling the whole system[cite: 78].

### 2. High Side Switch Board (Optional)

[cite_start]This board is typically required for agri-robots with complex hydraulic equipment[cite: 34].

#### Features:
* [cite_start]Provides an additional 20 channels of high side switching[cite: 149].
* [cite_start]Perfect for hydraulic solenoids and 12V beacons[cite: 149].
* [cite_start]Requires no additional components on the PCB other than connectors, making them extremely easy to use[cite: 150].


#### Assembly Notes:
* [cite_start]If the MCU board is the next layer, the standoffs selected must be long enough to allow clearance for the MCU, which under-hangs the board[cite: 151].

### 3. MCU Board (Typically at the Top of the LHS Stack)

This is the central control unit.

#### Features & Details:
* [cite_start]The MCU PCB has dedicated circuits only for 3 LEDs, an SBUS connection for the RC, and a 5V power bus for the MCU itself[cite: 36].
* [cite_start]An onboard 3V3 regulator powers a GPS daughter board[cite: 37].
* [cite_start]Includes "helper" circuits like a bank of voltage dividers (useful for 12V sensors) and logic level shifters (essential for reading 5V quadrature encoders)[cite: 38].

#### Quadrature Encoder Pin Assignments (Recommended):
[cite_start]Due to the minimal set connections on the 144 pins of the MCU, there is no sample code available[cite: 39]. However, it is advisable to use the following pins for quadrature encoders:
* [cite_start]**TIM7:** PD12 and PD13 [cite: 41]
* [cite_start]**TIM6:** PE9 and PE11 [cite: 42]
* [cite_start]**TIM5:** PA0 and PA1 [cite: 43]

### 4. Enclosure Configuration

* [cite_start]**Fans:** Note the positions of the two fans in the enclosure; they should not be changed as they can interfere with electrical signals if relocated[cite: 100, 101].
* [cite_start]**USB:** The enclosure requires at least one external USB connection for programming and serial communication with SBCs in other control boxes[cite: 102].
* [cite_start]**Connectors:** Always use external inline connectors instead of connectors that fix onto the enclosure, as they are more practical and easier to use[cite: 91].
