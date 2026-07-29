# weedinator_vision.py
# Camera is TechNexion TEVS-AR0234 (/dev/video0), onsemi AR0234 (2.3 Megapixel, 1920 \times 1200) CMOS image sensor, global shutter.

# --- CRITICAL JETSON FIX: IMPORT TENSORRT FIRST ---
import tensorrt
# --------------------------------------------------

import cv2
import os
import time
import itertools
from PIL import Image, ImageTk
from ultralytics import YOLO
import shared_state
import logging
import pyvizionsdk as vz
import torchvision.transforms as T
from typing import Tuple, List, Dict
import numpy as np
import math
import json
import os
import inspect

expected_time_delta = 8.9 # This variable can be adjusted by both the camera detections and the encoder on the implement wheel, with appropriate weighting.
DEBOUNCE_TIME = expected_time_delta/5

RECORD_GRAPH_DATA = True

# Disable Ultralytics logging globally
# logging.getLogger("ultralytics").setLevel(logging.ERROR)

# Define the minimum area threshold:
MIN_CENTROID_AREA = 500

# --- Camera vs Video Configuration ---
path_simulate = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/simulate_status.txt"
USE_CAMERA = True # Default fallback

if os.path.exists(path_simulate):
    try:
        with open(path_simulate, "r") as f:
            USE_CAMERA = (f.read().strip() == "True")
    except Exception as e:
        print(f"[Vision Startup] Error reading simulate_status.txt: {e}. Defaulting to Camera.")

print(f"[Vision Startup] Configured via file status. USE_CAMERA = {USE_CAMERA}")
# video_path = "/home/nano/Videos/bus_cards_03_reversed.webm"
video_path = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/recordings/weedinator_RAW_20260726-190140.mp4"
# video_path = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/recordings/simulation_01.webm"

# --- Auto-Coalesce Configuration ---
EXPECTED_SEEDLINGS_IN_FRAME = 4  # Target number of seedling groups

# --- Color Masking Bounds (Normalized 0.0 to 1.0) ---
# Hue (Color): The OpenCV range 0-180 is normalized to [0.0, 1.0].
# Use /home/nano/Documents/yolo_stuff && python3 lower_and_upper_hue_generator_01.py to adjust vales.
# HUE_GREEN_LOWER = 0.194
# HUE_GREEN_UPPER = 0.511

# Saturation (Purity/Intensity)
SATURATION_MIN = 25 / 255.0
# SATURATION_MIN = 15 / 255.0
SATURATION_MAX = 1.0

# Value (Brightness)
BRIGHT_VAL_MIN = 75 / 255.0
# BRIGHT_VAL_MIN = 7 / 255.0
BRIGHT_VAL_MAX = 1.0

DESKTOP_DISPLAY = True
TIME_CALCS = True
ANIMATED_PLOT = True

DISPLAY_WIDTH = 800 # GUI display
DISPLAY_HEIGHT = 480

DISPLAY_WIDTH = 960 # GUI display
DISPLAY_HEIGHT = 600

DISPLAY_WIDTH = 1048 # GUI display
DISPLAY_HEIGHT = 656

CAMERA_FRAME_RATE = 10
CAMERA_SOURCE = 0
CONFIDENCE_THRESHOLD = 0.10

# Must be an odd number (e.g., 3, 5, 7, 9...)
BLUR_KERNEL_SIZE = (5,5)   # CPU

BLUR_SIGMA = 5.0      # Controls the intensity of the blur
BLUR_ITERATIONS = 1   # Number of times to apply the blur transform

# Distance threshold (in pixels) for merging nearby centroids
# COALESCE_DISTANCE_THRESHOLD = 300

# Define the minimum area threshold:
MIN_CENTROID_AREA = 500


# Set to 300 pixels as a starting point.
LINE_LEN_MAX = 600

# --- Tunnel Vision Configuration ---
TUNNEL_VISION = 200

# --- Angle Check Configuration ---
# The tolerance for checking alignment. Lines must be within this many 
# degrees of 0 (horizontal), 90 (vertical), or 180 (horizontal).
ANGLE_TOLERANCE_DEG = 20

# BGR color for the connecting line between green centers (Green)
LINE_COLOR = (0, 255, 0)
LINE_THICKNESS = 2

# --- YOLO Box Alignment Check Configuration (New) ---
# BGR color for the connecting line between YOLO boxes (Blue)
YOLO_LINE_COLOR = (255, 0, 0)
YOLO_LINE_THICKNESS = 2

# --- Quadrilateral Check Configuration ---
# Max pixel difference allowed for centers to be considered on the same X or Y axis.
# This relaxes the 'axis-aligned' check from exact match to proximity.
AXIS_PROXIMITY_TOLERANCE = 150 # Pixels

AUTO_LEVEL_ADJUST_FLAG = False

# --- Device Setup ---
# Check if CUDA (NVIDIA GPU acceleration) is available
# DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print(f"PyTorch will use the following device for tensor operations: {DEVICE}")

mid_y = 0
mid_x = 0
width = 0
height = 0

adjust_time = 0.05
# absolute fastest stable speed without dropping camera commands, use 0.005


# --- GLOBAL TENSORRT INITIALIZATION ---
MODEL_NAME = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/Models/business_cards_02.engine"
print("\n[Vision Setup] Loading raw TensorRT engine into main thread...")

# CRITICAL: Tell Ultralytics this is a 'detect' task since trtexec engines have no metadata headers
model = YOLO(MODEL_NAME, task="detect")

print("[Vision Setup] Running GPU warmup with native 640x640 frame...")
dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)

# Explicitly pass device=0 as an integer to force clean CUDA allocation
model.predict(source=dummy_frame, device=0, verbose=True)
print("[Vision Setup] Warmup complete.\n")

# Get class names for printing labels globally
class_names: Dict[int, str] = model.names
allowed_classes = [id for id in class_names.keys() if id != 13]
# --------------------------------------

def normalize_angle(angle_deg: float) -> float:
    """Normalize angle to the range [0, 180] degrees for line orientation."""
    # Convert angle from [-180, 180] to [0, 360]
    angle_deg = (angle_deg + 360) % 360
    # Normalize angle to [0, 180] (as 180-360 is the same line orientation)
    if angle_deg > 180:
        angle_deg -= 180
    return angle_deg

def calculate_angle_between_centers(center1: Tuple[int, int], center2: Tuple[int, int]) -> float:
    """Calculate the normalized angle (0-180 degrees) between two points."""
    x1, y1 = center1
    x2, y2 = center2
    
    dx = x2 - x1
    dy = y2 - y1
    
    # Calculate angle in radians, then convert to degrees
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)
    
    return normalize_angle(angle_deg)

def calculate_distance(center1: Tuple[int, int], center2: Tuple[int, int]) -> float:
    """Calculate the Euclidean distance between two points."""
    x1, y1 = center1
    x2, y2 = center2
    distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return distance

def append_smoothed_crossing(filtered_array: list, current_timestamp: float, current_delta: float, expected_delta: float):
    """
    Interpolates missed crossings and appends smoothed time deltas.
    """
    # 1. Retrieve the caller's actual variable name for 'filtered_array'
    caller_frame = inspect.currentframe().f_back
    var_name = next(
        (name for name, val in caller_frame.f_locals.items() if val is filtered_array),
        "filtered_array"  # Fallback if unassigned (e.g., passed as literal)
    )

    # 2. Check thresholds and handle smoothing
    if current_delta < expected_delta * 1.6:
        # Normal delta: No missing data detected here
        filtered_array.append((current_timestamp, round(current_delta, 2)))
    elif current_delta < expected_delta * 2.5:
        print(f"Missing {var_name} data detected !! Division by 2 effected.")
        filtered_array.append((current_timestamp, round(current_delta / 2.0, 2)))
    elif current_delta < expected_delta * 3.5:
        print(f"Missing {var_name} data detected !! Division by 3 effected.")
        filtered_array.append((current_timestamp, round(current_delta / 3.0, 2)))
    elif current_delta < expected_delta * 4.5:
        print(f"Missing {var_name} data detected !! Division by 4 effected.")
        filtered_array.append((current_timestamp, round(current_delta / 4.0, 2)))
    else:
        filtered_array.append((current_timestamp, round(current_delta, 2)))

