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

## ⚙️ Assembly Instructions: Please download the Instructions PDF here: [Assembly_instructions](https://github.com/paddygoat/WEEDINATOR_2026/blob/main/Instructions/Control_panel_assembly_instructions_01.pdf)
