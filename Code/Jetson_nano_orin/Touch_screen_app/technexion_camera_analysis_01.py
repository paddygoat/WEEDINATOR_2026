


'''
cd && source python_env_01/bin/activate &&
export LD_LIBRARY_PATH=/home/nano/python_env_01/lib/python3.10/site-packages/nvidia/cusparselt/lib:\$LD_LIBRARY_PATH &&
cd /home/nano/Documents/WEEDINATOR/Code/Jetson_nano && python3 technexion_camera_analysis_01.py
'''

import subprocess
import pyvizionsdk as vz

def get_camera_details(device_path):
    
    print("Available Resolutions and Frame Rates:")
    print("---")
    try:
        v4l2_cmd = ["v4l2-ctl", "-d", device_path, "--list-formats-ext"]
        v4l2_output = subprocess.check_output(v4l2_cmd, text=True)
        print(v4l2_output)
    except FileNotFoundError:
        print("v4l2-ctl utility is missing on this system.")
    print("---")
    
    print("Adjustable ISP Properties:")
    print("---")
    
    # Initialize the camera using pyvizionsdk
    # Initialize and open the camera device handle at index 0
    initialise = vz.VxInitialCameraDevice(0)
    camera = vz.VxOpen(initialise)
    
    # Dictionary mapping friendly names to the SDK's internal enumerations
    properties = {
        "Brightness": vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_BRIGHTNESS,
        "Contrast": vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_CONTRAST,
        "Saturation": vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_SATURATION,
        "Hue": vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_HUE,
        "Gamma": vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_GAMMA,
        "Sharpness": vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_SHARPNESS,
        "White Balance": vz.VX_ISP_IMAGE_PROPERTIES.ISP_IMAGE_WHITE_BALANCE
    }

    for prop_name, prop_enum in properties.items():
        try:
            # The API returns a tuple containing the execution result alongside the metrics
            result, min_val, max_val, step, def_val = vz.VxGetISPImageProcessingRange(camera, prop_enum)
            
            print(f"{prop_name} Property Metrics:")
            print(f"Range: [{min_val} to {max_val}]")
            print(f"Default: {def_val}")
            print(f"Step: {step}")
            print("---")
        except AttributeError:
            pass

    vz.VxCloseDevice(camera)

get_camera_details("/dev/video0")
