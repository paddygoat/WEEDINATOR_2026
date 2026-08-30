# shared_state.py

import threading
from collections import deque
import time

# --- App Start Time Tracking ---
start_time = time.time()  # <--- Stores the application baseline start time

LIGHT_BULB_FLASH_DELTA_ARRAY = []  # Is this necessary?

# --- Graph Tracking Metrics (Max 5000 points) ---
MAX_GRAPH_POINTS = 5000
# These will store tuples in the format: (epoch_timestamp, time_delta)
graph_green_filtered = deque(maxlen=MAX_GRAPH_POINTS)
graph_yolo_filtered = deque(maxlen=MAX_GRAPH_POINTS)
graph_averaged = deque(maxlen=MAX_GRAPH_POINTS)
graph_predicted = deque(maxlen=MAX_GRAPH_POINTS)
graph_light_bulb_flash = deque(maxlen=MAX_GRAPH_POINTS)
graph_gps_speed = deque(maxlen=MAX_GRAPH_POINTS)

# GREEN_TIME_DELTA_ARRAY, GREEN_TIME_DELTA_ARRAY_FILTERED, YOLO_TIME_DELTA_ARRAY, YOLO_TIME_DELTA_ARRAY_FILTERED, AVERAGED_TIME_DELTA_ARRAY, PREDICTED_TIME_DELTA_ARRAY

# --- The Lock ---
data_lock = threading.Lock()

# --- Connection Tracking ---
MCU0_alive = False
MCU1_alive = False

# --- Telemetry Data ---
act_lat = 0.0
act_lon = 0.0
des_lat = 53.302801158199024
des_lon = -4.240779625855205
distance_to_go = 0.0
waypointsArray = []
current_waypoint_index = 0
act_heading = 0.0
gps_speed = 0.0
accuracyMM = 0
rel_pos_acc = 0.0
carrierSolutionType = "N/A"
act_throtA_val = 999
act_throtB_val = 999

encImplWheelVal = 0
encHorizActVal = 0
encDrawbarActVal = 0

# --- Settings ---
USE_CAMERA = True  # True = Live Camera, False = Video File
X_AXIS_ADJUST = 0
slider_1_val = 999
slider_2_val = 999
camera_saturation = 15
camera_exposure_gain = 15
confidence_threshold = 0.10
coalesce_distance_threshold = 50
camera_exposure_time = 1000
camera_brightness = -3
camera_contrast = -30
camera_sharpness = 20
camera_wb_temp = 5000
tunnel_vision = 200
hue_green_lower = 0.194
hue_green_upper = 0.511
camera_gamma = 10
camera_denoise = 0
camera_backlight_comp = 0
camera_flick_mode = 0        # 0: Off, 1: 50Hz, 2: 60Hz, 3: Auto

auto_coalesce_enabled = False
auto_confidence_enabled = False
auto_cam_gain_enabled = False
screen_record_enabled = False
raw_screen_record_enabled = False
auto_weed_enabled = False

OPTIMISE_EXP_TIME_BY_COLOUR = False

auto_camera_settings_enabled = False

expected_seedlings_target = 4

avg_detection_confidence = 0.0

latest_frame = None  # This will hold the processed image

send_data_state = False

# ADD THIS LINE TO TRACK THE YELLOW FLASH EVENT:
yellow_flash_event = False

# ADD THIS LINE TO TRACK EXPECTED TIME DELTA:
expected_time_delta_val = 8.0

# TRACK VISION LOOP TIME:
vision_loop_time = 0.0

# Array to store loop speed data (timestamp, duration) ---
loop_speed_array = deque(maxlen=MAX_GRAPH_POINTS)
data_for_analysis = deque(maxlen=MAX_GRAPH_POINTS)

ch12_data = 992 # horizontal hydraulic actuator

camera_start = False





