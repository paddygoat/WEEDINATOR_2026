'''
cd && source python_env_01/bin/activate &&
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:/home/nano/python_env_01/lib/python3.10/site-packages/nvidia/cusparselt/lib:$LD_LIBRARY_PATH &&
cd /home/nano/Documents/WEEDINATOR/Code/Jetson_nano && python3 monitor_serial_comms.py

Color	Standard (Normal)	Bright / Light
Black	\033[30m	        \033[90m
Red	    \033[31m	        \033[91m
Green	\033[32m	        \033[92m
Yellow	\033[33m	        \033[93m
Blue	\033[34m	        \033[94m
Magenta	\033[35m	        \033[95m
Cyan	\033[36m	        \033[96m
White	\033[37m	        \033[97m
'''



import serial
from serial.tools import list_ports
import json
import time
import sys
import threading

# --- Configuration ---
BAUD_RATE = 500000         # Must match the Serial.begin() call in the Arduino sketch
TIMEOUT = 5                # Timeout for serial read operation (in seconds)

# --- Monitoring Flags ---
MONITOR_ALL = False
MONITOR_encoderSteerVal = True
MONITOR_act_throtA_val = True    # New flag for Throttle A
MONITOR_act_throtB_val = True    # New flag for Throttle B

# --- Global Serial Port Management ---
open_ports = {}
ports_lock = threading.Lock()

# --- Dynamic Routing and Identification ---
mcu_routing_lock = threading.Lock()
mcu_serial_objects = {"MCU0": None, "MCU1": None} # Stores the targeted serial objects
port_labels = {} # Maps system paths like '/dev/ttyACM2' to 'USB0' or 'USB1'

def extract_json_value(data_dict, target_key):
    """Recursively searches a nested dictionary for a specific key."""
    if target_key in data_dict:
        return data_dict[target_key]
    for value in data_dict.values():
        if isinstance(value, dict):
            result = extract_json_value(value, target_key)
            if result is not None:
                return result
    return None
    
def port_recovery_thread():
    """
    Continuously monitors for dropped or newly connected serial ports
    and spins up new read threads for them to enable auto-reconnect.
    """
    while True:
        time.sleep(5)
        # Silently scan for currently available hardware ports
        current_ports = autodetect_serial_ports(quiet=True)

        # Safely check which ports are actively being monitored
        with ports_lock:
            active_ports = list(open_ports.keys())

        # If a port is physically connected but we don't have an active thread for it, start one
        for port in current_ports:
            if port not in active_ports:
                print(f"\n[RECOVERY] New or reconnected port detected: {port}. Initializing thread...")
                thread = threading.Thread(target=read_and_parse_serial, args=(port,), daemon=True)
                thread.start()


def autodetect_serial_ports(quiet=False):
    """
    Automatically detects available serial ports and returns a list of port names.
    """
    if not quiet:
        print("\n[PORT DETECTOR] Searching for available serial ports...")
        
    available_ports = [port.device for port in list_ports.comports()]
    
    if not quiet:
        print("\n[PORT DETECTOR] available_ports = ",available_ports)
        if not available_ports:
            print("[PORT DETECTOR] WARNING: No serial ports found. Ensure devices are connected.")
    
    return available_ports


