
'''
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

# This Python script reads data from two serial ports concurrently using threads.
# It validates if each received line is a well-formed JSON string and then deserializes it.
# It dynamically identifies which port is connected to MCU0 and MCU1 based on incoming data.
# It then routes targeted JSON commands exclusively to the intended microcontrollers.
import passwords
import serial
from serial.tools import list_ports
import json
import time
import sys
import threading
import datetime
from datetime import datetime
import requests
from typing import List, Union # Import List and Union for more specific type hints
import math
import os
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox

import shared_state             # Import the state
from weedinator_gui import gui_thread  # Import the GUI function
from weedinator_vision import update_camera_frame # Import the vision stuff

# --- Configuration ---
CALL_FREQUENCY = 20        # Hertz (needs to be at least double the MCU frequencies, assuming they equal each other).
BAUD_RATE = 500000         # Must match the Serial.begin() call in the Arduino sketch
TIMEOUT = 5                # Timeout for serial read operation (in seconds)
PRINT_JSON_ONLY = False    # If True, only prints the "--> VALID JSON DETECTED <--" message.
PRINT_JSON = False
PRINT_MCU_SERIAL_ONLY = True

# --- Global Serial Port Management ---
open_ports = {}
ports_lock = threading.Lock()

# --- NEW: Dynamic Routing and Identification ---
mcu_routing_lock = threading.Lock()
mcu_serial_objects = {"MCU0": None, "MCU1": None} # Stores the targeted serial objects
port_labels = {} # Maps system paths like '/dev/ttyACM2' to 'USB0' or 'USB1'

# --- Global Shared State for Communication ---
should_illuminate_blue_mcu1 = False
should_illuminate_orange_mcu0 = False
ch14_data = 555
ch13_data = 555
ch12_data = 992 # horizontal hydraulic actuator
ch11_data = 555
ch10_data = 555
ch9_data = 555
ch6_data = 555

prev_waypoint_epoch_time = 0
last_waypoint_epoch_time = 0

# Global variables for coordinates, to be updated and sent
current_lat = 53.302801158199024
current_lon = -4.240779625855205

# Connection Tracking (Heartbeats)
last_mcu0_time = 0
last_mcu1_time = 0

current_GPSFixTime = "000000"

MCU0_count = 0
MCU1_count = 0

#TODO: Are these variables still used:
current_acthead = 0
current_myRelPosAcc = 0
act_steer_angle = 0
encoderSteerVal = 0

#################################################################################################################

#################################################################################################################
def manage_waypoints_thread(): # reads desired latitude and longitude pair, used to be called thread_two


    global current_acthead
    global current_GPSFixTime
    global current_myRelPosAcc
    global shutDown_value
    global throttAVal
    global aliveFlag2
    global mySpeed

    distance_for_speed = 0.0
    prev_lat = 1.0
    prev_lon = 1.0

    while True:
        with shared_state.data_lock:
            pass
            # print("waypointsArray: ",waypointsArray)
        try:
            with shared_state.data_lock:
                # flip waypointsArray on first axis if necessary:
                # Flip the waypointsArray on the 1st axis (reverse the order of the inner lists)
                flipped_waypointsArray = shared_state.waypointsArray[::-1]
                current_waypoints = flipped_waypointsArray[0]
                
                shared_state.des_lat = current_waypoints[1]
                shared_state.des_lon = current_waypoints[2]
                # print("des_lat: ", shared_state.des_lat, "des_lon: ", shared_state.des_lon)
                # print("current_lat: ", current_lat, "current_lon: ", current_lon)
            
                # distance_to_go = haversine_distance(current_lat, current_lon, des_lat, des_lon)*1000
                shared_state.distance_to_go = haversine_distance(float(shared_state.act_lat), float(shared_state.act_lon), shared_state.des_lat, shared_state.des_lon) * 1000
                # print(f"\033[96mdistance_to_go:  {distance_to_go} meters\033[0m")

            # TODO: change the distance_to_go value to something more sensible after testing:
            if (shared_state.distance_to_go < 1.0):
                print("\033[92mWay point was reached !!!!\033[0m") # Green
                # delete the data at waypointsArray[0]
                shared_state.waypointsArray = shared_state.waypointsArray[:-1]
        
            # print("current_waypoints: ",current_waypoints)
            # print("current_lat: ", current_lat, "current_lon: ", current_lon)
            # print("des_lat: ", des_lat, "des_lon: ", shared_state.des_lon)
            # print(f"\033[96mdistance_to_go:  {distance_to_go} meters\033[0m")
            # print("distance_to_go: ",distance_to_go, " meters")
            # print("")
        except:
            pass
            # print("\033[93mNo way points downloaded yet !!\033[0m")
            # print("No way points downloaded yet !!")
            

            
        time.sleep(0.05) # Small delay to prevent 100% CPU usage

#################################################################################################################
def haversine_distance(current_lat, current_lon, des_lat, des_lon):
    """
    Calculates the distance between two points on Earth using the Haversine formula.

    Args:
        current_lat (float): Latitude of the first point in degrees.
        current_lon (float): Longitude of the first point in degrees.
        des_lat (float): Latitude of the second point in degrees.
        des_lon (float): Longitude of the second point in degrees.

    Returns:
        float: The distance between the two points in kilometers.
    """
    # R = 6371  # Radius of Earth in kilometers
    R = 6364.581 # Llanbedrgoch.

    # Convert latitudes and longitudes from degrees to radians
    lat1_rad = math.radians(current_lat)
    lon1_rad = math.radians(current_lon)
    lat2_rad = math.radians(shared_state.des_lat)
    lon2_rad = math.radians(shared_state.des_lon)

    # Calculate the differences in coordinates
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Apply the Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance
    
#################################################################################################################   
def process_data_string_to_2d_array(data_string: str) -> List[List[Union[int, float]]]:
    """
    Processes a string containing 'id', 'des_lat', and 'des_lon' data
    into a 2D array (list of lists).

    Each inner list will contain [id, des_lat, des_lon] as numbers.

    Args:
        data_string: The input string with data entries separated by '?'.
                     Each entry has fields like 'id: X; des_lat: Y; des_lon: Z;'.

    Returns:
        A 2D array (list of lists), where each inner list represents an entry
        with [id (int), des_lat (float), des_lon (float)].
        Returns an empty list if the input string is empty or contains no valid data.
    """

    result_array = []

    # Split the main string into individual data entries.
    # We strip any leading/trailing whitespace from each entry.
    entries = [entry.strip() for entry in data_string.split('?') if entry.strip()]

    for entry_str in entries:
        # Split each entry into its key-value pairs.
        # Filter out any empty strings that might result from extra semicolons.
        parts = [part.strip() for part in entry_str.split(';') if part.strip()]

        current_id = None
        current_lat = None
        current_lon = None

        for part in parts:
            # Split each part into key and value.
            # Example: "id: 242" -> ["id", " 242"]
            if ':' in part:
                key, value_str = part.split(':', 1) # Split only on the first colon
                key = key.strip()
                value_str = value_str.strip()

                try:
                    if key == 'id':
                        current_id = int(value_str)
                    elif key == 'des_lat':
                        current_lat = float(value_str)
                    elif key == 'des_lon':
                        current_lon = float(value_str)
                except ValueError:
                    # Handle cases where conversion fails (e.g., non-numeric values)
                    print(f"Warning: Could not convert value '{value_str}' for key '{key}'. Skipping this part.")
                    continue # Skip to the next part

        # If all three required fields are found, add them to the result array.
        if current_id is not None and current_lat is not None and current_lon is not None:
            result_array.append([current_id, current_lat, current_lon])
        else:
            # print(f"Warning: Incomplete data entry found: '{entry_str}'. Skipping.")
            print(f"\033[91mWarning: Incomplete data entry found: '{entry_str}'. Skipping.\033[0m") # red

    return result_array

#################################################################################################################
def download_waypoints(): # Called by read_database_thread()
    print("Try to download waypoints .....")
    url_retreive_all_data = "http://www.################/control_room_database/show_all_data.php"
    headers = {"X-API-Password": passwords.get_password()}
    
    try:
        response_retreive_all_data = requests.get(url_retreive_all_data, headers=headers)
        response_retreive_all_data.raise_for_status()
        print("\033[92mNew way points data retreived successfully!\033[0m")
        all_data = str(response_retreive_all_data.text).strip()
        return process_data_string_to_2d_array(all_data)
    except requests.exceptions.RequestException as e:
        print(f"\033[91mFailed to download waypoints: {e}\033[0m")
#################################################################################################################
def parse_data_string_2(data_string):
    """
    Parses a string with key-value pairs separated by semi colons which is more compatible with how php works,
    where each pair is key:value.
    """
    # Create a dictionary to store the parsed values
    parsed_values = {}

    # Split the main string by the semi colon character
    pairs = data_string.split(';')

    for pair in pairs:
        # Split each pair by the colon character
        if ':' in pair:
            key, value_str = pair.split(':', 1) # Split only on the first colon

            # Clean up key and convert value
            key = key.strip()
            try:
                # Try to convert to float. If it fails, keep it as a string.
                # This handles cases like 'null' or other non-numeric values
                value = float(value_str)
            except ValueError:
                value = value_str.strip() # Keep as string if not a valid float

            parsed_values[key] = value
    # usage: parsed_values = parse_data_string_2(data_string)
    return parsed_values

#################################################################################################################
def retreive_data_from_des_coords_table():
    """
    Retreives data with the 'show_single_line.php' script for the des_coords table.
    The Mapping app uses a temporary table called 'control_room' which gets copied to 'des_coords' when all editing of waypoints is completed.
    Args:
        time_stamp:time_stamp
    """
    # print("Try to get single line time stamp data ....")
    url_retreive_min = "http://www.################/control_room_database/show_single_line.php"
    headers = {"X-API-Password": passwords.get_password()}

    try:
        response_retreive_min = requests.get(url_retreive_min, headers=headers)
        # print("response_retreive_min: ",response_retreive_min)
        response_retreive_min.raise_for_status()
        
        my_data = str(response_retreive_min.text).strip()
        # print("my_data: ",my_data)
        time_stamp_data = my_data.replace(' ', '').replace('<br>', '')
        # print("time_stamp_data: ",time_stamp_data)
        data_dict_time_stamp = parse_data_string_2(time_stamp_data)
        # print("data_dict_time_stamp: ",data_dict_time_stamp)
        time_stamp_value = data_dict_time_stamp.get('time_stamp')
        # print("time_stamp_value: ",time_stamp_value)
        
        date_format = '%Y-%m-%d%H:%M:%S'
        time_stamp_value = datetime.strptime(time_stamp_value, date_format)
        # print("time_stamp_value: ",time_stamp_value)
        return time_stamp_value.timestamp()

    except Exception as e:
        if not PRINT_MCU_SERIAL_ONLY:
            print(f"\033[91mAn error occurred: {e}\033[0m")
#################################################################################################################      
def read_database_thread():
    # Firstly, check if there's new waypoint data inputted by user from mapping app:
    # The Mapping app uses a temporary table called 'control_room' which gets copied to 'des_coords' when all editing of waypoints is completed.
    # try:
    last_waypoint_epoch_time = 0
    global prev_waypoint_epoch_time
    
    while True:
        try:
            # Attempt to retrieve data
            result = retreive_data_from_des_coords_table()
    
            # If the DB exists but the specific cell is empty, it might return None
            # We force it to be 0 in that case.
            last_waypoint_epoch_time = result if result is not None else 0
        except Exception as e:
            # If the query itself fails (table missing, etc.)
            last_waypoint_epoch_time = 0

        with shared_state.data_lock:
            # Now this check is robust because we know it's at least 0
            aliveFlag1 = (last_waypoint_epoch_time > 0)
            print("waypoints database latest epoch_time value: ",last_waypoint_epoch_time)
            
        '''
        read_database_thread checks the epoch time and downloads waypoints every 60 seconds.
        database_update_thread also checks the epoch time and downloads waypoints every 5 seconds.
        '''

        if last_waypoint_epoch_time > prev_waypoint_epoch_time:
            print("\033[93mDetected an increase in waypoint epoch time !!\033[0m") # Yellow
            print("Now download all the waypoints from des_coords table .....")
            prev_waypoint_epoch_time = last_waypoint_epoch_time
            with shared_state.data_lock:
                shared_state.waypointsArray = download_waypoints()
                # print("waypointsArray from des_coords table: ",shared_state.waypointsArray)
        time.sleep(60)
#################################################################################################################
def autodetect_serial_ports():
    """
    Automatically detects available serial ports and returns a list of port names.
    """
    print("\n[PORT DETECTOR] Searching for available serial ports...")
    available_ports = [port.device for port in list_ports.comports()]
    
    if not available_ports:
        print("[PORT DETECTOR] WARNING: No serial ports found. Ensure devices are connected.")
    
    return available_ports
#################################################################################################################
def send_command_thread():
    """
    Thread function that periodically sends targeted JSON commands
    exclusively to the corresponding identified serial ports.
    """
    try:
        while True:
            # 1. Read the global state safely 
            with shared_state.data_lock:
                current_state_blue_LED_MCU1 = should_illuminate_blue_mcu1
                current_state_orange_LED_MCU0 = should_illuminate_orange_mcu0
                current_ch14_data = ch14_data
                current_ch13_data = ch13_data
                current_ch12_data = ch12_data # horizontal hydraulic actuator
                current_ch11_data = ch11_data
                current_ch10_data = ch10_data
                current_ch9_data = ch9_data
                current_ch6_data = ch6_data
                des_lat_to_send = shared_state.des_lat
                des_lon_to_send = shared_state.des_lon
                slider1val = shared_state.slider_1_val
                slider2val = shared_state.slider_2_val
                # print(f"\033[91mdes_lon_to_send: '{des_lon_to_send}'. \033[0m")

            
            # 2. Build the split, targeted commands
            command_mcu0 = {
                "To_MCU0": {
                    "illuminate_orange_LED": current_state_orange_LED_MCU0,
                    "des_lat": des_lat_to_send,
                    "des_lon": des_lon_to_send
                }
            }
            
            command_mcu1 = {
                "To_MCU1": {
                    "illuminate_blue_LED": current_state_blue_LED_MCU1,
                    "ch14_data": current_ch14_data,
                    "ch13_data": current_ch13_data,
                    "ch12_data": current_ch12_data,
                    "ch11_data": current_ch11_data,
                    "ch10_data": current_ch10_data,
                    "ch9_data": current_ch9_data,
                    "ch6_data": current_ch6_data,
                    "slider1val": slider1val,
                    "slider2val": slider2val
                }
            }
            
            cmd_str_mcu0 = json.dumps(command_mcu0) + '\n'
            cmd_str_mcu1 = json.dumps(command_mcu1) + '\n'

            # 3. Get the identified serial port objects
            with mcu_routing_lock:
                ser_mcu0 = mcu_serial_objects["MCU0"]
                ser_mcu1 = mcu_serial_objects["MCU1"]

            # 4. Route the commands to their precise targets (if identified)
            if ser_mcu0:
                try:
                    ser_mcu0.write(cmd_str_mcu0.encode('utf-8'))
                    ser_mcu0.flush()
                except serial.SerialTimeoutException:
                    pass
                except serial.SerialException as e:
                    print(f"[COMMAND SENDER] ERROR: Serial error writing to USB0: {e}")

            if ser_mcu1:
                try:
                    ser_mcu1.write(cmd_str_mcu1.encode('utf-8'))
                    ser_mcu1.flush()
                except serial.SerialTimeoutException:
                    pass
                except serial.SerialException as e:
                    print(f"[COMMAND SENDER] ERROR: Serial error writing to USB1: {e}")

            # Wait for a short interval before the next transmission
            time.sleep(1/CALL_FREQUENCY)
            
    except KeyboardInterrupt:
        print("\n[COMMAND SENDER] Exiting sender thread...")
    except Exception as e:
        print(f"[COMMAND SENDER] An unexpected error occurred in sender thread: {e}")
#################################################################################################################
def read_and_parse_serial(port_name):
    """
    Initializes the serial connection and continuously reads lines.
    It identifies which MCU is connected, applies labels ('USB0'/'USB1'), 
    and updates global states.
    port_mcu_map: variable is never defined anywhere in the script!!
    """
    global mcu_serial_objects, port_mcu_map
    ser = None
    try:
        ser = serial.Serial(port=port_name, baudrate=BAUD_RATE, timeout=TIMEOUT)
    except serial.SerialException as e:
        return

    # Once opened, add the port object to the global dictionary
    with ports_lock:
        open_ports[port_name] = ser

    print(f"[{port_name}] --- Listening on {port_name} at {BAUD_RATE} baud ---")
    time.sleep(2)
    print(f"[{port_name}] Ready for data...")
    
    global MCU0_count, MCU1_count
    MCU0_count = 0
    MCU1_count = 0

    try:
        while True:
            MCU0_count = MCU0_count +1
            MCU1_count = MCU1_count +1
            # In theory,because the MCU0 thread rarely sees an MCU1 message, it will constantly drive MCU1_count past 100 and force shared_state.MCU1_alive = False, directly fighting the MCU1 thread that is trying to keep it True. This will result in rapid GUI flickering and false disconnects. In practice, this does not happen !!
            # Dynamically grab the label for print statements
            with mcu_routing_lock:
                label = port_labels.get(port_name, port_name)

            line = ser.readline().decode('utf-8').strip()

            if line:
                if not PRINT_JSON_ONLY and not PRINT_MCU_SERIAL_ONLY:
                    print(f"\n[{label}] RAW RECEIVE: {line}")
                
                try:
                    data = json.loads(line)
                    is_dict = isinstance(data, dict)

                    if is_dict:
                        # --- Dynamic Port Identification ---
                        if "From_MCU0" in data:
                            with mcu_routing_lock:
                                mcu_serial_objects["MCU0"] = ser
                                port_labels[port_name] = "USB0"
                                label = "USB0"
                        elif "From_MCU1" in data:
                            with mcu_routing_lock:
                                mcu_serial_objects["MCU1"] = ser
                                port_labels[port_name] = "USB1"
                                label = "USB1"

                        # VALID JSON OBJECT DETECTED
                        if PRINT_JSON and not PRINT_MCU_SERIAL_ONLY:
                            print(f"[{label}] --> VALID JSON DETECTED <--")
                            print(json.dumps(data, indent=4, ensure_ascii=False))
                        
                        # --- Check for incoming command to control MCU1 (Source: From_MCU0) ---
                        # FIX: Check if "From_MCU0" exists before accessing it
                        if "From_MCU0" in data and "To_MCU1" in data["From_MCU0"]:
                            mcu1_command = data["From_MCU0"]["To_MCU1"]
                            if MCU0_count < 100:
                                with shared_state.data_lock:
                                    shared_state.MCU0_alive = True
                                # print("MCU0 is alive !! ", MCU0_count)
                            MCU0_count = 0

                            if isinstance(mcu1_command, dict):
                                if "illuminate_blue_LED" in mcu1_command:
                                    incoming_state_str = str(mcu1_command["illuminate_blue_LED"]).lower()
                                    global should_illuminate_blue_mcu1
                                    
                                    with shared_state.data_lock:
                                        if incoming_state_str == "true":
                                            should_illuminate_blue_mcu1 = True
                                            # print(f"[{label}] >>> RECEIVED CMD: Setting shared MCU1 blue LED state to TRUE.")
                                        elif incoming_state_str == "false":
                                            should_illuminate_blue_mcu1 = False
                                            # print(f"[{label}] >>> RECEIVED CMD: Setting shared MCU1 blue LED state to FALSE.")

                                if "ch14_data" in mcu1_command:
                                    incoming_ch14_data = mcu1_command["ch14_data"]
                                    incoming_ch13_data = mcu1_command["ch13_data"]
                                    
                                    # --- AUTO WEED LOGIC FOR CH12 ---
                                    with shared_state.data_lock:
                                        is_auto_weed = shared_state.auto_weed_enabled
                                        # Safely fetch from shared_state (defaults to 555 if missing)
                                        shared_ch12 = getattr(shared_state, 'ch12_data', 555) 
                                        
                                    if is_auto_weed:
                                        # Read from shared_state when AUTO WEED is ON
                                        incoming_ch12_data = shared_ch12
                                        print("Reading ch12_data from shared_state.py: ",incoming_ch12_data)
                                    else:
                                        # Read from MCU0 when AUTO WEED is OFF
                                        incoming_ch12_data = mcu1_command["ch12_data"]
                                    # --------------------------------
                                    
                                    incoming_ch11_data = mcu1_command["ch11_data"]
                                    incoming_ch10_data = mcu1_command["ch10_data"]
                                    incoming_ch9_data = mcu1_command["ch9_data"]
                                    incoming_ch6_data = mcu1_command["ch6_data"]
                                    incoming_ch14_data = mcu1_command["ch14_data"]
                                    incoming_ch13_data = mcu1_command["ch13_data"]
                                    # incoming_ch12_data = mcu1_command["ch12_data"]
                                    incoming_ch11_data = mcu1_command["ch11_data"]
                                    incoming_ch10_data = mcu1_command["ch10_data"]
                                    incoming_ch9_data = mcu1_command["ch9_data"]
                                    incoming_ch6_data = mcu1_command["ch6_data"]
                                    global ch14_data, ch13_data, ch12_data, ch11_data, ch10_data, ch9_data, ch6_data
                                    with shared_state.data_lock:
                                        ch14_data = incoming_ch14_data
                                        ch13_data = incoming_ch13_data
                                        ch12_data = incoming_ch12_data
                                        ch11_data = incoming_ch11_data
                                        ch10_data = incoming_ch10_data
                                        ch9_data = incoming_ch9_data
                                        ch6_data = incoming_ch6_data
                        else:
                            if MCU0_count > 100:
                                with shared_state.data_lock:
                                    shared_state.MCU0_alive = False
                                # print("MCU0 is dead !! ", MCU0_count)                
                        # --- Check for incoming command to control MCU0 (Source: From_MCU1) ---
                        # FIX: Check if "From_MCU1" exists before accessing it
                        if "From_MCU1" in data and "To_MCU0" in data["From_MCU1"]:
                            mcu0_command = data["From_MCU1"]["To_MCU0"]
                            if MCU1_count < 100: 
                                with shared_state.data_lock:
                                    shared_state.MCU1_alive = True
                                # print("MCU1 is alive !! ", MCU1_count)
                            MCU1_count = 0

                            if isinstance(mcu0_command, dict):
                                if "encImplWheelVal" in mcu0_command:
                                    incoming_encImplWheelVal = mcu0_command["encImplWheelVal"]
                                    # print("incoming_encImplWheelVal",incoming_encImplWheelVal)
                                if "encHorizActVal" in mcu0_command:
                                    incoming_encHorizActVal = mcu0_command["encHorizActVal"]
                                    # print("incoming_encHorizActVal",incoming_encHorizActVal)
                                if "encDrawbarActVal" in mcu0_command:
                                    incoming_encDrawbarActVal = mcu0_command["encDrawbarActVal"]
                                    # print("incoming_encDrawbarActVal",incoming_encDrawbarActVal)
                                if "illuminate_orange_LED" in mcu0_command:
                                    incoming_state_str = str(mcu0_command["illuminate_orange_LED"]).lower()
                                    global should_illuminate_orange_mcu0
                                    
                                    with shared_state.data_lock:
                                        shared_state.encHorizActVal = incoming_encHorizActVal
                                        shared_state.encImplWheelVal = incoming_encImplWheelVal
                                        shared_state.encDrawbarActVal = incoming_encDrawbarActVal
                                        if incoming_state_str == "true":
                                            should_illuminate_orange_mcu0 = True
                                            # print(f"[{label}] >>> RECEIVED CMD: Setting shared MCU0 Orange LED state to TRUE.")
                                        elif incoming_state_str == "false":
                                            should_illuminate_orange_mcu0 = False
                                            # print(f"[{label}] >>> RECEIVED CMD: Setting shared MCU0 Orange LED state to FALSE.")
                        else:
                            if MCU1_count > 100:
                                with shared_state.data_lock:
                                    shared_state.MCU1_alive = False
                                # print("MCU1 is dead !! ", MCU1_count)

                        # --- Check for incoming command to control NANO (Source: From_MCU0) ---
                        # --- Check for incoming command to control NANO (Source: From_MCU0) ---
                        if "From_MCU0" in data and isinstance(data["From_MCU0"], dict):
                            if "To_NANO" in data["From_MCU0"] and isinstance(data["From_MCU0"]["To_NANO"], dict):
                                try:
                                    mcu0_command = data["From_MCU0"]["To_NANO"]

                                    if "act_lat" in mcu0_command:
                                        # Cast to float instead of str().lower()
                                        incoming_act_lat = float(mcu0_command["act_lat"])
                                        incoming_act_lon = float(mcu0_command["act_lon"])
            
                                        # Keep as string if it's not meant to be formatted as a float in the GUI
                                        incoming_act_steer_angle = str(mcu0_command["act_steer_angle"]).lower() 
                                        incoming_act_throtA_val = str(mcu0_command["act_throtA_val"]).lower()
                                        incoming_act_throtB_val = str(mcu0_command["act_throtB_val"]).lower()
            
                                        incoming_act_heading = float(mcu0_command["act_heading"])
                                        incoming_gps_speed = float(mcu0_command["GPSspeed_calc"]) # Matched to GUI var
            
                                        incoming_encoderSteerVal = str(mcu0_command["encoderSteerVal"]).lower()
                                        incoming_Nano_Shutdown = str(mcu0_command["Nano_Shutdown"]).lower()
            
                                        incoming_accuracy_MM = int(mcu0_command["accuracy_MM"])
                                        incoming_rel_pos_acc = float(mcu0_command["relPosAcc"])
                                        incoming_carrierSolutionType = mcu0_command["carrierSolutionType"]

                                    # Make sure globals match the names declared at the top of the script
                                    global act_steer_angle, encoderSteerVal, Nano_Shutdown
            
                                    with shared_state.data_lock:
                                        shared_state.act_lat = incoming_act_lat
                                        shared_state.act_lon = incoming_act_lon
                                        act_steer_angle = incoming_act_steer_angle
                                        shared_state.act_throtA_val = incoming_act_throtA_val
                                        shared_state.act_throtB_val = incoming_act_throtB_val
                                        shared_state.act_heading = incoming_act_heading
                                        shared_state.gps_speed = incoming_gps_speed       # Updated
                                        encoderSteerVal = incoming_encoderSteerVal
                                        Nano_Shutdown = incoming_Nano_Shutdown
                                        shared_state.accuracyMM = incoming_accuracy_MM   # Updated
                                        shared_state.rel_pos_acc = incoming_rel_pos_acc * 1000
                                        shared_state.carrierSolutionType = incoming_carrierSolutionType
                                        
                                except:
                                    print("\033[91mError in getting data from MCU0 !!!!\033[0m") # Red

                        # Optional Data Extraction Prints
                        if not PRINT_JSON_ONLY:
                            if "From_MCU0" in data and "To_MCU1" in data["From_MCU0"] and not PRINT_MCU_SERIAL_ONLY:
                                print(f"[{label}] Extracted Sensor Value (From_MCU0): {data['From_MCU0']['To_MCU1'].get('sensor', 'N/A')}")
                                print(f"[{label}] Extracted ch14_data Value (From_MCU0): {data['From_MCU0']['To_MCU1'].get('ch14_data', 'N/A')}")
                            if "From_MCU1" in data and "To_MCU0" in data["From_MCU1"] and not PRINT_MCU_SERIAL_ONLY:
                                print(f"[{label}] Extracted Sensor Value (From_MCU1): {data['From_MCU1']['To_MCU0'].get('sensor', 'N/A')}")
                            if "From_MCU0" in data and "To_NANO" in data["From_MCU0"] and not PRINT_MCU_SERIAL_ONLY:
                                print(f"[{label}] Extracted Nano_Shutdown Value (From_MCU0): {data['From_MCU0']['To_NANO'].get('Nano_Shutdown', 'N/A')}")
                            if "From_MCU0" in data and "To_NANO" in data["From_MCU0"] and not PRINT_MCU_SERIAL_ONLY:
                                print(f"[{label}] Extracted act_heading Value (From_MCU0): {shared_state.act_heading}")
                            if "From_MCU0" in data and "To_NANO" in data["From_MCU0"] and not PRINT_MCU_SERIAL_ONLY:
                                print(f"[{label}] Extracted relPosAcc Value (From_MCU0): {shared_state.rel_pos_acc}")
                            if "From_MCU0" in data and "To_NANO" in data["From_MCU0"] and not PRINT_MCU_SERIAL_ONLY:
                                print(f"[{label}] Extracted carrierSolutionType Value (From_MCU0): {shared_state.carrierSolutionType}")
                            if "From_MCU0" in data and "To_NANO" in data["From_MCU0"] and not PRINT_MCU_SERIAL_ONLY:
                                try:
                                    print(f"distance_to_go: {shared_state.distance_to_go}")
                                except:
                                    print(f"distance_to_go related error !!!")
                            
                    else:
                        if not PRINT_JSON_ONLY:
                            print(f"[{label}] --> VALID JSON PRIMITIVE DETECTED, SKIPPING <--")

                except json.JSONDecodeError:
                    is_noise = False
                    if PRINT_JSON_ONLY:
                        if line in ('{', '}', '[', ']', ',', ':') or not line:
                            is_noise = True

                    if not PRINT_JSON_ONLY and not is_noise:
                        print(f"[{label}] --> Non-JSON message, ignoring...")
                        
                    if PRINT_MCU_SERIAL_ONLY:
                        print(f"\n[{label}] RAW MCU SERIAL RECEIVE: {line}")

            time.sleep(0.001)
            

    except KeyboardInterrupt:
        print(f"\n[{port_labels.get(port_name, port_name)}] Exiting thread...")
    except Exception as e:
        print(f"[{port_labels.get(port_name, port_name)}] Line 834, An unexpected error occurred in def read_and_parse_serial(): {e}")
    finally:
        # Case where 'try:' fails:
        with shared_state.data_lock:
            shared_state.MCU0_alive = False
            shared_state.MCU1_alive = False
        print("Both MCU0 and MCU1 connections are dead !!")

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
#################################################################################################################
def database_update_thread():
    """
    This function uploads sensor data to a database via an asynchronous HTTP request.
    This thread manages its own asyncio event loop for the async HTTP calls.
    """
    # global current_lat
    # global current_lon
    # global current_acthead
    # global current_GPSFixTime
    # global current_carrierSolutionType
    # global current_myRelPosAcc
    # global aliveFlag1
    # global mySpeed

    global current_GPSFixTime
    global shutDown_value
    global throttAVal
    global aliveFlag2

    thread_update_time = 5 # seconds
    
    # current_waypoints = []
    # shared_state.waypointsArray = []

    prev_waypoint_epoch_time = 0

    print("database_update_thread started .............................................")

    # current_lat = 53.302801158199024
    # current_lon = -4.240779625855205

    while(1):
        try:
            # Acquire lock before accessing/modifying shared global variables
            with shared_state.data_lock:

                # Prepare data for upload using the current (locked) global values
                lat_to_upload = shared_state.act_lat
                lon_to_upload = shared_state.act_lon
                acthead_to_upload = shared_state.act_heading
                GPSFixTime_to_upload = current_GPSFixTime
                carrierSolutionType_to_upload = shared_state.carrierSolutionType
                current_myRelPosAcc_to_upload = shared_state.rel_pos_acc
                mySpeed_to_upload = shared_state.gps_speed
                act_throtA_val_to_upload = shared_state.act_throtA_val

            weedinator_data = {
                "act_lat": lat_to_upload,
                "act_lon": lon_to_upload,
                "act_steer_angle": 15.5,
                "act_throtA_val": act_throtA_val_to_upload,
                "act_heading": acthead_to_upload,
                "mySpeed": mySpeed_to_upload,
                "GPSspeed_calc": mySpeed_to_upload,
                "encoderSteerVal": 1024,
                "GSM_session_num": 999,
                "carrierSolutionType": carrierSolutionType_to_upload,
                "GPSFixTime": GPSFixTime_to_upload,
                "myRelPosAcc": current_myRelPosAcc_to_upload ,
            }

            # print(weedinator_data)
            # print("mySpeed_to_upload: ",mySpeed_to_upload)
            if shared_state.send_data_state:
                print("Data sent to the weedinator database !!!")
                send_data_to_weedinator(**weedinator_data)  # sends data to the weedinator database eg gps, actual heading.

            # The Mapping app uses a temporary table called 'control_room' which gets copied to 'des_coords' when all editing of waypoints is completed.
            last_waypoint_epoch_time = None
            try:
                last_waypoint_epoch_time = retreive_data_from_des_coords_table() # retrieve the latest wapoint epoch time value.
            except:
                pass

            with shared_state.data_lock:
                if last_waypoint_epoch_time != None:
                    aliveFlag1 = True
                else:
                    aliveFlag1 = False

            # print("waypoints database latest epoch_time value: ",last_waypoint_epoch_time)
            
            '''
            read_database_thread checks the epoch time and downloads waypoints every 60 seconds.
            database_update_thread also checks the epoch time and downloads waypoints every 5 seconds.
            '''

            if last_waypoint_epoch_time > prev_waypoint_epoch_time:
                print("\033[93mDetected an increase in waypoint epoch time !!\033[0m") # Yellow
                print("Now download all the waypoints from des_coords table .....")
                prev_waypoint_epoch_time = last_waypoint_epoch_time
                with shared_state.data_lock:
                    shared_state.waypointsArray = download_waypoints()
                    # print("waypointsArray from des_coords table: ",shared_state.waypointsArray)
        except Exception as e:
            pass

        time.sleep(thread_update_time)

##################################################################################################################
def send_data_to_weedinator(
    act_lat, act_lon, act_steer_angle, act_throtA_val, act_heading,
    mySpeed, GPSspeed_calc, encoderSteerVal, GSM_session_num,
    carrierSolutionType, GPSFixTime, myRelPosAcc
):
    url_send = "http://www.################/database/send.php"
    headers = {"X-API-Password": passwords.get_password()}

    payload = {
        "act_lat": shared_state.act_lat,
        "act_lon": shared_state.act_lon,
        "act_steer_angle": act_steer_angle,
        "act_throtA_val": shared_state.act_throtA_val,
        "act_heading": shared_state.act_heading,
        "mySpeed": mySpeed,
        "GPSspeed_calc": GPSspeed_calc,
        "encoderSteerVal": encoderSteerVal,
        "GSM_session_num": GSM_session_num,
        "carrierSolutionType": shared_state.carrierSolutionType,
        "GPSFixTime": GPSFixTime,
        "myRelPosAcc": myRelPosAcc,
    }

    '''
    try:
        # Switch to HTTP POST for mutating state and protecting telemetry
        print("Try to send location to weedinator database .....")
        response_send = requests.post(url_send, data=payload, headers=headers)
        print("response_send: ",response_send)
        response_send.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"\033[91mAn error occurred: {e}\033[0m")
    '''
  
    try:
        print("Try to send location to weedinator database .....")
        response_send = requests.post(url_send, data=payload, headers=headers)
        print("response_send: ",response_send)
        
        # NEW: If the server returns an error, print the exact message from PHP!
        if response_send.status_code != 200:
            print(f"\033[93mPHP Server says: {response_send.text}\033[0m")
            
        response_send.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"\033[91mAn error occurred: {e}\033[0m")

###########################################################################################################
def main():
    threads = []
    
    detected_ports = autodetect_serial_ports()
    
    if not detected_ports:
        print("Exiting script because no serial ports were found.")
        sys.exit(1)

    for port in detected_ports:
        thread = threading.Thread(target=read_and_parse_serial, args=(port,))
        threads.append(thread)
        thread.start()
        
    sender_thread = threading.Thread(target=send_command_thread)
    threads.append(sender_thread)
    sender_thread.start()
    
    database_thread_read = threading.Thread(target=read_database_thread)
    threads.append(database_thread_read)
    database_thread_read.start()
    
    waypoints_manager_thread = threading.Thread(target=manage_waypoints_thread)
    threads.append(waypoints_manager_thread)
    waypoints_manager_thread.start()
    
    update_database_thread = threading.Thread(target=database_update_thread)
    threads.append(update_database_thread)
    update_database_thread.start()
    
    update_camera_frame_thread = threading.Thread(target=update_camera_frame)
    threads.append(update_camera_frame_thread)
    update_camera_frame_thread.start()
    
    gui_thread()
    
    try:
        while any(t.is_alive() for t in threads):
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nMain thread received interrupt. Shutting down...")
    except Exception as e:
        print(f"An unexpected error occurred in main loop: {e}")

if __name__ == "__main__":
    main()