def perform_cv2_blur_and_mask(input_image_pil: Image.Image, hue_lower: float, hue_upper: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Performs CPU-accelerated Blur and Green Color Masking using OpenCV.

    Args:
        input_image_pil (Image.Image): The input image in PIL format (RGB).

    Returns:
        Tuple[np.ndarray, np.ndarray]:
        1. masked_image: The blurred and masked image as a NumPy array (BGR).
        2. mask: The binary mask as a NumPy array (0s and 255s).
    """
    
    # 1. Convert PIL Image to OpenCV format (NumPy array)
    # PIL Image is RGB, convert it to NumPy array
    image_np_rgb = np.array(input_image_pil)
    # OpenCV uses BGR, so convert RGB to BGR
    image_bgr = cv2.cvtColor(image_np_rgb, cv2.COLOR_RGB2BGR)

    # 2. Apply iterative Gaussian Blur
    blurred_image = image_bgr
    for _ in range(BLUR_ITERATIONS):
        blurred_image = cv2.GaussianBlur(
            blurred_image,
            ksize=BLUR_KERNEL_SIZE,
            sigmaX=BLUR_SIGMA
        )

    # 3. Perform Green Color Masking
    hsv_image = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2HSV)

    # Use the dynamic variables passed into the function
    lower_green = np.array([
        hue_lower * 179, 
        SATURATION_MIN * 255, 
        BRIGHT_VAL_MIN * 255
    ])
    upper_green = np.array([
        hue_upper * 179, 
        SATURATION_MAX * 255, 
        BRIGHT_VAL_MAX * 255
    ])
    
    mask = cv2.inRange(hsv_image, lower_green, upper_green)
    masked_image = cv2.bitwise_and(blurred_image, blurred_image, mask=mask)
    
    return masked_image, mask

def adjust_camera_settings():
    # 1. Scan for connected TechNexion GMSL2/CSI cameras
    result, camera_list = vz.VxDiscoverCameraDevices()
    
    if len(camera_list) == 0:
        print("Error: No TechNexion cameras detected.")
        return
        
    print(f"Detected {len(camera_list)} TechNexion device(s):")
    for cam in camera_list:
        print(f" - {cam}")
    
    # 2. Initialize and open the camera device handle at index 0
    camera = vz.VxInitialCameraDevice(0)
    open_status = vz.VxOpen(camera)
    
    if open_status != 0: 
        print(f"Error: Failed to open camera connection. Code: {open_status}")
        return
        
    _, name = vz.VxGetDeviceName(camera)
    print(f"Connected to: {name}")
    
    '''
    --- Saturation Property Metrics: Range: [0 to 50]
    --- Contrast Property Metrics: Range: [-50 to 50]
    --- Brightness Property Metrics: Range: [-10 to 10]
    --- Sharpness Property Metrics: Range: [-20 to 20]
    --- Exposure Time Property Metrics: Range: [1 to 1000000] 
    --- Exposure Gain Property Metrics: Range: [0 to 255] |
    '''

    try:
        # 3. Setup property identifiers safely (with fallbacks for older/newer SDK structures)
        try:
            contrast_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_CONTRAST
            brightness_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_BRIGHTNESS
            saturation_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_SATURATION
            sharpness_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_SHARPNESS
            exp_mode_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_EXPOSURE_MODE
            exp_time_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_EXPOSURE_TIME
            exp_gain_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_EXPOSURE_GAIN
            wb_mode_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_WHITEBALANCE_MODE
            wb_temp_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_WHITEBALANCE_TEMPERATURE
            gamma_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_GAMMA
            denoise_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_DENOISE
            backlight_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_BACKLIGHT_COMPENSATION
            flick_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_FLICK_MODE
        except AttributeError:
            # Fallback configuration if your specific wheel maps properties to the root namespace
            contrast_prop = vz.ISP_IMAGE_CONTRAST
            brightness_prop = vz.ISP_IMAGE_BRIGHTNESS
            saturation_prop = vz.ISP_IMAGE_SATURATION
            sharpness_prop = vz.ISP_IMAGE_SHARPNESS
            exp_mode_prop = vz.ISP_IMAGE_EXPOSURE_MODE
            exp_time_prop = vz.ISP_IMAGE_EXPOSURE_TIME
            exp_gain_prop = vz.ISP_IMAGE_EXPOSURE_GAIN
            wb_mode_prop = vz.ISP_IMAGE_WHITEBALANCE_MODE
            wb_temp_prop = vz.ISP_IMAGE_WHITEBALANCE_TEMPERATURE
            gamma_prop = vz.ISP_IMAGE_GAMMA
            denoise_prop = vz.ISP_IMAGE_DENOISE
            backlight_prop = vz.ISP_IMAGE_BACKLIGHT_COMPENSATION
            flick_prop = vz.ISP_IMAGE_FLICK_MODE

        # 4. Define target settings
        target_contrast = -30
        target_brightness = -3
        target_saturation = 15
        target_sharpness = 20
        target_flick = 0
        DISABLE_AUTO = 0 
        
        target_exposure_time = 1000  # Adjust baseline shutter speed index
        target_exposure_gain = 15    # Adjust baseline sensor gain matrix
        target_wb_temperature = 5000  # Adjust color balance (Kelvin index)
        
        target_gamma = 10
        target_denoise = 5
        target_backlight = 0

        # 5. Apply basic image quality controls
        vz.VxSetISPImageProcessing(camera, contrast_prop, target_contrast)
        time.sleep(adjust_time)
        vz.VxSetISPImageProcessing(camera, brightness_prop, target_brightness)
        time.sleep(adjust_time)
        vz.VxSetISPImageProcessing(camera, saturation_prop, target_saturation)
        time.sleep(adjust_time)
        vz.VxSetISPImageProcessing(camera, sharpness_prop, target_sharpness)
        time.sleep(adjust_time)
        vz.VxSetISPImageProcessing(camera, gamma_prop, target_gamma)
        time.sleep(adjust_time)
        vz.VxSetISPImageProcessing(camera, denoise_prop, target_denoise)
        time.sleep(adjust_time)
        vz.VxSetISPImageProcessing(camera, backlight_prop, target_backlight)
        time.sleep(adjust_time)
        vz.VxSetISPImageProcessing(camera, flick_prop, target_flick)
        time.sleep(adjust_time)

        print("\n--- Applying Lockout Constraints ---")

        # 6. TURN OFF AUTO-EXPOSURE (Switch to Manual Mode)
        print("Disabling Auto-Exposure (Locking to Manual)...")
        ae_status = vz.VxSetISPImageProcessing(camera, exp_mode_prop, DISABLE_AUTO)
        time.sleep(adjust_time)
        if ae_status == 0:
            print(" -> Auto-Exposure successfully disabled.")
            vz.VxSetISPImageProcessing(camera, exp_time_prop, target_exposure_time)
            time.sleep(adjust_time)
            vz.VxSetISPImageProcessing(camera, exp_gain_prop, target_exposure_gain)
            time.sleep(adjust_time)
            print(f" -> Static exposure locked (Time: {target_exposure_time}, Gain: {target_exposure_gain})")
        else:
            print(f" -> Failed to turn off Auto-Exposure. Code: {ae_status}")

        # 7. DISABLE AUTO WHITE BALANCE (Switch to Manual Mode)
        print("Disabling Auto White Balance (Locking Color Matrix)...")
        awb_status = vz.VxSetISPImageProcessing(camera, wb_mode_prop, DISABLE_AUTO)
        time.sleep(adjust_time)
        if awb_status == 0:
            print(" -> Auto White Balance successfully disabled.")
            vz.VxSetISPImageProcessing(camera, wb_temp_prop, target_wb_temperature)
            time.sleep(adjust_time)
            print(f" -> Static color balance locked at: {target_wb_temperature}K")
        else:
            print(f" -> Failed to turn off Auto White Balance. Code: {awb_status}")
            
        print("------------------------------------\n")

    except Exception as e:
        print(f"An error occurred during runtime control execution: {e}")
        
    finally:
        # Returns the camera handle up to the parent application frame-loop
        return camera

def update_camera_frame():
    global expected_time_delta

    width = 0
    height = 0
    
    # is_currently_below_green = None

    # YOLO Model path
    print("Load a YOLO model ....")
    


    #TODO Use os.path.expanduser("~") to dynamically get the home directory:
    # MODEL_NAME = "/home/nano/Documents/yolo_stuff/yolo11n.pt"
    # MODEL_NAME = "/home/nano/Documents/yolo_stuff/training_stuff/data/models/yolo26n_seedlings_and_onions_ready_to_deploy.pt"
    # MODEL_NAME = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/Models/business_cards_02.engine"
    
    # Load a pretrained YOLO model
    # print("Load a model ....")
    # model = YOLO(MODEL_NAME)
    
    # Get class names for printing labels
    class_names: Dict[int, str] = model.names
    # --- ADD THIS LINE TO PRINT THE CLASSES ---
    # print(f"Loaded YOLO classes: {class_names}")

    # Get class names for printing labels
    class_names: Dict[int, str] = model.names
    
    # --- ADD THIS LINE TO FILTER OUT CLASS 13 (slugs) ---
    allowed_classes = [id for id in class_names.keys() if id != 13]
    
    camera_handle = None

    if USE_CAMERA:
        print(f"Initializing camera device {CAMERA_SOURCE} at 1920x1200...")
        cap = cv2.VideoCapture(CAMERA_SOURCE)
        if not cap.isOpened():
            print("[ERROR] OpenCV could not open the GStreamer pipeline! Aborting.")
            import sys
            sys.exit(1) # Stop the script here instead of hanging
        
        # Force the hardware resolution constraints directly on the stream
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
        cap.set(cv2.CAP_PROP_FPS, CAMERA_FRAME_RATE)
        
        # --- Run Live Inference ---
        print(f"Starting live object detection on camera source: {CAMERA_SOURCE}")
        camera_handle = adjust_camera_settings()
        
        # [ KEEP YOUR EXISTING GSTREAMER PIPELINE CODE HERE ]
        gstreamer_pipeline = (
        "v4l2src device=/dev/video0 io-mode=2 ! "  
        "video/x-raw, format=UYVY, width=1920, height=1200, framerate=60/1 ! "  
        "nvvidconv ! video/x-raw(memory:NVMM) ! "  
        "nvvidconv ! video/x-raw, format=BGRx ! "  
        "videoconvert ! video/x-raw, format=BGR ! "  
        "appsink drop=true max-buffers=1 sync=false"  
        )  
        
        print(f"Opening camera stream via GStreamer: {gstreamer_pipeline}")
        cap = cv2.VideoCapture(gstreamer_pipeline, cv2.CAP_GSTREAMER)
        
        if not cap.isOpened():
            print("GStreamer pipeline initialization failed. Falling back to direct V4L2...")
            cap = cv2.VideoCapture(CAMERA_SOURCE, cv2.CAP_V4L2)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
    else:
        print(f"Initializing video stream from file: {video_path}")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"[ERROR] Could not open video file {video_path}! Aborting.")
            import sys
            sys.exit(1)
    
    try:
        saturation_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_SATURATION
        exp_gain_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_EXPOSURE_GAIN
        exp_time_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_EXPOSURE_TIME
        brightness_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_BRIGHTNESS
        exp_mode_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_EXPOSURE_MODE
        wb_mode_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_WHITEBALANCE_MODE
        contrast_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_CONTRAST
        sharpness_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_SHARPNESS
        wb_temp_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_WHITEBALANCE_TEMPERATURE
        gamma_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_GAMMA
        denoise_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_DENOISE
        backlight_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_BACKLIGHT_COMPENSATION
        flick_prop = vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_FLICK_MODE
    except AttributeError:
        saturation_prop = vz.ISP_IMAGE_SATURATION
        exp_gain_prop = vz.ISP_IMAGE_EXPOSURE_GAIN
        exp_time_prop = vz.ISP_IMAGE_EXPOSURE_TIME
        brightness_prop = vz.ISP_IMAGE_BRIGHTNESS
        exp_mode_prop = vz.ISP_IMAGE_EXPOSURE_MODE
        wb_mode_prop = vz.ISP_IMAGE_WHITEBALANCE_MODE
        contrast_prop = vz.ISP_IMAGE_CONTRAST
        sharpness_prop = vz.ISP_IMAGE_SHARPNESS
        wb_temp_prop = vz.ISP_IMAGE_WHITEBALANCE_TEMPERATURE
        gamma_prop = vz.ISP_IMAGE_GAMMA
        denoise_prop = vz.ISP_IMAGE_DENOISE
        backlight_prop = vz.ISP_IMAGE_BACKLIGHT_COMPENSATION
        flick_prop = vz.ISP_IMAGE_FLICK_MODE
    
    last_applied_saturation = 15
    last_applied_gain = 15
    last_applied_exp_time = 1000
    last_applied_brightness = -3
    last_applied_contrast = -30
    last_applied_sharpness = 20
    last_applied_wb_temp = 5000
    last_applied_conf = CONFIDENCE_THRESHOLD
    last_applied_coalesce = 50
    last_applied_auto_coalesce = False
    last_applied_auto_confidence = False
    last_applied_auto_cam_gain = False
    last_applied_screen_record = False
    last_applied_raw_screen_record = False
    last_applied_gamma = 10
    last_applied_denoise = 5
    last_applied_backlight = 0
    last_applied_flick = 0
    last_applied_optimise_exp = False
    last_applied_auto_cam_settings = False

    video_writer = None
    raw_video_writer = None
    
    # State variables for Auto-Gain Hill Climbing
    prev_avg_conf = 0.0
    gain_step_direction = 1  # 1 for increasing gain, -1 for decreasing gain

    # ------------------------------------------------------------------------
    # FORCE 1920x1200 HARDWARE RESOLUTION VIA OPTIMIZED GSTREAMER PIPELINE
    # ------------------------------------------------------------------------
    # NB Do not remove the following Gstreamer block, even though it appears to fail:
    '''
    gstreamer_pipeline = (
    "v4l2src device=/dev/video0 io-mode=2 ! "  # Open video0 using memory-mapped IO to bypass CPU data copying.
    "video/x-raw, format=UYVY, width=1920, height=1200, framerate=60/1 ! "  # Request the sensor's native resolution, UYVY format, and 60 FPS.
    "nvvidconv ! video/x-raw(memory:NVMM) ! "  # Upload frames into Nvidia NVMM memory for hardware-accelerated processing.
    "nvvidconv ! video/x-raw, format=BGRx ! "  # Convert UYVY to 32-bit aligned BGRx using Jetson's hardware engine.
    "videoconvert ! video/x-raw, format=BGR ! "  # Discard the extra alpha padding byte to output standard BGR for OpenCV.
    "appsink drop=true max-buffers=1 sync=false"  # Disable clock sync and drop old buffers to guarantee zero real-time lag.
    )  
    
    print(f"Opening camera stream via GStreamer: {gstreamer_pipeline}")
    cap = cv2.VideoCapture(gstreamer_pipeline, cv2.CAP_GSTREAMER)
    
    # Safety fallback if GStreamer fails to initialize on your specific OpenCV build
    if not cap.isOpened():
        print("GStreamer pipeline initialization failed. Falling back to direct V4L2...")
        cap = cv2.VideoCapture(CAMERA_SOURCE, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
    '''

    '''
    Ignore this error message:
    Opening camera stream via GStreamer: v4l2src device=/dev/video0 ! video/x-raw, width=1920, height=1200, framerate=10/1 ! videoconvert ! video/x-raw, format=BGR ! appsink drop=true
GStreamer pipeline initialization failed. Falling back to direct V4L2...
Camera stream initialized successfully. Starting manual frame processing loop...
    '''

    # Initialize flag and confidence threshold variables for the loop context
    has_printed_dimensions = False
    current_gui_conf = CONFIDENCE_THRESHOLD

    # print("Camera stream initialized successfully. Starting manual frame processing loop...")
    
    # Initialize the camera frame size one-off print flag before the loop begins
    has_printed_dimensions = False

    # Process frames manually to guarantee 1920x1200 resolution and prevent cold boot drops
    # --- Global State Variables for Crossing Detection ---
    LAST_POSITION_BELOW_GREEN = None
    LAST_CROSSING_EPOCH_TIME_GREEN = None
    current_epoch_time = 0.0

    GREEN_TIME_DELTA_ARRAY = []
    GREEN_TIME_DELTA_ARRAY_FILTERED = []
    YOLO_TIME_DELTA_ARRAY_FILTERED = []
    AVERAGED_TIME_DELTA_ARRAY = []
    LIGHT_BULB_FLASH_DELTA_ARRAY = []
    averageCalculated = False

    # --- Crossing Detection State Variables for YOLO ---
    LAST_POSITION_BELOW_YOLO = None
    LAST_CROSSING_EPOCH_TIME_YOLO = None
    YOLO_TIME_DELTA_ARRAY = []

    # --- Averaged Time Delta Arrays ---
    PREDICTED_TIME_DELTA_ARRAY = []
    first_missing = False
    second_missing = False
    third_missing = False
    fourth_missing = False
    fith_missing = False
    last_prediction_time = 0.0

    # --- Display Flags ---
    YELLOW_FLASH = False
    
    LAST_FLASH_EPOCH_TIME = None

    while True:
        ret, frame = cap.read()
        current_epoch_time = time.time()
        
        # Calculate relative time since application started
        current_rel_time = current_epoch_time - shared_state.start_time

        if not ret:
            if USE_CAMERA:
                print("Warning: Camera frame drop detected. Retrying frame grab...")
                time.sleep(0.1)
                continue
            else:
                print("End of video stream reached. Looping back to start...")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
        # print("Camera frame successfully grabbed! Running inference...")
            
        # Run YOLO inference directly on the grabbed frame array
        results = model.predict(
            source=frame,              # Pass the raw NumPy frame array directly
            conf=current_gui_conf,     # Dynamically applies your GUI slider value seamlessly
            device='0', 
            verbose=False, 
            classes=allowed_classes    # Suppresses class 13 (slugs) completely
        )
        
        # Extract the primary result object so the rest of your original script runs unchanged
        result = results[0]
        # ------------------------------------------------------------------------
    


        # Get the bounding box object
        boxes = result.boxes
        
        # --- TUNNEL VISION CALCULATIONS ---
        with shared_state.data_lock:
            current_tunnel_vision = shared_state.tunnel_vision
            
        # Scale the UI tunnel vision slider to the actual camera frame width
        frame_height, frame_width = result.orig_shape
        
        
        # ONE-OFF PRINT OF CAMERA FRAME SIZE
        if not has_printed_dimensions:
            print("\n" + "="*40)
            print(f"NATIVE CAMERA RESOLUTION DETECTED:")
            print(f"  Frame Width:  {frame_width} px")
            print(f"  Frame Height: {frame_height} px")
            print("="*40 + "\n")
            has_printed_dimensions = True  # Flips the flag so it never runs again

        scale_x = frame_width / DISPLAY_WIDTH
        actual_tunnel_left = int(current_tunnel_vision * scale_x)
        actual_tunnel_right = frame_width - actual_tunnel_left
        
        # --- FILTER YOLO BOXES BY TUNNEL VISION ---
        tunnel_boxes_conf = []
        for i in range(len(boxes)):
            coords = boxes.xyxy[i].cpu().numpy().astype(int).flatten()
            box_cx = (coords[0] + coords[2]) // 2 # Center X of the YOLO box
            if actual_tunnel_left < box_cx < actual_tunnel_right:
                tunnel_boxes_conf.append(boxes.conf[i].cpu().item())
                
        actual_detections_in_tunnel = len(tunnel_boxes_conf)
            
    
        # 1. --- LOGIC TO PRINT DIMENSIONS AND COORDINATES ---
    
        # boxes.xyxy returns the coordinates in the format [x_min, y_min, x_max, y_max]
        # boxes.cls returns the class IDs
        # We loop through each detected box
        for i in range(len(boxes)):
            # Get coordinates as a numpy array: [x_min, y_min, x_max, y_max]
            coords = boxes.xyxy[i].cpu().numpy().astype(int).flatten()
            x_min, y_min, x_max, y_max = coords
        
            # Calculate dimensions
            width = x_max - x_min
            height = y_max - y_min
            
            # Calculate the vertical midpoint (the y-coordinate of the reference line)
            # mid_y = int(height / 2)
        
            # Get class ID and look up the name
            class_id = int(boxes.cls[i].cpu().item())
            label = class_names.get(class_id, "Unknown")
            confidence = boxes.conf[i].cpu().item()
        
            # print(f"--- Detected: {label} (Conf: {confidence:.2f}) ---")
            # print(f"  Coordinates (x_min, y_min): ({x_min}, {y_min})")
            # print(f"  Coordinates (x_max, y_max): ({x_max}, {y_max})")
            # print(f"  Dimensions (W x H): {width} x {height}")
        
        # --- Monitor and apply GUI slider mutations ---
        with shared_state.data_lock:
            current_gui_sat = shared_state.camera_saturation
            current_gui_gain = shared_state.camera_exposure_gain
            current_gui_exp_time = shared_state.camera_exposure_time
            current_gui_brightness = shared_state.camera_brightness
            current_gui_contrast = shared_state.camera_contrast
            current_gui_sharpness = shared_state.camera_sharpness
            current_gui_wb_temp = shared_state.camera_wb_temp
            current_gui_conf = shared_state.confidence_threshold
            current_gui_coalesce = shared_state.coalesce_distance_threshold
            current_auto_coalesce = shared_state.auto_coalesce_enabled
            current_auto_confidence = shared_state.auto_confidence_enabled
            current_auto_cam_gain = shared_state.auto_cam_gain_enabled
            current_gui_screen_record = shared_state.screen_record_enabled
            current_gui_raw_screen_record = getattr(shared_state, 'raw_screen_record_enabled', False)
            current_gui_gamma = shared_state.camera_gamma
            current_gui_denoise = shared_state.camera_denoise
            current_gui_backlight = shared_state.camera_backlight_comp
            current_gui_flick = shared_state.camera_flick_mode
            EXPECTED_SEEDLINGS_IN_FRAME = shared_state.expected_seedlings_target
            TUNNEL_VISION = shared_state.tunnel_vision
            current_optimise_exp_by_colour = getattr(shared_state, 'OPTIMISE_EXP_TIME_BY_COLOUR', False)
            current_auto_cam_settings = getattr(shared_state, 'auto_camera_settings_enabled', False)
            
        COALESCE_THRESHOLD_SQ = current_gui_coalesce ** 2
        
        # --- BYPASS HARDWARE SDK CONTROLS IF USING VIDEO FILE ---
        if USE_CAMERA and camera_handle is not None:
        
            if current_auto_cam_settings != last_applied_auto_cam_settings:
                last_applied_auto_cam_settings = current_auto_cam_settings
            
                if current_auto_cam_settings:
                    print("[Vision SDK] Hardware Auto Settings: ENABLED (Gain, Exp Time, WB)")
                    vz.VxSetISPImageProcessing(camera_handle, exp_mode_prop, 1) # Auto Mode
                    time.sleep(adjust_time)
                    vz.VxSetISPImageProcessing(camera_handle, wb_mode_prop, 1)  # Auto Mode
                else:
                    print("[Vision SDK] Hardware Auto Settings: DISABLED (Manual Overrides Restored)")
                    vz.VxSetISPImageProcessing(camera_handle, exp_mode_prop, 0) # Manual Mode
                    time.sleep(adjust_time)
                    vz.VxSetISPImageProcessing(camera_handle, wb_mode_prop, 0)  # Manual Mode
                    time.sleep(adjust_time)
                
                    # Push the GUI sliders' current values back to the hardware
                    vz.VxSetISPImageProcessing(camera_handle, exp_gain_prop, current_gui_gain)
                    time.sleep(adjust_time)
                    vz.VxSetISPImageProcessing(camera_handle, exp_time_prop, current_gui_exp_time)
                    time.sleep(adjust_time)
                    vz.VxSetISPImageProcessing(camera_handle, wb_temp_prop, current_gui_wb_temp)

            if current_gui_sat != last_applied_saturation:
                time.sleep(adjust_time)
                vz.VxSetISPImageProcessing(camera_handle, saturation_prop, current_gui_sat)
                last_applied_saturation = current_gui_sat
                print(f"[Vision SDK] Camera saturation updated to: {current_gui_sat}")

            if current_gui_gain != last_applied_gain:
                last_applied_gain = current_gui_gain
                if not current_auto_cam_settings:
                    time.sleep(adjust_time)
                    vz.VxSetISPImageProcessing(camera_handle, exp_gain_prop, current_gui_gain)
                    print(f"[Vision SDK] Camera exposure gain updated to: {current_gui_gain}")

            if current_gui_exp_time != last_applied_exp_time:
                last_applied_exp_time = current_gui_exp_time
                if not current_auto_cam_settings:
                    time.sleep(adjust_time)
                    vz.VxSetISPImageProcessing(camera_handle, exp_time_prop, current_gui_exp_time)
                    print(f"[Vision SDK] Camera exposure time updated to: {current_gui_exp_time}")

            if current_gui_brightness != last_applied_brightness:
                time.sleep(adjust_time)
                vz.VxSetISPImageProcessing(camera_handle, brightness_prop, current_gui_brightness)
                last_applied_brightness = current_gui_brightness
                print(f"[Vision SDK] Camera brightness updated to: {current_gui_brightness}")

            if current_gui_contrast != last_applied_contrast:
                time.sleep(adjust_time)
                vz.VxSetISPImageProcessing(camera_handle, contrast_prop, current_gui_contrast)
                last_applied_contrast = current_gui_contrast
                print(f"[Vision SDK] Camera contrast updated to: {current_gui_contrast}")

            if current_gui_sharpness != last_applied_sharpness:
                time.sleep(adjust_time)
                vz.VxSetISPImageProcessing(camera_handle, sharpness_prop, current_gui_sharpness)
                last_applied_sharpness = current_gui_sharpness
                print(f"[Vision SDK] Camera sharpness updated to: {current_gui_sharpness}")
            
            if current_gui_wb_temp != last_applied_wb_temp:
                last_applied_wb_temp = current_gui_wb_temp
                if not current_auto_cam_settings:
                    time.sleep(adjust_time)
                    vz.VxSetISPImageProcessing(camera_handle, wb_temp_prop, current_gui_wb_temp)
                    print(f"[Vision SDK] Camera WB temp updated to: {current_gui_wb_temp}K")

            if current_gui_conf != last_applied_conf:
                if hasattr(model, 'predictor') and model.predictor is not None:
                    model.predictor.args.conf = current_gui_conf
                    last_applied_conf = current_gui_conf
                    print(f"[YOLO Core] Inference threshold dynamically shifted to: {current_gui_conf:.2f}")

            if current_gui_coalesce != last_applied_coalesce:
                last_applied_coalesce = current_gui_coalesce
                print(f"[Vision Processing] Coalesce distance limit shifted to: {current_gui_coalesce}")
            
            if current_auto_coalesce != last_applied_auto_coalesce:
                last_applied_auto_coalesce = current_auto_coalesce
                if current_auto_coalesce:
                    print("[Vision Processing] Auto-Coalesce Mode: ENABLED")
                else:
                    print("[Vision Processing] Auto-Coalesce Mode: DISABLED")
                
            if current_auto_confidence != last_applied_auto_confidence:
                last_applied_auto_confidence = current_auto_confidence
                if current_auto_confidence:
                    print("[Vision Processing] Auto-Confidence Mode: ENABLED")
                else:
                    print("[Vision Processing] Auto-Confidence Mode: DISABLED")
                
            if current_auto_cam_gain != last_applied_auto_cam_gain:
                last_applied_auto_cam_gain = current_auto_cam_gain
                if current_auto_cam_gain:
                    print("[Vision Processing] Auto-Cam-Gain Mode: ENABLED")
                else:
                    print("[Vision Processing] Auto-Cam-Gain Mode: DISABLED")
                
            if current_optimise_exp_by_colour != last_applied_optimise_exp:
                last_applied_optimise_exp = current_optimise_exp_by_colour
                if current_optimise_exp_by_colour:
                    print("[Vision Processing] Optimise Exp Time by Colour Mode: ENABLED")
                else:
                    print("[Vision Processing] Optimise Exp Time by Colour Mode: DISABLED")
                
            if current_gui_gamma != last_applied_gamma:
                time.sleep(adjust_time)
                vz.VxSetISPImageProcessing(camera_handle, gamma_prop, current_gui_gamma)
                last_applied_gamma = current_gui_gamma
                print(f"[Vision SDK] Camera gamma updated to: {current_gui_gamma}")

            if current_gui_denoise != last_applied_denoise:
                time.sleep(adjust_time)
                vz.VxSetISPImageProcessing(camera_handle, denoise_prop, current_gui_denoise)
                last_applied_denoise = current_gui_denoise
                print(f"[Vision SDK] Camera denoise updated to: {current_gui_denoise}")

            if current_gui_backlight != last_applied_backlight:
                time.sleep(adjust_time)
                vz.VxSetISPImageProcessing(camera_handle, backlight_prop, current_gui_backlight)
                last_applied_backlight = current_gui_backlight
                print(f"[Vision SDK] Camera backlight comp updated to: {current_gui_backlight}")
            
            if current_gui_flick != last_applied_flick:
                time.sleep(adjust_time)
                vz.VxSetISPImageProcessing(camera_handle, flick_prop, current_gui_flick)
                last_applied_flick = current_gui_flick
                print(f"[Vision SDK] Camera flicker mode updated to: {current_gui_flick}")
                
            # --- Dynamic Auto-Cam-Gain Feedback Loop (Hill Climbing) ---
            if current_auto_cam_gain:
                actual_detections = actual_detections_in_tunnel
            
                if actual_detections > 0:
                    # Calculate average confidence of detections INSIDE the tunnel
                    avg_conf = sum(tunnel_boxes_conf) / actual_detections
                
                    # If confidence dropped compared to the last frame, reverse the search direction
                    if avg_conf < prev_avg_conf:
                        gain_step_direction *= -1
                
                    # Apply the step to the gain
                    current_gui_gain += gain_step_direction
                
                    # Clamp the gain to safe SDK limits (0 to 255)
                    if current_gui_gain >= 255:
                        current_gui_gain = 255
                        gain_step_direction = -1 # Force reverse
                    elif current_gui_gain <= 0:
                        current_gui_gain = 0
                        gain_step_direction = 1  # Force reverse
                    
                    # Update previous confidence for the next frame's comparison
                    prev_avg_conf = avg_conf

                    # Push back to the GUI and Shared State
                    with shared_state.data_lock:
                        shared_state.camera_exposure_gain = current_gui_gain
                        shared_state.avg_detection_confidence = avg_conf

        # ----------------------------------------------

        # --- Handle Screen Recording State Change ---
        if current_gui_screen_record != last_applied_screen_record:
            last_applied_screen_record = current_gui_screen_record
            
            if current_gui_screen_record:
                print("[Vision Processing] Screen Recording: STARTED")
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                # Ensure directory exists
                record_dir = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/recordings"
                os.makedirs(record_dir, exist_ok=True)
                filepath = os.path.join(record_dir, f"weedinator_{timestamp}.mp4")
                video_writer = cv2.VideoWriter(filepath, fourcc, CAMERA_FRAME_RATE, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
            else:
                print("[Vision Processing] Screen Recording: STOPPED")
                if video_writer is not None:
                    video_writer.release()
                    video_writer = None
                    
        # --- Handle RAW Screen Recording State Change ---
        if current_gui_raw_screen_record != last_applied_raw_screen_record:
            last_applied_raw_screen_record = current_gui_raw_screen_record
            
            if current_gui_raw_screen_record:
                print("[Vision Processing] Raw Screen Recording: STARTED")
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                record_dir = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/recordings"
                os.makedirs(record_dir, exist_ok=True)
                filepath = os.path.join(record_dir, f"weedinator_RAW_{timestamp}.mp4")
                
                # Dynamically fetch native hardware dimensions (e.g., 1280x720) directly from YOLO's original frame capture
                native_height, native_width = result.orig_shape
                raw_video_writer = cv2.VideoWriter(filepath, fourcc, CAMERA_FRAME_RATE, (native_width, native_height))
            else:
                print("[Vision Processing] Raw Screen Recording: STOPPED")
                if raw_video_writer is not None:
                    raw_video_writer.release()
                    raw_video_writer = None

############################################################################

        # --- CV2 video Frame Processing Pipeline ---:
        
        # Get the raw image frame for color analysis and box drawing
        frame = result.orig_img
        
        # 1. Calculate tunnel boundaries scaled to the actual camera resolution
        frame_height, frame_width = result.orig_shape
        
        # ADD THIS LINE TO SET THE TRUE MIDPOINT:
        mid_y = int(frame_height / 2)

        with shared_state.data_lock:
            current_tunnel_vision = shared_state.tunnel_vision
            
        scale_x = frame_width / DISPLAY_WIDTH
        actual_tunnel_left = int(current_tunnel_vision * scale_x)
        actual_tunnel_right = frame_width - actual_tunnel_left

        # 2. Start with a clean copy of the raw frame instead of using result.plot()
        frame_with_detections = frame.copy()

        # 3. Manually render bounding boxes ONLY if they fall inside the tunnel limits and class is less than 7. Classes above 6 are weeds and slugs.
        for i in range(len(boxes)):
            # Fetch class ID first to filter out unwanted classes early
            class_id = int(boxes.cls[i].cpu().item())
            if class_id > 6:
                continue # Jumps to next box in loop.
                
            coords = boxes.xyxy[i].cpu().numpy().astype(int).flatten()
            x_min, y_min, x_max, y_max = coords
            
            # Calculate the box's horizontal center point
            box_cx = (x_min + x_max) // 2
            
            # Filter condition: Only draw if the box center is within the lines
            if actual_tunnel_left < box_cx < actual_tunnel_right:
                # Draw the bounding box rectangle (Bright Blue color in BGR: (255, 0, 0))
                cv2.rectangle(frame_with_detections, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
                
                # Fetch class label and confidence score
                label = class_names.get(class_id, "Unknown")
                confidence = boxes.conf[i].cpu().item()
                text_label = f"{label} {confidence:.2f}"
                
                # Render label text directly above the box
                cv2.putText(frame_with_detections, text_label, (x_min, y_min - 7), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)
        
        # 1. Convert OpenCV BGR to RGB (NumPy array)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        original_image_pil = Image.fromarray(rgb_frame)
        
        # Grab dynamic hue bounds
        with shared_state.data_lock:
            current_hue_lower = shared_state.hue_green_lower
            current_hue_upper = shared_state.hue_green_upper
        
        # 3. Perform blur and mask on the CPU with dynamic hues:
        masked_output_tensor, mask_tensor = perform_cv2_blur_and_mask(original_image_pil, current_hue_lower, current_hue_upper)
        
        # 4. Convert the masked image result back to BGR for OpenCV display
        # Move back to CPU, convert to NumPy, and swap RGB to BGR
        masked_frame_rgb_pil = T.ToPILImage()(masked_output_tensor)           #  CPU
        contoured_frame_bgr = cv2.cvtColor(np.array(masked_frame_rgb_pil), cv2.COLOR_RGB2BGR)
        
        # 5. --- CPU-BASED CONTOUR, CENTROID CALCULATION, AND COALESCING ---
        mask_np = mask_tensor
        
        '''
        This code snippet implements a custom software-based closed-loop feedback controller (specifically, a Proportional controller) designed to optimize the camera's exposure time dynamically. Instead of letting the camera evaluate the entire horizon, it optimizes the brightness specifically for the green plants in focus:
        '''
        
        if current_optimise_exp_by_colour and USE_CAMERA and camera_handle is not None:
            # Check if there are any pixels within the designated hue bounds
            if np.any(mask_np > 0):
                # Calculate mean grayscale value EXCLUSIVELY under the active green mask
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                mean_brightness = cv2.mean(gray_frame, mask=mask_np)[0]
                
                # Target ideal luminance midpoint (130 out of 255) for green plant definition
                target_luminance = 130.0
                brightness_error = target_luminance - mean_brightness
                
                # Calculate correction step size proportional to error
                exp_step = int(brightness_error * 25)
                
                # Apply dead-band logic (> 4 units of error) to prevent rapid shutter jitter
                if abs(brightness_error) > 4:
                    current_gui_exp_time += exp_step
                    
                    # Clamp step value safely within TechNexion SDK metrics [1 to 1,000,000]
                    current_gui_exp_time = max(1, min(current_gui_exp_time, 1000000))
                    
                    # Update the shared state and camera engine tracking
                    with shared_state.data_lock:
                        shared_state.camera_exposure_time = current_gui_exp_time

##########################################################################################################

        # Find contours
        contours, _ = cv2.findContours(mask_np, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        individual_centroids = []
        valid_contours = []
        
        for contour in contours:
            M = cv2.moments(contour)
    
            # M["m00"] is the area of the contour
            if M["m00"] != 0 and M["m00"] > MIN_CENTROID_AREA: 
        
                # Calculate centroid coordinates
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
        
                # --- FILTER BY TUNNEL VISION ---
                if actual_tunnel_left < cX < actual_tunnel_right:
                    # Store results for valid contours
                    individual_centroids.append((cX, cY))
                    valid_contours.append(contour)


##########################################################################################################

        # Coalesce (Merge) Centroids:
        centers_green = []
        coalesced_centroids = []
        used_indices = set()

        for i in range(len(individual_centroids)):
            if i in used_indices:
                continue

            cX_i, cY_i = individual_centroids[i]
            current_group = [(cX_i, cY_i)]
            used_indices.add(i)

            # Check this centroid against all others that haven't been used
            for j in range(i + 1, len(individual_centroids)):
                if j in used_indices:
                    continue
                
                cX_j, cY_j = individual_centroids[j]
                
                # Calculate squared distance
                distance_sq = (cX_i - cX_j)**2 + (cY_i - cY_j)**2
                
                if distance_sq < COALESCE_THRESHOLD_SQ:
                    current_group.append((cX_j, cY_j))
                    used_indices.add(j)

            # Calculate the average centroid for the merged group
            sum_X = sum(c[0] for c in current_group)
            sum_Y = sum(c[1] for c in current_group)
            avg_X = int(sum_X / len(current_group))
            avg_Y = int(sum_Y / len(current_group))
            
            # Store the merged centroid as a simple (X, Y) tuple
            centers_green.append((avg_X, avg_Y))
            coalesced_centroids.append({'center': (avg_X, avg_Y), 'count': len(current_group)})

        # --- Dynamic Auto-Coalesce Feedback Loop ---
        if current_auto_coalesce:
            actual_groups = len(coalesced_centroids)
        
            # If we have too many groups, grow the threshold to merge them
            if actual_groups > EXPECTED_SEEDLINGS_IN_FRAME:
                current_gui_coalesce += 2
            # If we have too few, shrink it to separate them
            elif actual_groups < EXPECTED_SEEDLINGS_IN_FRAME and len(individual_centroids) >= EXPECTED_SEEDLINGS_IN_FRAME:
                current_gui_coalesce -= 2

            # Clamp the threshold boundaries
            current_gui_coalesce = max(0, min(current_gui_coalesce, 1000))

            # 4. PUSH OVERRIDE BACK TO THE GUI
            # This updates the shared state so the next frame inherits the adjusted value
            with shared_state.data_lock:
                shared_state.coalesce_distance_threshold = current_gui_coalesce
                
        # --- Dynamic Auto-Confidence Feedback Loop ---
        if current_auto_confidence:
            # Count the bounding boxes detected by YOLO INSIDE the tunnel
            actual_detections = actual_detections_in_tunnel
        
            # If the model sees too many objects, raise confidence to drop false positives
            if actual_detections > EXPECTED_SEEDLINGS_IN_FRAME:
                current_gui_conf += 0.01
            # If the model sees too few objects, lower confidence to accept weaker predictions
            elif actual_detections < EXPECTED_SEEDLINGS_IN_FRAME:
                current_gui_conf -= 0.01

            # Clamp the threshold boundaries safely between 1% and 99%
            current_gui_conf = max(0.01, min(current_gui_conf, 0.99))

            # PUSH OVERRIDE BACK TO THE GUI AND SHARED STATE
            with shared_state.data_lock:
                # Round to 2 decimal places to keep the GUI slider looking clean
                shared_state.confidence_threshold = round(current_gui_conf, 2)


##########################################################################################################
        # Drawing: Draw contours on the processed frame (these will be blended)
        # Draw all valid contours (in bright red) on the MASKED/CONTOURED frame
        # This frame is the foreground for blending.
        cv2.drawContours(contoured_frame_bgr, valid_contours, -1, (0, 0, 255), 2)

        # 6. --- BLENDING (OVERLAY) STEP ---
        # 6. --- HIGHLY OPTIMIZED NATIVE UINT8 BLENDING (OVERLAY) STEP ---
        # Expand the binary uint8 mask (0 or 255) directly to 3 channels (No float conversion!)
        mask_3ch = cv2.cvtColor(mask_np, cv2.COLOR_GRAY2BGR)

        # Use lightning-fast bitwise operations natively on the Jetson CPU
        foreground = cv2.bitwise_and(contoured_frame_bgr, mask_3ch)
        background = cv2.bitwise_and(frame_with_detections, cv2.bitwise_not(mask_3ch))
        
        # Combine the isolated foreground and background pixels safely
        final_display_frame = cv2.add(foreground, background)
        
        # REFERENCE LINE DRAWING (RED HORIZONTAL MIDPOINT) ---
        # Get frame dimensions (Height, Width, Channels)
        # The frame to draw on is 'final_display_frame'
        # height, width, _ = final_display_frame.shape # Already calculated above

        # Calculate the vertical midpoint (the y-coordinate)
        # mid_y = int(height / 2) # Already calculated above


##########################################################################################################
        # DRAW CENTROIDS, LINES, AND LABELS ON FINAL BLENDED FRAME (Foreground) ---
        
        # Check for Alignment and Draw Lines ---
        num_detections_green = len(centers_green)

        if num_detections_green >= 2:
            # Iterate over all unique pairs of detected objects
            for i in range(num_detections_green):
                for j in range(i + 1, num_detections_green):
                    center1 = centers_green[i]
                    center2 = centers_green[j]

                    distance = calculate_distance(center1, center2)
                    if distance > LINE_LEN_MAX:
                        continue
                        
                    # Calculate the normalized angle between the centers
                    angle_deg = calculate_angle_between_centers(center1, center2)
                    
                    # --- Check for Near-Horizontal Alignment (0/180 degrees +/- tolerance) ---
                    is_near_horizontal = (angle_deg <= ANGLE_TOLERANCE_DEG) or (angle_deg >= 180 - ANGLE_TOLERANCE_DEG)
                    
                    # --- Check for Near-Vertical Alignment (90 degrees +/- tolerance) ---
                    is_near_vertical = (90 - ANGLE_TOLERANCE_DEG) <= angle_deg <= (90 + ANGLE_TOLERANCE_DEG)
                    
                    # Draw the line if either condition is met
                    if DESKTOP_DISPLAY == True: 
                        if is_near_horizontal or is_near_vertical:
                            # print("Trying to draw lines ... ")
                            # The correct frame to draw on is final_display_frame
                            LINE_THICKNESS = 2
                            cv2.line(
                                img=final_display_frame, # Draw the line on the final composite image
                                pt1=center1,
                                pt2=center2,
                                color=LINE_COLOR,
                                thickness=LINE_THICKNESS
                            )
                    
                            alignment_type = "Vertical" if is_near_vertical else "Horizontal"
                            # print(f"  ** Connected GREEN centers {i} and {j}. Alignment: {alignment_type}. Angle: {angle_deg:.2f}°")

##########################################################################################################
        # DRAW CENTROIDS AND LABELS ON FINAL BLENDED FRAME
        # Draw the COALESCED centroids and labels on the final blended image so they are always visible
        for i, data in enumerate(coalesced_centroids):
            cX, cY = data['center']
            count = data['count']

            # Draw the centroid as a bright magenta circle
            if DESKTOP_DISPLAY == True: cv2.circle(final_display_frame, (cX, cY), 10, (255, 0, 255), -1) 
            
            # Label the centroid with its index and the number of merged points (Black text)
            label = f"Group {i} ({count} obj)"
            if DESKTOP_DISPLAY == True: cv2.putText(final_display_frame, label, (cX - 30, cY - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        # Add logic from test_torch_cpu_on_camera0_49.py here.
##########################################################################################################
##########################################################################################################

        # --- LOGIC TO PRINT DIMENSIONS AND COORDINATES (Original logging kept) ---
        yolo_centers: List[Tuple[int, int]] = [] # Initialize list to store YOLO centers
        for i in range(len(boxes)):
            class_id = int(boxes.cls[i].cpu().item())
        
            # --- NEW LOGIC: Only proceed for classes 0 through 6 ---
            if 0 <= class_id <= 6:
                # Get coordinates as a numpy array: [x_min, y_min, x_max, y_max]
                coords = boxes.xyxy[i].cpu().numpy().astype(int).flatten()
                x_min, y_min, x_max, y_max = coords
            
                width = x_max - x_min
                height = y_max - y_min
            
                # Calculate center (for logging context)
                cx = int((x_min + x_max) / 2)
                cy = int((y_min + y_max) / 2)
            
                yolo_centers.append((cx, cy)) # Store YOLO center
            
                # label = class_names.get(class_id, "Unknown")
                # confidence = boxes.conf[i].cpu().item()
            
                # print(f"--- YOLO Detected: {label} (Conf: {confidence:.2f}) ---")
                # print(f"  Center: ({cx}, {cy})")
                # print(f"  Coordinates (x_min, y_min): ({x_min}, {y_min})")
                # print(f"  Coordinates (x_max, y_max): ({x_max}, {y_max})")
                # print(f"  Dimensions (W x H): {width} x {height}")
        
##########################################################################################################
        # 4. --- LOGIC TO DRAW CONNECTING LINES BETWEEN YOLO BOX CENTERS (Blue) ---
        # Use the yolo_centers for angle analysis
        centers_yolo = yolo_centers
        num_detections_yolo = len(centers_yolo)
    
        if num_detections_yolo >= 2:
            # Iterate over all unique pairs of detected objects
            for i in range(num_detections_yolo):
                for j in range(i + 1, num_detections_yolo):
                    center1 = centers_yolo[i]
                    center2 = centers_yolo[j]
                
                    # --- NEW DISTANCE CHECK ---
                    distance = calculate_distance(center1, center2)
                    if distance > LINE_LEN_MAX:
                        continue
                    # -------------------------

                    # Calculate the normalized angle between the centers
                    angle_deg = calculate_angle_between_centers(center1, center2)
                
                    # --- Check for Near-Horizontal Alignment (0/180 degrees +/- 5) ---
                    is_near_horizontal = (angle_deg <= ANGLE_TOLERANCE_DEG) or \
                                         (angle_deg >= 180 - ANGLE_TOLERANCE_DEG)
                
                    # --- Check for Near-Vertical Alignment (90 degrees +/- 5) ---
                    is_near_vertical = (90 - ANGLE_TOLERANCE_DEG) <= angle_deg <= (90 + ANGLE_TOLERANCE_DEG)
                
                    # Draw the line if either condition is met
                    if DESKTOP_DISPLAY == True: 
                        if is_near_horizontal or is_near_vertical:
                            # Draw the blue line on the frame
                            cv2.line(
                                img=final_display_frame, # Draw the line on the final composite image
                                pt1=center1,
                                pt2=center2,
                                color=YOLO_LINE_COLOR, # Use the new blue color (255, 0, 0)
                                thickness=YOLO_LINE_THICKNESS
                            )
                    
                            alignment_type = "Vertical" if is_near_vertical else "Horizontal"
                            # print(f"  ** Connected YOLO centers {i} and {j}. Alignment: {alignment_type}. Angle: {angle_deg:.2f}°")

##########################################################################################################
        # --- INITIALIZATION ---
        # We'll find the centers first, then handle all drawing at the end to ensure correct layering.
        yolo_center_point = None
        green_center_point = None
    
        # 5. --- BLUE (YOLO) CENTER DETECTION ---
        if num_detections_yolo >= 4:
            for points_tuple in itertools.combinations(centers_yolo, 4):
                points = list(points_tuple)
                # (The grouping logic is extensive, so it's omitted here for brevity, but it's the same as your original code)
                # ... grouping logic for x_groups and y_groups ...
                x_coords = [p[0] for p in points]; y_coords = [p[1] for p in points]
                x_groups = []; y_groups = []
                for x in x_coords:
                    found_group = False
                    for group in x_groups:
                        if abs(x - np.mean(group)) < AXIS_PROXIMITY_TOLERANCE:
                            group.append(x); found_group = True; break
                    if not found_group: x_groups.append([x])
                for y in y_coords:
                    found_group = False
                    for group in y_groups:
                        if abs(y - np.mean(group)) < AXIS_PROXIMITY_TOLERANCE:
                            group.append(y); found_group = True; break
                    if not found_group: y_groups.append([y])

                is_quad_found = (len(x_groups) == 2 and all(len(g) == 2 for g in x_groups) and len(y_groups) == 2 and all(len(g) == 2 for g in y_groups))
                if is_quad_found:
                    avg_x1 = np.mean(x_groups[0]); avg_x2 = np.mean(x_groups[1])
                    avg_y1 = np.mean(y_groups[0]); avg_y2 = np.mean(y_groups[1])
                    center_x = int((avg_x1 + avg_x2) / 2); center_y = int((avg_y1 + avg_y2) / 2)
                    yolo_center_point = (center_x, center_y) # Store the point, don't draw yet
                    # print(f"  *** Found BLUE NEAR-BOX (4 points) at center: {yolo_center_point}. ***")
                    break
        if TIME_CALCS == True: time_T = time.time()
        if not yolo_center_point and num_detections_yolo >= 3:
            for points_tuple in itertools.combinations(centers_yolo, 3):
                points = list(points_tuple)
                # ... grouping logic for x_groups and y_groups ...
                x_coords = [p[0] for p in points]; y_coords = [p[1] for p in points]
                x_groups = []; y_groups = []
                for x in x_coords:
                    found_group = False
                    for group in x_groups:
                        if abs(x - np.mean(group)) < AXIS_PROXIMITY_TOLERANCE:
                            group.append(x); found_group = True; break
                    if not found_group: x_groups.append([x])
                for y in y_coords:
                    found_group = False
                    for group in y_groups:
                        if abs(y - np.mean(group)) < AXIS_PROXIMITY_TOLERANCE:
                            group.append(y); found_group = True; break
                    if not found_group: y_groups.append([y])

                is_tri_found = (len(x_groups) == 2 and sorted([len(g) for g in x_groups]) == [1, 2] and len(y_groups) == 2 and sorted([len(g) for g in y_groups]) == [1, 2])
                if is_tri_found:
                    avg_x1 = np.mean(x_groups[0]); avg_x2 = np.mean(x_groups[1])
                    avg_y1 = np.mean(y_groups[0]); avg_y2 = np.mean(y_groups[1])
                    center_x = int((avg_x1 + avg_x2) / 2); center_y = int((avg_y1 + avg_y2) / 2)
                    yolo_center_point = (center_x, center_y) # Store the point, don't draw yet
                    # print(f"  *** Found BLUE L-SHAPE (3 points), interpolated center: {yolo_center_point}. ***")
                    break
##########################################################################################################
        # 5.5 --- GREEN CENTER DETECTION ---
        if num_detections_green >= 4:
            for points_tuple in itertools.combinations(centers_green, 4):
                points = list(points_tuple)
                # ... grouping logic for x_groups and y_groups ...
                x_coords = [p[0] for p in points]; y_coords = [p[1] for p in points]
                x_groups = []; y_groups = []
                for x in x_coords:
                    found_group = False
                    for group in x_groups:
                        if abs(x - np.mean(group)) < AXIS_PROXIMITY_TOLERANCE:
                            group.append(x); found_group = True; break
                    if not found_group: x_groups.append([x])
                for y in y_coords:
                    found_group = False
                    for group in y_groups:
                        if abs(y - np.mean(group)) < AXIS_PROXIMITY_TOLERANCE:
                            group.append(y); found_group = True; break
                    if not found_group: y_groups.append([y])
            
                is_quad_found = (len(x_groups) == 2 and all(len(g) == 2 for g in x_groups) and len(y_groups) == 2 and all(len(g) == 2 for g in y_groups))
                if is_quad_found:
                    avg_x1 = np.mean(x_groups[0]); avg_x2 = np.mean(x_groups[1])
                    avg_y1 = np.mean(y_groups[0]); avg_y2 = np.mean(y_groups[1])
                    center_x = int((avg_x1 + avg_x2) / 2); center_y = int((avg_y1 + avg_y2) / 2)
                    green_center_point = (center_x, center_y) # Store the point, don't draw yet
                    # print(f"  *** Found GREEN NEAR-BOX (4 points) at center: {green_center_point}. ***")
                    break

        if TIME_CALCS == True: time_V = time.time()
        if not green_center_point and num_detections_green >= 3:
            for points_tuple in itertools.combinations(centers_green, 3):
                points = list(points_tuple)
                # ... grouping logic for x_groups and y_groups ...
                x_coords = [p[0] for p in points]; y_coords = [p[1] for p in points]
                x_groups = []; y_groups = []
                for x in x_coords:
                    found_group = False
                    for group in x_groups:
                        if abs(x - np.mean(group)) < AXIS_PROXIMITY_TOLERANCE:
                            group.append(x); found_group = True; break
                    if not found_group: x_groups.append([x])
                for y in y_coords:
                    found_group = False
                    for group in y_groups:
                        if abs(y - np.mean(group)) < AXIS_PROXIMITY_TOLERANCE:
                            group.append(y); found_group = True; break
                    if not found_group: y_groups.append([y])

                is_tri_found = (len(x_groups) == 2 and sorted([len(g) for g in x_groups]) == [1, 2] and len(y_groups) == 2 and sorted([len(g) for g in y_groups]) == [1, 2])
                if is_tri_found:
                    avg_x1 = np.mean(x_groups[0]); avg_x2 = np.mean(x_groups[1])
                    avg_y1 = np.mean(y_groups[0]); avg_y2 = np.mean(y_groups[1])
                    center_x = int((avg_x1 + avg_x2) / 2); center_y = int((avg_y1 + avg_y2) / 2)
                    green_center_point = (center_x, center_y) # Store the point, don't draw yet
                    # print(f"  *** Found GREEN L-SHAPE (3 points), interpolated center: {green_center_point}. ***")
                    break
                    
        if TIME_CALCS == True: time_W = time.time()

##########################################################################################################
        # --- 6. FINAL DRAWING LOGIC (PURPLE SQUARE & CIRCLES) ---
        purple_square_center = None
    
        # Determine the final 'py' (y-coordinate) of the purple square center
        py = None 


        # Case 1: Both blue and green centers are found
        if yolo_center_point and green_center_point:
            # Calculate Euclidean distance between the two centers
            dist = np.linalg.norm(np.array(yolo_center_point) - np.array(green_center_point))
        
            if dist < 100:
                # PROXIMITY MET: Use a weighted average for the purple square's center
                # Weight: 0.7 for blue (YOLO), 0.3 for green
                px = int(green_center_point[0] * 0.3 + yolo_center_point[0] * 0.7)
                py = int(green_center_point[1] * 0.3 + yolo_center_point[1] * 0.7)
                purple_square_center = (px, py)
            else:
                # Too far apart: Default to the green center as the base
                py = green_center_point[1]
                purple_square_center = green_center_point

        # Case 2: Only the yolo or green center is found (or green is too far). Priority is given to yolo.
        elif yolo_center_point:
            py = yolo_center_point[1]
            purple_square_center = yolo_center_point

        # Case 3: Only the green center is found (or yolo is too far). This is the last resort.
        elif green_center_point:
            py = green_center_point[1]
            purple_square_center = green_center_point
            
        # --- HORIZONTAL HYDRAULIC ACTUATOR (CH12) LOGIC ---
        if USE_CAMERA:
            # Safely grab the current auto-weed state from the shared lock
            with shared_state.data_lock:
                auto_weed_state = shared_state.auto_weed_enabled
                
            # Only proceed if Auto-Weed is ON *AND* we actually have a valid tracking target
            if auto_weed_state is True and purple_square_center is not None:
                # print("frame_width/2: ", frame_width/2)
                # print("purple_square_center x: ", purple_square_center[0])
                
                ch12_data = 992 # Default to dead-center
                
                # If target is to the right of the center zone (1% deadband)
                if purple_square_center[0] < (frame_width/2 - frame_width/200):
                    ch12_data = 1200
                    print("Move to the right !!!")
                # If target is to the left of the center zone (1% deadband)
                elif purple_square_center[0] > (frame_width/2 + frame_width/200):
                    ch12_data = 800
                    print("Move to the left !!!")

                # Safely overwrite the shared state variable so the MCU thread can read it
                with shared_state.data_lock:
                    shared_state.ch12_data = ch12_data

            

        if TIME_CALCS == True: time_X = time.time()
        min_time_delta_threshold = 3.0


##########################################################################################################
        # Crossing Detection and Epoch Time Output (Using System Time) for green ---
        if green_center_point is not None:
            # Use the 'py' variable determined in the logic block above
            current_y = green_center_point[1]


            # Check the position relative to the reference line (mid_y)
            # Higher Y value is typically further DOWN the screen.
            is_currently_below_green = current_y > mid_y
            # print(f"Y-Coord: {current_y} | Below line: {is_currently_below_green}")

            # Implement state-based crossing detection
            if LAST_POSITION_BELOW_GREEN is not None:
                # print("LAST_POSITION_BELOW_GREEN is not None ",current_y)

                # Crossing detected if the state has changed AND the new position is ABOVE the line.
                if is_currently_below_green != LAST_POSITION_BELOW_GREEN  and not is_currently_below_green:
                    if LAST_CROSSING_EPOCH_TIME_GREEN is not None:
                        # Calculate time elapsed since the *last* crossing event
                        time_delta = current_epoch_time - LAST_CROSSING_EPOCH_TIME_GREEN 
                        rounded_delta = round(time_delta, 2)
                        GREEN_TIME_DELTA_ARRAY.append((current_rel_time, rounded_delta))
                        # GREEN_TIME_DELTA_ARRAY_FILTERED.append((current_rel_time, rounded_delta))
                        # print("GREEN_TIME_DELTA_ARRAY: ",GREEN_TIME_DELTA_ARRAY)
                    else:
                        # First crossing event
                        time_delta = 0.0
                        rounded_delta = 0.0

                    # --- SINGLE-LINE PRINT STATEMENT ---
                    # print("")
                    # print(f"⚠️ LINE CROSSED GRREN ⚠️  | Epoch: {current_epoch_time:.6f} | Delta: {time_delta:.6f}")
                    # print(f"TIME_DELTA_ARRAY (Reversed):           {TIME_DELTA_ARRAY[::-1]}")
                    # print(f"CORRECTED_TIME_DELTA_ARRAY (Reversed): {CORRECTED_TIME_DELTA_ARRAY[::-1]}")
                    # print("GREEN_TIME_DELTA_ARRAY: ",GREEN_TIME_DELTA_ARRAY)

                    # Filter out instances where the inference jumps backwards momentarily:
                    # expected_time_delta = 11.0 # Make this variable dynamic some time in the future.
                    # Only process and append if the time gap is large enough
                    if rounded_delta >= min_time_delta_threshold:
                        # 1. Add to the filtered array
                        append_smoothed_crossing(
                            filtered_array=GREEN_TIME_DELTA_ARRAY_FILTERED,
                            current_timestamp=current_rel_time,
                            current_delta=time_delta,
                            expected_delta=expected_time_delta 
                        )

                        # 2. UPDATE THE TIME OF THE LAST CROSSING EVENT
                        LAST_CROSSING_EPOCH_TIME_GREEN = current_epoch_time
                        
                        # 3. Create a simple average, part 2
                        try:
                            yolo_timestamp, yolo_delta = YOLO_TIME_DELTA_ARRAY_FILTERED[-1]
                            green_timestamp, green_delta = GREEN_TIME_DELTA_ARRAY_FILTERED[-1]
                            if (abs(yolo_timestamp - green_timestamp) < expected_time_delta / 3):
                                AVERAGED_TIME_DELTA_ARRAY.append(((yolo_timestamp + green_timestamp)/2, (yolo_delta + green_delta)/2 ))
                                averageCalculated = True
                        except IndexError:
                            pass

                    LAST_CROSSING_EPOCH_TIME_GREEN  = current_epoch_time
                    
                    # GREEN_TIME_DELTA_ARRAY
                    # LAST_CROSSING_EPOCH_TIME_GREEN
                    # LAST_POSITION_BELOW_GREEN

##########################################################################################################
        # Crossing Detection and Epoch Time Output (Using System Time) for yolo ---
        if yolo_center_point is not None:
            # Use the 'py' variable determined in the logic block above
            current_y = yolo_center_point[1]


            # Check the position relative to the reference line (mid_y)
            # Higher Y value is typically further DOWN the screen.
            is_currently_below_yolo = current_y > mid_y
            # print("is_currently_below_green: ",current_y)

            # Implement state-based crossing detection
            if LAST_POSITION_BELOW_YOLO is not None:
                # print("LAST_POSITION_BELOW_GREEN is not None ",current_y)

                # Crossing detected if the state has changed AND the new position is ABOVE the line.
                if is_currently_below_yolo != LAST_POSITION_BELOW_YOLO  and not is_currently_below_yolo:
                    if LAST_CROSSING_EPOCH_TIME_YOLO is not None:
                        # Calculate time elapsed since the *last* crossing event
                        time_delta = current_epoch_time - LAST_CROSSING_EPOCH_TIME_YOLO
                        rounded_delta = round(time_delta, 2)
                        # Filter out instances where the inference jumps backwards momentarily:
                        # if rounded_delta < 2.0:
                        YOLO_TIME_DELTA_ARRAY.append((current_rel_time, rounded_delta))
                        # YOLO_TIME_DELTA_ARRAY_FILTERED.append((current_rel_time, rounded_delta))
                        # print("YOLO_TIME_DELTA_ARRAY: ",YOLO_TIME_DELTA_ARRAY)
                    else:
                        # First crossing event
                        time_delta = 0.0
                        rounded_delta = 0.0

                    # --- SINGLE-LINE PRINT STATEMENT ---
                    # print("")
                    # print(f"⚠️ LINE CROSSED YOLO ⚠️  | Epoch: {current_epoch_time:.6f} | Delta: {time_delta:.6f}")
                    # print(f"TIME_DELTA_ARRAY (Reversed):           {TIME_DELTA_ARRAY[::-1]}")
                    # print(f"CORRECTED_TIME_DELTA_ARRAY (Reversed): {CORRECTED_TIME_DELTA_ARRAY[::-1]}")


                    # Filter out instances where the inference jumps backwards momentarily:
                    if rounded_delta >= min_time_delta_threshold:
                        # 1. Add to the filtered array
                        append_smoothed_crossing(
                            filtered_array=YOLO_TIME_DELTA_ARRAY_FILTERED,
                            current_timestamp=current_rel_time,
                            current_delta=time_delta,
                            expected_delta=expected_time_delta 
                        )

                        # 2. UPDATE THE TIME OF THE LAST CROSSING EVENT
                        LAST_CROSSING_EPOCH_TIME_YOLO = current_epoch_time
                        
                        # 3. Create a simple average, part 2
                        try:
                            yolo_timestamp, yolo_delta = YOLO_TIME_DELTA_ARRAY_FILTERED[-1]
                            green_timestamp, green_delta = GREEN_TIME_DELTA_ARRAY_FILTERED[-1]
                            if (abs(yolo_timestamp - green_timestamp) < expected_time_delta / 3):
                                AVERAGED_TIME_DELTA_ARRAY.append(((yolo_timestamp + green_timestamp)/2, (yolo_delta + green_delta)/2 ))
                                averageCalculated = True
                        except IndexError:
                            pass

                    LAST_CROSSING_EPOCH_TIME_YOLO  = current_epoch_time


            # Update the position state for the next frame
            # LAST_POSITION_BELOW = is_currently_below
            LAST_POSITION_BELOW_GREEN = is_currently_below_green
            LAST_POSITION_BELOW_YOLO= is_currently_below_yolo

##########################################################################################################
        # Check AVERAGED_TIME_DELTA_ARRAY for double and triple entries:
        # Create a for loop:
        duplicate_timestamp = True
        try:
            while duplicate_timestamp == True:
                timestamp_a, delta_time_a = AVERAGED_TIME_DELTA_ARRAY[-1]
                timestamp_b, delta_time_b = AVERAGED_TIME_DELTA_ARRAY[-2]
                timestamp_c, delta_time_c = AVERAGED_TIME_DELTA_ARRAY[-3]
                if (timestamp_b == timestamp_c):
                    duplicate_timestamp = True
                    AVERAGED_TIME_DELTA_ARRAY.pop(-2)
                    # print("⚠️⚠️⚠️⚠️⚠️⚠️⚠️   Duplicate timestamp found !!   ⚠️⚠️⚠️⚠️⚠️⚠️⚠️")
                if (timestamp_a == timestamp_b):
                    duplicate_timestamp = True
                    AVERAGED_TIME_DELTA_ARRAY.pop(-1)
                    # print("⚠️⚠️⚠️⚠️⚠️⚠️⚠️   Duplicate timestamp found !!   ⚠️⚠️⚠️⚠️⚠️⚠️⚠️")
                else:
                    duplicate_timestamp = False
                    # print("AVERAGED_TIME_DELTA_ARRAY: ",AVERAGED_TIME_DELTA_ARRAY)
        except:
            pass

        try:
            if (averageCalculated == True):
                print("averageCalculated == True")
                
                # Firstly initialise the array with 5 points:
                # May need to put 5 sets of objects on the ground to achive this
                '''
                if len(LIGHT_BULB_FLASH_DELTA_ARRAY) == 1:
                    timestamp, delta_time = LIGHT_BULB_FLASH_DELTA_ARRAY[-1]
                    PREDICTED_TIME_DELTA_ARRAY.append((timestamp, delta_time))
                    
                if len(LIGHT_BULB_FLASH_DELTA_ARRAY) == 2:
                    timestamp, delta_time = LIGHT_BULB_FLASH_DELTA_ARRAY[-1]
                    PREDICTED_TIME_DELTA_ARRAY.append((timestamp, delta_time))
                    
                if len(LIGHT_BULB_FLASH_DELTA_ARRAY) == 3:
                    timestamp, delta_time = LIGHT_BULB_FLASH_DELTA_ARRAY[-1]
                    PREDICTED_TIME_DELTA_ARRAY.append((timestamp, delta_time))
                    
                if len(LIGHT_BULB_FLASH_DELTA_ARRAY) == 4:
                    timestamp, delta_time = LIGHT_BULB_FLASH_DELTA_ARRAY[-1]
                    PREDICTED_TIME_DELTA_ARRAY.append((timestamp, delta_time))
                    
                if len(LIGHT_BULB_FLASH_DELTA_ARRAY) == 5:
                    timestamp, delta_time = LIGHT_BULB_FLASH_DELTA_ARRAY[-1]
                    PREDICTED_TIME_DELTA_ARRAY.append((timestamp, delta_time))
                '''


                # Use expected_time_delta as a starting point.
                if len(LIGHT_BULB_FLASH_DELTA_ARRAY) >= 1:
                    timestamp_a, delta_time_a = LIGHT_BULB_FLASH_DELTA_ARRAY[-1]
                    
                # Use different values for timestamp_a and delta_time_a after missing initial data point detected since no flash delta array value is available:
                if (len(LIGHT_BULB_FLASH_DELTA_ARRAY) >= 1) and (first_missing == True):
                    timestamp_a, delta_time_a = PREDICTED_TIME_DELTA_ARRAY[-1]

                if len(LIGHT_BULB_FLASH_DELTA_ARRAY) >= 2:
                    timestamp_b, delta_time_b = LIGHT_BULB_FLASH_DELTA_ARRAY[-2]

                if len(LIGHT_BULB_FLASH_DELTA_ARRAY) >= 3:
                    timestamp_c, delta_time_c = LIGHT_BULB_FLASH_DELTA_ARRAY[-3]

                if len(LIGHT_BULB_FLASH_DELTA_ARRAY) >= 4:
                    timestamp_d, delta_time_d = LIGHT_BULB_FLASH_DELTA_ARRAY[-4]
                    
                if len(LIGHT_BULB_FLASH_DELTA_ARRAY) >= 5:
                    timestamp_e, delta_time_e = LIGHT_BULB_FLASH_DELTA_ARRAY[-5]
                    

                    # print("timestamp_d, delta_time_d: ",timestamp_d, delta_time_d)
                # elif len(YOLO_TIME_DELTA_ARRAY_FILTERED) >= 4:
                    # print("No value for AVERAGED_TIME_DELTA_ARRAY[-5] !!!!")
                    # print("timestamp_d, delta_time_e: ",timestamp_d, delta_time_e)
                    # timestamp_a, delta_time_e = YOLO_TIME_DELTA_ARRAY_FILTERED[-4]

                # else:
                    # delta_time_e = expected_time_delta
                    # print("delta_time_a: ",delta_time_e)

                
                # timestamp_b, delta_time_b = AVERAGED_TIME_DELTA_ARRAY[-3]
                # timestamp_c, delta_time_c = AVERAGED_TIME_DELTA_ARRAY[-4]
                # timestamp_d, delta_time_d = AVERAGED_TIME_DELTA_ARRAY[-5]


        except:
            pass
            
###############################################################################################################################################
        # Weights must add up to 1.0:
        weight_a5 = 0.3
        weight_b5 = 0.25
        weight_c5 = 0.20
        weight_d5 = 0.15
        weight_e5 = 0.1
        
        weight_a4 = 0.4
        weight_b4 = 0.25
        weight_c4 = 0.20
        weight_d4 = 0.15
        
        weight_a3 = 0.6
        weight_b3 = 0.3
        weight_c3 = 0.1

        
        weight_a2 = 0.7
        weight_b2 = 0.3


        try:
            if (averageCalculated == True):
                print("💡💡💡💡💡💡💡💡 Yellow Flash !!! 💡💡💡💡💡💡💡💡")
                
                # --- NEW FLASH DELTA LOGIC ---
                # Calculate the delta purely based on the elapsed time between actual light bulb flashes
                if LAST_FLASH_EPOCH_TIME is not None:
                    actual_flash_delta = round(current_epoch_time - LAST_FLASH_EPOCH_TIME, 3)
                else:
                    # Fallback for the very first flash before a delta can be established
                    actual_flash_delta = expected_time_delta 
                
                # Update the timestamp tracker for the next flash calculation
                LAST_FLASH_EPOCH_TIME = current_epoch_time
                
                # Append the truly measured flash delta
                LIGHT_BULB_FLASH_DELTA_ARRAY.append((current_rel_time, actual_flash_delta))

                # --- Debounce LIGHT_BULB_FLASH_DELTA_ARRAY ---
                # Rebuild the array in-place, keeping only entries where the delta is >= DEBOUNCE_TIME
                LIGHT_BULB_FLASH_DELTA_ARRAY[:] = [
                    pair for pair in LIGHT_BULB_FLASH_DELTA_ARRAY 
                    if pair[1] >= DEBOUNCE_TIME
                ]

                
                # ADD THIS TO TRIGGER GUI:
                with shared_state.data_lock:
                    shared_state.yellow_flash_event = True
                    
                if len(LIGHT_BULB_FLASH_DELTA_ARRAY) == 2:
                    delta_time_p = round(((delta_time_a * weight_a2) + (delta_time_b * weight_b2) ),3)
                    expected_time_delta = delta_time_p
                    print("expected_time_delta: ",expected_time_delta)
                    with shared_state.data_lock:
                        shared_state.expected_time_delta_val = expected_time_delta
               
                if len(LIGHT_BULB_FLASH_DELTA_ARRAY) == 3:
                    delta_time_p = round(((delta_time_a * weight_a3) + (delta_time_b * weight_b3) + (delta_time_c * weight_c3) ),3)
                    expected_time_delta = delta_time_p
                    print("expected_time_delta: ",expected_time_delta)
                    with shared_state.data_lock:
                        shared_state.expected_time_delta_val = expected_time_delta
                        
                if len(LIGHT_BULB_FLASH_DELTA_ARRAY) == 4:
                    delta_time_p = round(((delta_time_a * weight_a4) + (delta_time_b * weight_b4) + (delta_time_c * weight_c4) + (delta_time_d * weight_d4) ),3)
                    expected_time_delta = delta_time_p
                    print("expected_time_delta: ",expected_time_delta)
                    with shared_state.data_lock:
                        shared_state.expected_time_delta_val = expected_time_delta

                if len(LIGHT_BULB_FLASH_DELTA_ARRAY) >= 5:
                    delta_time_p = round(((delta_time_a * weight_a5) + (delta_time_b * weight_b5) + (delta_time_c * weight_c5) + (delta_time_d * weight_d5)  + (delta_time_e * weight_e5)),3)
                    expected_time_delta = delta_time_p
                    print("expected_time_delta: ",expected_time_delta)
                    with shared_state.data_lock:
                        shared_state.expected_time_delta_val = expected_time_delta

                    # delta_time_e = delta_time_a
                
                # --- UPDATED PREDICTION STEP ---
                # Predict the exact coordinate for the next light bulb flash on the graph.
                # X-axis: Current system time of this flash + the expected wait time until the next one.
                # Y-axis: The expected time delta itself.
                next_flash_timestamp = current_rel_time + expected_time_delta
                PREDICTED_TIME_DELTA_ARRAY.append((next_flash_timestamp, expected_time_delta))
                
                last_prediction_time = time.time()
                # print("PREDICTED_TIME_DELTA_ARRAY: ",PREDICTED_TIME_DELTA_ARRAY)

                # Put this block where the YELLOW_FLASH condition is set and PREDICTED_TIME_DELTA_ARRAY is set.
                if RECORD_GRAPH_DATA:
                    graph_file_path = '/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/graph_data.txt'
    
                    # Bundle the requested time delta arrays into a structured dictionary
                    # "GREEN_TIME_DELTA_ARRAY": GREEN_TIME_DELTA_ARRAY,
                    # "YOLO_TIME_DELTA_ARRAY": YOLO_TIME_DELTA_ARRAY,
                    data_to_record = {
                        "GREEN_TIME_DELTA_ARRAY_FILTERED": GREEN_TIME_DELTA_ARRAY_FILTERED,
                        "YOLO_TIME_DELTA_ARRAY_FILTERED": YOLO_TIME_DELTA_ARRAY_FILTERED,
                        "AVERAGED_TIME_DELTA_ARRAY": AVERAGED_TIME_DELTA_ARRAY,
                        "PREDICTED_TIME_DELTA_ARRAY": PREDICTED_TIME_DELTA_ARRAY,
                        "LIGHT_BULB_FLASH_DELTA_ARRAY": LIGHT_BULB_FLASH_DELTA_ARRAY
                    }
    
                    try:
                        # print("Try to record graph data ....")
                        # Ensure target directory exists before writing
                        os.makedirs(os.path.dirname(graph_file_path), exist_ok=True)
        
                        # Open and overwrite the text file with the latest structured data using JSON
                        with open(graph_file_path, 'w') as f:
                            json.dump(data_to_record, f, indent=4)
            
                        # print(f"[Data Logger] Graph data successfully updated at: {graph_file_path}")
                    except Exception as e:
                        print(f"[Data Logger] Failed to save graph data: {e}")

                first_missing = False
                second_missing = False
                third_missing = False
                fourth_missing = False
                fith_missing = False
        except:
            pass
        
        '''
        try:
            
            # Look for the first missing data point in a possible sequence of many:
            timestamp, delta_time = AVERAGED_TIME_DELTA_ARRAY[-1]
            # Need to look back a bit more than expected time delta due to the last step being predicted.
            if ((current_epoch_time - last_prediction_time) > (expected_time_delta * 1.0) and (averageCalculated == False)):
                timestamp, delta_time = PREDICTED_TIME_DELTA_ARRAY[-1]
                # Add in the missing data point:
                PREDICTED_TIME_DELTA_ARRAY.append((timestamp + expected_time_delta, expected_time_delta))
                first_missing = True
                last_prediction_time = time.time()
                print("⚠️⚠️⚠️⚠️⚠️⚠️⚠️    Missing initial data point was added !!!    ⚠️⚠️⚠️⚠️⚠️⚠️⚠️")

        except:
            pass
        '''
            
        # Reset flag:
        averageCalculated = False
                
################################################################################################################################################################

        # --- DRAW EVERYTHING (in the correct order) ---

        if TIME_CALCS == True: time_Y = time.time()
        # 1. Draw the purple square FIRST so it's in the background
        if purple_square_center:
            SQUARE_HALF_SIDE = 20 # Make it slightly larger than the circle radius of 15
            pt1 = (purple_square_center[0] - SQUARE_HALF_SIDE, purple_square_center[1] - SQUARE_HALF_SIDE)
            pt2 = (purple_square_center[0] + SQUARE_HALF_SIDE, purple_square_center[1] + SQUARE_HALF_SIDE)
            PURPLE_COLOR = (128, 0, 128) # BGR color for Purple
            if DESKTOP_DISPLAY == True: cv2.rectangle(final_display_frame, pt1, pt2, PURPLE_COLOR, -1)

        # 2. Draw the blue YOLO circle on TOP (if it was found)
        if yolo_center_point:
            if DESKTOP_DISPLAY == True: cv2.circle(final_display_frame, yolo_center_point, 15, YOLO_LINE_COLOR, -1)
    
        # 3. Draw the green circle on TOP (if it was found)
        if green_center_point:
            GREEN_COLOR = (0, 255, 0)
            if DESKTOP_DISPLAY == True: cv2.circle(final_display_frame, green_center_point, 15, GREEN_COLOR, -1)
        
        # 4. Draw the yellow circle on TOP (if it was found)
        if YELLOW_FLASH == True:
            YELLOW_COLOR=(255,255,0)
            # Use integer division to prevent errors with floats.
            # if DESKTOP_DISPLAY == True: cv2.circle(final_display_frame, (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2) , 60, YELLOW_COLOR, -1)
            if DESKTOP_DISPLAY == True: cv2.circle(final_display_frame, (400, DISPLAY_HEIGHT // 2) , 60, YELLOW_COLOR, -1)
            # print("💡💡💡💡💡💡💡💡 Yellow Flash !!! 💡💡💡💡💡💡💡💡")
            
            # ADD THIS TO TRIGGER GUI:
            # with shared_state.data_lock:
                # shared_state.yellow_flash_event = True

            # Reset yellow flash
            YELLOW_FLASH = False

##########################################################################################################

        # Display the frame with detections
        # Using result.plot() to get the image frame with boxes drawn on it
        # frame_with_detections = result.plot()
        # frame_resized = cv2.resize(frame_with_detections, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        frame_resized = cv2.resize(final_display_frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        
        # TUNNEL VISION VERTICAL LINES and trigger lines DRAWING:
        if DESKTOP_DISPLAY == True:
            # Middle trigger line:
            cv2.line(frame_resized, (0, int(DISPLAY_HEIGHT/2)), (DISPLAY_WIDTH, int(DISPLAY_HEIGHT/2)), (0, 0, 255), 2)
            # Left vertical line (thin, thickness=1)
            cv2.line(frame_resized, (TUNNEL_VISION, 0), (TUNNEL_VISION, DISPLAY_HEIGHT), (0, 0, 255), 2)
            # Right vertical line (thin, thickness=1)
            cv2.line(frame_resized, (DISPLAY_WIDTH - TUNNEL_VISION, 0), (DISPLAY_WIDTH - TUNNEL_VISION, DISPLAY_HEIGHT), (0, 0, 255), 2)
        
        # Write to recording file if enabled
        if last_applied_screen_record and video_writer is not None:
            video_writer.write(frame_resized)
            
        if last_applied_raw_screen_record and raw_video_writer is not None:
            # result.orig_img (aliased as 'frame' earlier in your loop) contains the untouched 
            # BGR NumPy array directly from the camera feed before cv2.rectangle or contours were applied.
            raw_video_writer.write(frame)
        # ---------------------------------------------
       
        # OpenCV uses BGR natively, Tkinter requires RGB
        cv2image = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            
        # Convert to PIL Image ONLY
        img = Image.fromarray(cv2image)

        with shared_state.data_lock:
            shared_state.latest_frame = img # Pass the PIL image, not ImageTk

        # --- Update shared collections for live graph animation ---
        with shared_state.data_lock:
            # Sync the event-driven local arrays to the shared state
            shared_state.graph_green_filtered.clear()
            shared_state.graph_green_filtered.extend(GREEN_TIME_DELTA_ARRAY_FILTERED[-shared_state.MAX_GRAPH_POINTS:])
            
            shared_state.graph_yolo_filtered.clear()
            shared_state.graph_yolo_filtered.extend(YOLO_TIME_DELTA_ARRAY_FILTERED[-shared_state.MAX_GRAPH_POINTS:])
            
            shared_state.graph_averaged.clear()
            shared_state.graph_averaged.extend(AVERAGED_TIME_DELTA_ARRAY[-shared_state.MAX_GRAPH_POINTS:])
            
            shared_state.graph_predicted.clear()
            shared_state.graph_predicted.extend(PREDICTED_TIME_DELTA_ARRAY[-shared_state.MAX_GRAPH_POINTS:])
            
            shared_state.graph_light_bulb_flash.clear()
            shared_state.graph_light_bulb_flash.extend(LIGHT_BULB_FLASH_DELTA_ARRAY[-shared_state.MAX_GRAPH_POINTS:])
            
        time.sleep(1/CAMERA_FRAME_RATE)
        
    cap.release()
        
# update_camera_frame()