def read_and_parse_serial(port_name):
    """
    Initializes the serial connection and continuously reads lines.
    It identifies which MCU is connected, applies labels, and prints diagnostics.
    """
    global mcu_serial_objects
    ser = None
    try:
        ser = serial.Serial(port=port_name, baudrate=BAUD_RATE, timeout=TIMEOUT)
    except serial.SerialException as e:
        print(f"[ERROR] Could not open {port_name}: {e}")
        return

    # Once opened, add the port object to the global dictionary
    with ports_lock:
        open_ports[port_name] = ser

    print(f"[{port_name}] --- Listening on {port_name} at {BAUD_RATE} baud ---")
    time.sleep(2)
    print(f"[{port_name}] Ready for data...")

    try:
        while True:
            # Dynamically grab the label for print statements
            with mcu_routing_lock:
                label = port_labels.get(port_name, port_name)

            line = ser.readline().decode('utf-8', errors='ignore').strip()

            if line:
                try:
                    data = json.loads(line)
                    is_dict = isinstance(data, dict)

                    if is_dict:
                        # --- Dynamic Port Identification ---
                        if "From_MCU0" in data:
                            with mcu_routing_lock:
                                if mcu_serial_objects["MCU0"] != ser:
                                    print(f"\n>>>> [ROUTING] Successfully identified MCU0 on {port_name} <<<<")
                                mcu_serial_objects["MCU0"] = ser
                                port_labels[port_name] = "USB0 (MCU0)"
                                label = "USB0 (MCU0)"
                        elif "From_MCU1" in data:
                            with mcu_routing_lock:
                                if mcu_serial_objects["MCU1"] != ser:
                                    print(f"\n>>>> [ROUTING] Successfully identified MCU1 on {port_name} <<<<")
                                mcu_serial_objects["MCU1"] = ser
                                port_labels[port_name] = "USB1 (MCU1)"
                                label = "USB1 (MCU1)"

                        # Print the valid JSON we just received
                        # --- Output Filtering Logic ---
                        if MONITOR_ALL:
                            print(f"[{label}] VALID JSON: {json.dumps(data)}")
                        else:
                            if MONITOR_encoderSteerVal:
                                steer_val = extract_json_value(data, "encoderSteerVal")
                                if steer_val is not None:
                                    print(f"[{label}] MONITORED [encoderSteerVal]: {steer_val}")
                                    
                            if MONITOR_act_throtA_val:
                                throtA_val = extract_json_value(data, "act_throtA_val")
                                if throtA_val is not None:
                                    print(f"[{label}] MONITORED [act_throtA_val]: {throtA_val}")
                                    
                            if MONITOR_act_throtB_val:
                                throtB_val = extract_json_value(data, "act_throtB_val")
                                if throtB_val is not None:
                                    print(f"[{label}] MONITORED [act_throtB_val]: {throtB_val}")

                except json.JSONDecodeError:
                    # If it's not JSON, print it as raw text
                    print(f"[{label}] RAW TXT: {line}")

            time.sleep(0.001)

    except KeyboardInterrupt:
        print(f"\n[{port_labels.get(port_name, port_name)}] Exiting thread...")
    except Exception as e:
        print(f"[{port_labels.get(port_name, port_name)}] An unexpected error occurred: {e}")
    finally:
        if ser:
            ser.close()
            with ports_lock:
                if port_name in open_ports:
                    del open_ports[port_name]
            # Safely clear routing mapping if this device unplugs
            with mcu_routing_lock:
                if mcu_serial_objects["MCU0"] == ser:
                    mcu_serial_objects["MCU0"] = None
                if mcu_serial_objects["MCU1"] == ser:
                    mcu_serial_objects["MCU1"] = None
            print(f"[{port_labels.get(port_name, port_name)}] Serial port closed.")


def status_monitor_thread():
    """
    Periodically prints the status of the connections to ensure data is still flowing.
    """
    while True:
        time.sleep(5)
        print("\n--- [SYSTEM STATUS] ---")
        with mcu_routing_lock:
            mcu0_port = [k for k, v in open_ports.items() if v == mcu_serial_objects["MCU0"]]
            mcu1_port = [k for k, v in open_ports.items() if v == mcu_serial_objects["MCU1"]]
            
            print(f"MCU0 Connected: {bool(mcu_serial_objects['MCU0'])} (Port: {mcu0_port[0] if mcu0_port else 'None'})")
            print(f"MCU1 Connected: {bool(mcu_serial_objects['MCU1'])} (Port: {mcu1_port[0] if mcu1_port else 'None'})")
        print("-----------------------\n")


def main():
    threads = []
    
    detected_ports = autodetect_serial_ports()
    
    if not detected_ports:
        print("Exiting script because no serial ports were found.")
        sys.exit(1)

    # Start a read thread for every detected port
    for port in detected_ports:
        thread = threading.Thread(target=read_and_parse_serial, args=(port,), daemon=True)
        threads.append(thread)
        thread.start()
        
    # Start the status monitor
    monitor = threading.Thread(target=status_monitor_thread, daemon=True)
    threads.append(monitor)
    monitor.start()
    
    try:
        # Keep the main thread alive and monitor for dropped/reconnected ports
        while True:
            time.sleep(5)
            
            # Silently scan for currently available hardware ports
            current_ports = autodetect_serial_ports(quiet=True)
            
            # Safely check which ports are actively being monitored
            with ports_lock:
                active_ports = list(open_ports.keys())
            
            # If a port is physically connected but we don't have an active thread for it, start one
            for port in current_ports:
                if port not in active_ports:
                    print(f"\n[RECOVERY] New or reconnected port detected: {port}. Initializing thread...")
                    thread = threading.Thread(target=read_and_parse_serial, args=(port,), daemon=True)
                    thread.start()
            
    except KeyboardInterrupt:
        print("\nMain thread received interrupt. Shutting down...")
    except Exception as e:
        print(f"An unexpected error occurred in main loop: {e}")

if __name__ == "__main__":
    main()
