# weedinator_gui.py

import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
import os
import sys
import shared_state # Import your new state file
import cv2
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# send_data_state = False

def gui_thread():

    def toggle_send_data():
        # nonlocal send_data_state
        with shared_state.data_lock:
            shared_state.send_data_state = not shared_state.send_data_state
        
        if shared_state.send_data_state:
            # Change to Red when True
            btn_send_data.config(bg="#e74c3c", activebackground="#e74c3c", activeforeground="white") 
            with shared_state.data_lock:
                shared_state.send_data_state = True
        else:
            # Change to Green when False
            btn_send_data.config(bg="#2ecc71", activebackground="#2ecc71", activeforeground="white")
            with shared_state.data_lock:
                shared_state.send_data_state = False

    def load_slider_values():
        path1 = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/slider_1_val.txt"
        path2 = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/slider_2_val.txt"
        path_sat = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_saturation.txt"
        path_gain = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_exposure_gain.txt"
        path_conf = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/confidence_threshold.txt"
        path_coalesce = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/coalesce_distance_threshold.txt"
        path_target_plants = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/expected_seedlings_target.txt"
        path_tunnel_vision = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/tunnel_vision.txt"
        path_exp_time = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_exposure_time.txt"
        path_brightness = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_brightness.txt"
        path_contrast = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_contrast.txt"
        path_sharpness = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_sharpness.txt"
        path_wb_temp = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_wb_temp.txt"
        path_hue_lower = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/hue_green_lower.txt"
        path_hue_upper = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/hue_green_upper.txt"
        path_gamma = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_gamma.txt"
        path_denoise = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_denoise.txt"
        path_backlight = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_backlight_comp.txt"
        path_flick = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_flick_mode.txt"
        path_simulate = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/simulate_status.txt"
        
        # Set defaults in case files don't exist yet
        val1, val2 = 0, 0 
        val_sat = 15
        val_gain = 15
        val_conf = 0.10
        val_coalesce = 50
        val_target_plants = 4
        val_tunnel_vision = 200
        val_exp_time = 1000
        val_brightness = -3
        val_contrast = -30
        val_sharpness = 20
        val_wb_temp = 5000
        val_hue_lower, val_hue_upper = 0.194, 0.511
        val_gamma = 10
        val_denoise = 5
        val_backlight = 0
        val_flick = 0
        val_simulate = True
        
        try:
            if os.path.exists(path1):
                with open(path1, "r") as f:
                    val1 = int(f.read().strip())
            if os.path.exists(path2):
                with open(path2, "r") as f:
                    val2 = int(f.read().strip())
            if os.path.exists(path_sat):
                with open(path_sat, "r") as f:
                    val_sat = int(f.read().strip())
            if os.path.exists(path_gain):
                with open(path_gain, "r") as f:
                    val_gain = int(f.read().strip())
            if os.path.exists(path_conf):
                with open(path_conf, "r") as f:
                    val_conf = float(f.read().strip())
            if os.path.exists(path_coalesce):
                with open(path_coalesce, "r") as f:
                    val_coalesce = int(f.read().strip())
            if os.path.exists(path_target_plants):
                with open(path_target_plants, "r") as f:
                    val_target_plants = int(f.read().strip())
            if os.path.exists(path_tunnel_vision):
                with open(path_tunnel_vision, "r") as f:
                    val_tunnel_vision = int(f.read().strip())
            if os.path.exists(path_exp_time):
                with open(path_exp_time, "r") as f:
                    val_exp_time = int(f.read().strip())
            if os.path.exists(path_brightness):
                with open(path_brightness, "r") as f:
                    val_brightness = int(f.read().strip())
            if os.path.exists(path_contrast):
                with open(path_contrast, "r") as f:
                    val_contrast = int(f.read().strip())
            if os.path.exists(path_sharpness):
                with open(path_sharpness, "r") as f:
                    val_sharpness = int(f.read().strip())
            if os.path.exists(path_wb_temp):
                with open(path_wb_temp, "r") as f:
                    val_wb_temp = int(f.read().strip())
            if os.path.exists(path_hue_lower):
                with open(path_hue_lower, "r") as f:
                    val_hue_lower = float(f.read().strip())
            if os.path.exists(path_hue_upper):
                with open(path_hue_upper, "r") as f:
                    val_hue_upper = float(f.read().strip())
            if os.path.exists(path_flick):
                with open(path_flick, "r") as f: val_flick = int(f.read().strip())
            if os.path.exists(path_gamma):
                with open(path_gamma, "r") as f: val_gamma = int(f.read().strip())
            if os.path.exists(path_denoise):
                with open(path_denoise, "r") as f: val_denoise = int(f.read().strip())
            if os.path.exists(path_backlight):
                with open(path_backlight, "r") as f: val_backlight = int(f.read().strip())
            if os.path.exists(path_simulate):
                with open(path_simulate, "r") as f: val_simulate = (f.read().strip() == "True")
                

            print(f"Loaded persistent settings: Slider1={val1}, Slider2={val2}, Saturation={val_sat}, Gain={val_gain}, Confidence={val_conf}, Coalesce={val_coalesce}")
        except Exception as e:
            print(f"Could not load saved values (using defaults): {e}")
            
        # Update the global variables used by the rest of the logic
        with shared_state.data_lock:
            shared_state.slider_1_val = val1
            shared_state.slider_2_val = val2
            shared_state.camera_saturation = val_sat
            shared_state.camera_exposure_gain = val_gain
            shared_state.confidence_threshold = val_conf
            shared_state.coalesce_distance_threshold = val_coalesce
            shared_state.expected_seedlings_target = val_target_plants
            shared_state.tunnel_vision = val_tunnel_vision
            shared_state.camera_exposure_time = val_exp_time
            shared_state.camera_brightness = val_brightness
            shared_state.camera_contrast = val_contrast
            shared_state.camera_sharpness = val_sharpness
            shared_state.camera_wb_temp = val_wb_temp
            shared_state.hue_green_lower = val_hue_lower
            shared_state.hue_green_upper = val_hue_upper
            shared_state.camera_gamma = val_gamma
            shared_state.camera_denoise = val_denoise
            shared_state.camera_backlight_comp = val_backlight
            shared_state.camera_flick_mode = val_flick
            shared_state.USE_CAMERA = val_simulate

    # Execute the load immediately
    load_slider_values()

    root = tk.Tk()
    root.title("Weedinator Control Panel")
    
    is_fullscreen = False
    root.attributes('-fullscreen', True)
    root.geometry("1920x1200+0+0")
    root.configure(bg='#1a1a1a')

    # Fonts
    header_font = tkfont.Font(family="Helvetica", size=24, weight="bold")
    data_font = tkfont.Font(family="Courier", size=48, weight="bold")
    small_data_font = tkfont.Font(family="Courier", size=32, weight="bold")
    status_font = tkfont.Font(family="Helvetica", size=18, weight="bold")
    button_font = tkfont.Font(family="Helvetica", size=22, weight="bold")
    slider_font = tkfont.Font(family="Helvetica", size=10, weight="bold")
    
    def save_slider_values():
        """Overwrites the text files with current slider values on a single line."""
        # Grab values safely with your lock
        with shared_state.data_lock:
            val1 = str(shared_state.slider_1_val)
            val2 = str(shared_state.slider_2_val)
            val_sat = str(shared_state.camera_saturation)
            val_gain = str(shared_state.camera_exposure_gain)
            val_conf = str(shared_state.confidence_threshold)
            val_coalesce = str(shared_state.coalesce_distance_threshold)
            val_target_plants = str(shared_state.expected_seedlings_target)
            val_tunnel_vision = str(shared_state.tunnel_vision)
            val_exp_time = str(shared_state.camera_exposure_time)
            val_brightness = str(shared_state.camera_brightness)
            val_contrast = str(shared_state.camera_contrast)
            val_sharpness = str(shared_state.camera_sharpness)
            val_wb_temp = str(shared_state.camera_wb_temp)
            val_gamma = str(shared_state.camera_gamma)
            val_denoise = str(shared_state.camera_denoise)
            val_backlight = str(shared_state.camera_backlight_comp)
            val_flick = str(shared_state.camera_flick_mode)
            val_simulate = str(shared_state.USE_CAMERA)
            
        paths = {
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/slider_1_val.txt": val1,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/slider_2_val.txt": val2,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_saturation.txt": val_sat,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_exposure_gain.txt": val_gain,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/confidence_threshold.txt": val_conf,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/coalesce_distance_threshold.txt": val_coalesce,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/expected_seedlings_target.txt": val_target_plants,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/tunnel_vision.txt": val_tunnel_vision,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_exposure_time.txt": val_exp_time,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_brightness.txt": val_brightness,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_contrast.txt": val_contrast,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_sharpness.txt": val_sharpness,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_wb_temp.txt": val_wb_temp,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/hue_green_lower.txt": str(shared_state.hue_green_lower),
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/hue_green_upper.txt": str(shared_state.hue_green_upper),
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_gamma.txt": val_gamma,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_denoise.txt": val_denoise,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_backlight_comp.txt": val_backlight,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/camera_flick_mode.txt": val_flick,
            "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/simulate_status.txt": val_simulate
        }
        
        try:
            for path, value in paths.items():
                with open(path, "w") as f:
                    f.write(value) 
            print("All slider, camera, and algorithm configurations successfully overwritten.")
        except Exception as e:
            print(f"File Save Error: {e}")
            
    def toggle_auto_weed():
        with shared_state.data_lock:
            shared_state.auto_weed_enabled = not shared_state.auto_weed_enabled
            current_state = shared_state.auto_weed_enabled
            
        if current_state:
            btn_auto_weed.config(text="AUTO WEED: ON", bg="#2ecc71", activebackground="#2ecc71")
        else:
            btn_auto_weed.config(text="AUTO WEED: OFF", bg="#e74c3c", activebackground="#e74c3c")
            
    def toggle_simulate_mode():
        with shared_state.data_lock:
            # Flip the boolean (True = Camera, False = Simulate/Video)
            shared_state.USE_CAMERA = not shared_state.USE_CAMERA
            current_state = shared_state.USE_CAMERA
            
        if current_state:
            # Camera mode (Simulation OFF)
            btn_simulate.config(text="SIMULATE: OFF", bg="#e74c3c", activebackground="#e74c3c")
        else:
            # Video file mode (Simulation ON)
            btn_simulate.config(text="SIMULATE: ON", bg="#2ecc71", activebackground="#2ecc71")

    def toggle_screen_mode():
        nonlocal is_fullscreen
        is_fullscreen = not is_fullscreen
        root.attributes("-fullscreen", is_fullscreen)
        if not is_fullscreen:
            root.geometry("1920x1200+0+0")
            btn_toggle.config(text="GO FULLSCREEN", bg="#2980b9", activebackground="#2980b9", activeforeground="white")
        else:
            btn_toggle.config(text="EXIT FULLSCREEN", bg="#34495e", activebackground="#34495e", activeforeground="white")

    def quit_app():
        if messagebox.askyesno("Quit", "Stop the Weedinator app?"):
            save_slider_values()  
            # cleanup_resources()
            root.destroy()
            os._exit(0)

    def restart_app():
        if messagebox.askyesno("Restart", "Are you sure you want to RESTART the Weedinator app?"):
            save_slider_values()  
            # cleanup_resources()
            root.destroy()
            os.execl(sys.executable, sys.executable, *sys.argv)

    def shutdown_jetson():
        if messagebox.askyesno("SHUTDOWN", "Are you sure you want to SHUTDOWN the Jetson Nano?"):
            save_slider_values()  
            # cleanup_resources()
            os.system("sudo shutdown -h now")

    def update_slider1(val):
        with shared_state.data_lock:
            shared_state.slider_1_val = int(val)

    def update_slider2(val):
        with shared_state.data_lock:
            shared_state.slider_2_val = int(val)
            
    def update_saturation(val):
        with shared_state.data_lock:
            shared_state.camera_saturation = int(val)
            
    def update_exposure_gain(val):
        with shared_state.data_lock:
            shared_state.camera_exposure_gain = int(val)
            
    def update_confidence(val):
        with shared_state.data_lock:
            shared_state.confidence_threshold = float(val)
            
    def update_coalesce_distance(val):
        with shared_state.data_lock:
            shared_state.coalesce_distance_threshold = int(val)
            
    def update_expected_seedlings(val):
        with shared_state.data_lock:
            shared_state.expected_seedlings_target = int(val)
            
    def update_tunnel_vision(val):
        with shared_state.data_lock:
            shared_state.tunnel_vision = int(val)
            
    def update_exposure_time(val):
        with shared_state.data_lock:
            shared_state.camera_exposure_time = int(val)

    def update_brightness(val):
        with shared_state.data_lock:
            shared_state.camera_brightness = int(val)

    def update_contrast(val):
        with shared_state.data_lock:
            shared_state.camera_contrast = int(val)

    def update_sharpness(val):
        with shared_state.data_lock:
            shared_state.camera_sharpness = int(val)
            
    def update_wb_temp(val):
        with shared_state.data_lock:
            shared_state.camera_wb_temp = int(val)

    def update_hue_lower(val):
        with shared_state.data_lock:
            shared_state.hue_green_lower = float(val)

    def update_hue_upper(val):
        with shared_state.data_lock:
            shared_state.hue_green_upper = float(val)
            
    def update_gamma(val):
        with shared_state.data_lock:
            shared_state.camera_gamma = int(val)

    def update_denoise(val):
        with shared_state.data_lock:
            shared_state.camera_denoise = int(val)

    def update_backlight_comp(val):
        with shared_state.data_lock:
            shared_state.camera_backlight_comp = int(val)
            
    def update_flick_mode(val):
        with shared_state.data_lock:
            shared_state.camera_flick_mode = int(val)
            
    def toggle_auto_coalesce():
        with shared_state.data_lock:
            shared_state.auto_coalesce_enabled = not shared_state.auto_coalesce_enabled
            current_state = shared_state.auto_coalesce_enabled
        if current_state:
            btn_auto_coalesce.config(text="AUTO: ON", bg="#2ecc71", activebackground="#2ecc71")
        else:
            btn_auto_coalesce.config(text="AUTO: OFF", bg="#e74c3c", activebackground="#e74c3c")
            
    def toggle_auto_confidence():
        with shared_state.data_lock:
            shared_state.auto_confidence_enabled = not shared_state.auto_confidence_enabled
            current_state = shared_state.auto_confidence_enabled
        if current_state:
            btn_auto_confidence.config(text="AUTO: ON", bg="#2ecc71", activebackground="#2ecc71")
        else:
            btn_auto_confidence.config(text="AUTO: OFF", bg="#e74c3c", activebackground="#e74c3c")
            
    def toggle_auto_cam_gain():
        with shared_state.data_lock:
            shared_state.auto_cam_gain_enabled = not shared_state.auto_cam_gain_enabled
            current_state = shared_state.auto_cam_gain_enabled
        if current_state:
            btn_auto_cam_gain.config(text="AUTO: ON", bg="#2ecc71", activebackground="#2ecc71")
        else:
            btn_auto_cam_gain.config(text="AUTO: OFF", bg="#e74c3c", activebackground="#e74c3c")
            
    def toggle_auto_cam_settings():
        with shared_state.data_lock:
            # Flip the boolean state
            shared_state.auto_camera_settings_enabled = not shared_state.auto_camera_settings_enabled
            current_state = shared_state.auto_camera_settings_enabled
            
        if current_state:
            btn_auto_cam_settings.config(text="AUTO: ON", bg="#2ecc71", activebackground="#2ecc71")
            # Disable sliders so the user knows hardware has taken over
            gain_slider.config(state='disabled', fg="#444444")
            exp_time_slider.config(state='disabled', fg="#444444")
            wb_temp_slider.config(state='disabled', fg="#444444")
        else:
            btn_auto_cam_settings.config(text="AUTO: OFF", bg="#e74c3c", activebackground="#e74c3c")
            # Re-enable sliders for manual control
            gain_slider.config(state='normal', fg="#aaaaaa")
            exp_time_slider.config(state='normal', fg="#aaaaaa")
            wb_temp_slider.config(state='normal', fg="#aaaaaa")

    def toggle_optimise_exp_time():
        with shared_state.data_lock:
            shared_state.OPTIMISE_EXP_TIME_BY_COLOUR = not shared_state.OPTIMISE_EXP_TIME_BY_COLOUR
            current_state = shared_state.OPTIMISE_EXP_TIME_BY_COLOUR
        if current_state:
            btn_optimise_exp.config(text="AUTO: ON", bg="#2ecc71", activebackground="#2ecc71")
        else:
            btn_optimise_exp.config(text="AUTO: OFF", bg="#e74c3c", activebackground="#e74c3c")
            
    def toggle_screen_record():
        with shared_state.data_lock:
            shared_state.screen_record_enabled = not shared_state.screen_record_enabled
            current_state = shared_state.screen_record_enabled
        if current_state:
            btn_screen_record.config(text="REC: ON", bg="#2ecc71", activebackground="#2ecc71")
        else:
            btn_screen_record.config(text="REC: OFF", bg="#e74c3c", activebackground="#e74c3c")
            
    def toggle_raw_screen_record():
        with shared_state.data_lock:
            shared_state.raw_screen_record_enabled = not getattr(shared_state, 'raw_screen_record_enabled', False)
            current_state = shared_state.raw_screen_record_enabled
        if current_state:
            btn_raw_screen_record.config(text="RAW REC: ON", bg="#2ecc71", activebackground="#2ecc71")
        else:
            btn_raw_screen_record.config(text="RAW REC: OFF", bg="#e74c3c", activebackground="#e74c3c")
    # -----------------------------
            
    def on_auto_set_press(event):
        with shared_state.data_lock:
            shared_state.auto_camera_settings_enabled = True
        btn_auto_cam_settings.config(bg="#2ecc71", text="AUTO: ON")
        # Temporarily disable the sliders
        gain_slider.config(state='disabled')
        exp_time_slider.config(state='disabled')
        wb_temp_slider.config(state='disabled')

    def on_auto_set_release(event):
        with shared_state.data_lock:
            shared_state.auto_camera_settings_enabled = False
        btn_auto_cam_settings.config(bg="#e74c3c", text="AUTO: OFF")
        # Re-enable the sliders
        gain_slider.config(state='normal')
        exp_time_slider.config(state='normal')
        wb_temp_slider.config(state='normal')

    # --- Page Switching Logic ---
    def change_page(selection):
        page_telemetry.pack_forget()
        page_basic_cameras.pack_forget()
        page_cameras_graph.pack_forget()

        if selection == "Telemetry":
            page_telemetry.pack(expand=True, fill='both')
        elif selection == "Basic cameras":
            page_basic_cameras.pack(expand=True, fill='both')
        elif selection == "Cameras with graph":
            page_cameras_graph.pack(expand=True, fill='both')

    # --- UI Layout ---
    status_frame = tk.Frame(root, bg='#1a1a1a')
    status_frame.pack(fill='x', pady=5)

    lbl_status_mcu0 = tk.Label(status_frame, text="MCU0: DISCONNECTED", font=status_font, fg="#e74c3c", bg="#1a1a1a")
    lbl_status_mcu0.pack(side='left', padx=40)

    lbl_status_mcu1 = tk.Label(status_frame, text="MCU1: DISCONNECTED", font=status_font, fg="#e74c3c", bg="#1a1a1a")
    lbl_status_mcu1.pack(side='right', padx=40)

    # Top Navigation Frame ---
    nav_frame = tk.Frame(root, bg='#1a1a1a')
    nav_frame.pack(side='top', fill='x', pady=2, padx=20)

    # Dropdown menu for pages
    current_page_var = tk.StringVar(root)
    current_page_var.set("Telemetry") # Default page

    page_options = ["Telemetry", "Basic cameras", "Cameras with graph"]
    page_menu = tk.OptionMenu(nav_frame, current_page_var, *page_options, command=change_page)
    page_menu.config(font=button_font, bg="#f39c12", fg="white", activebackground="#f39c12", activeforeground="white", relief='flat', width=22)
    page_menu["menu"].config(font=status_font, bg="#1a1a1a", fg="white")
    page_menu.config(height=2)
    page_menu.pack(side='left', padx=15, expand=True)

    # Quit Button
    btn_quit = tk.Button(nav_frame, text="QUIT APP", font=button_font, bg="#444444", fg="white", activebackground="#444444", activeforeground="white", 
              command=quit_app, height=2, width=15, relief='flat')
    btn_quit.pack(side='left', padx=10, expand=True)

    # SEND DATA BUTTON ---
    btn_send_data = tk.Button(nav_frame, text="SEND DATA", font=button_font, bg="#2ecc71", fg="white", activebackground="#2ecc71", activeforeground="white", 
                              command=toggle_send_data, height=2, width=15, relief='flat')
    btn_send_data.pack(side='left', padx=10, expand=True)

    # Fullscreen Button
    btn_toggle = tk.Button(nav_frame, text="GO FULLSCREEN", font=button_font, bg="#2980b9", fg="white", activebackground="#2980b9", activeforeground="white", 
                           command=toggle_screen_mode, height=2, width=18, relief='flat')
    btn_toggle.pack(side='left', padx=10, expand=True)

    # Restart Button
    btn_restart = tk.Button(nav_frame, text="RESTART APP", font=button_font, bg="#8e44ad", fg="white", activebackground="#8e44ad", activeforeground="white", 
              command=restart_app, height=2, width=15, relief='flat')
    btn_restart.pack(side='left', padx=10, expand=True)

    # Shutdown Button
    btn_shutdown = tk.Button(nav_frame, text="SHUTDOWN", font=button_font, bg="#c0392b", fg="white", activebackground="#c0392b", activeforeground="white", 
              command=shutdown_jetson, height=2, width=15, relief='flat')
    btn_shutdown.pack(side='left', padx=10, expand=True)

    # --- Main Container for Pages ---
    main_container = tk.Frame(root, bg='#1a1a1a')
    main_container.pack(expand=True, fill='both', padx=20)

    # --- Pages ---
    page_telemetry = tk.Frame(main_container, bg='#1a1a1a')
    page_basic_cameras = tk.Frame(main_container, bg='#1a1a1a')
    page_cameras_graph = tk.Frame(main_container, bg='#1a1a1a')

    # Set default page to visible
    page_telemetry.pack(expand=True, fill='both')

    # --- Content for 'Basic cameras' Page ---
    # tk.Label(page_basic_cameras, text="Basic Cameras View", font=status_font, fg="#aaaaaa", bg="#1a1a1a").pack(pady=2)

    # --- Dual-Column Sliders Frame ---
    sliders_frame = tk.Frame(page_basic_cameras, bg="#1a1a1a")
    sliders_frame.pack(fill='x', padx=20, pady=2)

    # Left Column Frame
    left_slider_col = tk.Frame(sliders_frame, bg="#1a1a1a")
    left_slider_col.pack(side='left', expand=True, fill='both', padx=2)

    # Right Column Frame
    right_slider_col = tk.Frame(sliders_frame, bg="#1a1a1a")
    right_slider_col.pack(side='right', expand=True, fill='both', padx=2)

    # ==========================================
    # LEFT COLUMN: Original Sliders
    # ==========================================

    # Dynamic Saturation Slider
    sat_slider = tk.Scale(left_slider_col, from_=0, to=50, orient='horizontal', label="CAMERA SATURATION",
                         font=slider_font, fg="#aaaaaa", bg="#1a1a1a", troughcolor="#444444",
                         highlightthickness=0, command=update_saturation, sliderlength=80)
    sat_slider.set(shared_state.camera_saturation)
    sat_slider.pack(fill='x', pady=(0, 4))
    
    # Dynamic Gain Slider
    gain_slider = tk.Scale(left_slider_col, from_=0, to=255, orient='horizontal', label="CAMERA EXPOSURE GAIN",
                         font=slider_font, fg="#aaaaaa", bg="#1a1a1a", troughcolor="#444444",
                         highlightthickness=0, command=update_exposure_gain, sliderlength=80)
    gain_slider.set(shared_state.camera_exposure_gain)
    gain_slider.pack(fill='x', pady=(0, 4))
    
    # Dynamic Confidence Slider
    conf_slider = tk.Scale(left_slider_col, from_=0.0, to=1.0, resolution=0.01, orient='horizontal', 
                           label="YOLO CONFIDENCE THRESHOLD", font=slider_font, fg="#aaaaaa", bg="#1a1a1a", 
                           troughcolor="#444444", highlightthickness=0, command=update_confidence, sliderlength=80)
    conf_slider.set(shared_state.confidence_threshold)
    conf_slider.pack(fill='x', pady=(0, 4))
    
    # Dynamic Coalesce Distance Slider
    coalesce_slider = tk.Scale(left_slider_col, from_=0, to=1000, orient='horizontal', 
                               label="COALESCE DISTANCE THRESHOLD", font=slider_font, fg="#aaaaaa", bg="#1a1a1a", 
                               troughcolor="#444444", highlightthickness=0, command=update_coalesce_distance, sliderlength=80)
    coalesce_slider.set(shared_state.coalesce_distance_threshold)
    coalesce_slider.pack(fill='x', pady=(0, 4))
    
    # Expected Seedlings Slider Target
    target_plants_slider = tk.Scale(left_slider_col, from_=0, to=16, orient='horizontal', 
                               label="EXPECTED SEEDLINGS IN FRAME", font=slider_font, fg="#aaaaaa", bg="#1a1a1a", 
                               troughcolor="#444444", highlightthickness=0, command=update_expected_seedlings, sliderlength=80)
    target_plants_slider.set(shared_state.expected_seedlings_target)
    target_plants_slider.pack(fill='x', pady=(0, 4))
    
    # Dynamic Tunnel Vision Slider
    tunnel_vision_slider = tk.Scale(left_slider_col, from_=0, to=400, orient='horizontal', 
                               label="TUNNEL VISION LIMIT", font=slider_font, fg="#aaaaaa", bg="#1a1a1a", 
                               troughcolor="#444444", highlightthickness=0, command=update_tunnel_vision, sliderlength=80)
    tunnel_vision_slider.set(shared_state.tunnel_vision)
    tunnel_vision_slider.pack(fill='x', pady=(0, 4))
    
    # Dynamic backlight slider
    backlight_slider = tk.Scale(left_slider_col, from_=0, to=4, orient='horizontal', 
                               label="BACKLIGHT COMP", font=slider_font, fg="#aaaaaa", bg="#1a1a1a", 
                               troughcolor="#444444", highlightthickness=0, command=update_backlight_comp, sliderlength=80)
    backlight_slider.set(shared_state.camera_backlight_comp)
    backlight_slider.pack(fill='x', pady=(0, 4))

    # Dynamic flick slider
    flick_slider = tk.Scale(left_slider_col, from_=0, to=3, orient='horizontal', 
                           label="FLICKER MODE (0:Off, 1:50Hz, 2:60Hz, 3:Auto)", font=slider_font, fg="#aaaaaa", bg="#1a1a1a", 
                           troughcolor="#444444", highlightthickness=0, command=update_flick_mode, sliderlength=80)
    flick_slider.set(shared_state.camera_flick_mode)
    # flick_slider.pack(fill='x', pady=(0, 4))  # flisk slider currently not shown in GUI.

    # ==========================================
    # RIGHT COLUMN: New ISP Sliders
    # ==========================================

    # Dynamic Exposure Time Slider
    exp_time_slider = tk.Scale(right_slider_col, from_=1, to=100000, orient='horizontal', label="CAMERA EXPOSURE TIME",
                         font=slider_font, fg="#aaaaaa", bg="#1a1a1a", troughcolor="#444444",
                         highlightthickness=0, command=update_exposure_time, sliderlength=80)
    exp_time_slider.set(shared_state.camera_exposure_time)
    exp_time_slider.pack(fill='x', pady=(0, 4))

    # Dynamic Brightness Slider
    brightness_slider = tk.Scale(right_slider_col, from_=-10, to=10, orient='horizontal', label="CAMERA BRIGHTNESS",
                         font=slider_font, fg="#aaaaaa", bg="#1a1a1a", troughcolor="#444444",
                         highlightthickness=0, command=update_brightness, sliderlength=80)
    brightness_slider.set(shared_state.camera_brightness)
    brightness_slider.pack(fill='x', pady=(0, 4))

    # Dynamic Contrast Slider
    contrast_slider = tk.Scale(right_slider_col, from_=-50, to=50, orient='horizontal', label="CAMERA CONTRAST",
                         font=slider_font, fg="#aaaaaa", bg="#1a1a1a", troughcolor="#444444",
                         highlightthickness=0, command=update_contrast, sliderlength=80)
    contrast_slider.set(shared_state.camera_contrast)
    contrast_slider.pack(fill='x', pady=(0, 4))

    # Dynamic Sharpness Slider
    sharpness_slider = tk.Scale(right_slider_col, from_=-20, to=20, orient='horizontal', label="CAMERA SHARPNESS",
                         font=slider_font, fg="#aaaaaa", bg="#1a1a1a", troughcolor="#444444",
                         highlightthickness=0, command=update_sharpness, sliderlength=80)
    sharpness_slider.set(shared_state.camera_sharpness)
    sharpness_slider.pack(fill='x', pady=(0, 4))
    
    # Dynamic White Balance Temp Slider (Range: 2000K to 10000K)
    wb_temp_slider = tk.Scale(right_slider_col, from_=2000, to=10000, orient='horizontal', label="CAMERA WB TEMP (K)",
                         font=slider_font, fg="#aaaaaa", bg="#1a1a1a", troughcolor="#444444",
                         highlightthickness=0, command=update_wb_temp, sliderlength=80)
    wb_temp_slider.set(shared_state.camera_wb_temp)
    wb_temp_slider.pack(fill='x', pady=(0, 4))

    # Dynamic gamma slider
    gamma_slider = tk.Scale(right_slider_col, from_=4, to=79, orient='horizontal', 
                         label="CAMERA GAMMA (x10)", font=slider_font, fg="#aaaaaa", bg="#1a1a1a", 
                         troughcolor="#444444", highlightthickness=0, command=update_gamma, sliderlength=80)
    gamma_slider.set(shared_state.camera_gamma)
    gamma_slider.pack(fill='x', pady=(0, 4))

    # Dynamic denoise slider
    denoise_slider = tk.Scale(right_slider_col, from_=-2, to=2, orient='horizontal', label="CAMERA DENOISE",
                         font=slider_font, fg="#aaaaaa", bg="#1a1a1a", troughcolor="#444444",
                         highlightthickness=0, command=update_denoise, sliderlength=80)
    denoise_slider.set(shared_state.camera_denoise)
    denoise_slider.pack(fill='x', pady=(0, 4))




    # --- Video & LHS/RHS Controls Container ---
    video_and_controls_frame = tk.Frame(page_basic_cameras, bg="#1a1a1a")
    video_and_controls_frame.pack(expand=True, fill='both', pady=10)

    # --- LHS Hue Control Panel ---
    lhs_hue_frame = tk.Frame(video_and_controls_frame, bg="#1a1a1a", width=220,
                             highlightbackground="white", 
                             highlightcolor="white", 
                             highlightthickness=2)
    lhs_hue_frame.pack(side='left', fill='y', padx=5)
    lhs_hue_frame.pack_propagate(False)

    tk.Label(lhs_hue_frame, text="HUE MASK", font=status_font, fg="#aaaaaa", bg="#1a1a1a").pack(pady=(10, 5))
    
    hue_controls_container = tk.Frame(lhs_hue_frame, bg="#1a1a1a")
    hue_controls_container.pack(expand=True, fill='both')

    # Lower Hue Slider (Placed on the left)
    # Changed label text to 'L' to save horizontal space
    hue_lower_slider = tk.Scale(hue_controls_container, from_=1.0, to=0.0, resolution=0.001, orient='vertical',
                                label="L", font=slider_font, fg="#aaaaaa", bg="#1a1a1a", troughcolor="#444444",
                                highlightthickness=0, command=update_hue_lower)
    hue_lower_slider.set(shared_state.hue_green_lower)
    hue_lower_slider.pack(side='left', fill='y', padx=2)

    # Hue Visualizer Label (Sandwiched in the middle)
    lbl_hue_vis = tk.Label(hue_controls_container, bg="#000000")
    lbl_hue_vis.pack(side='left', fill='y', padx=4)

    # Upper Hue Slider (Placed on the right)
    # Changed label text to 'U' to save horizontal space
    hue_upper_slider = tk.Scale(hue_controls_container, from_=1.0, to=0.0, resolution=0.001, orient='vertical',
                                label="U", font=slider_font, fg="#aaaaaa", bg="#1a1a1a", troughcolor="#444444",
                                highlightthickness=0, command=update_hue_upper)
    hue_upper_slider.set(shared_state.hue_green_upper)
    hue_upper_slider.pack(side='left', fill='y', padx=2)

    # Label to hold the main video frames (Pushed left, next to Hue frame)
    video_label = tk.Label(video_and_controls_frame, bg="#000000")
    video_label.pack(side='left', expand=True, fill='both')

    # Combined RHS Wrapper Frame with White Border ---
    combined_rhs_frame = tk.Frame(video_and_controls_frame, bg="#1a1a1a",
                                  highlightbackground="white", 
                                  highlightcolor="white", 
                                  highlightthickness=2)
    combined_rhs_frame.pack(side='right', fill='y', padx=5)

    # Middle Control Panel (Placed on the left side INSIDE the wrapper)
    middle_control_frame = tk.Frame(combined_rhs_frame, bg="#1a1a1a", width=240)
    middle_control_frame.pack(side='left', fill='y', padx=5)
    middle_control_frame.pack_propagate(False)

    # RHS Control Panel (Placed on the right side INSIDE the wrapper)
    rhs_control_frame = tk.Frame(combined_rhs_frame, bg="#1a1a1a", width=180)
    rhs_control_frame.pack(side='left', fill='y', padx=5)
    rhs_control_frame.pack_propagate(False)

    ################################################################################################################################
    # --- The Screen Record Button ---
    tk.Label(middle_control_frame, text="VIDEO REC", font=status_font, fg="#aaaaaa", bg="#1a1a1a").pack(pady=(50, 5))
    btn_screen_record = tk.Button(middle_control_frame, text="REC: OFF", font=button_font, bg="#e74c3c", fg="white", 
                                  activebackground="#e74c3c", activeforeground="white", relief='flat',
                                  command=toggle_screen_record, height=2, width=13)
    btn_screen_record.pack()
    
    # The Raw Screen Record Button ---
    tk.Label(middle_control_frame, text="RAW VIDEO REC", font=status_font, fg="#aaaaaa", bg="#1a1a1a").pack(pady=(50, 5))
    btn_raw_screen_record = tk.Button(middle_control_frame, text="RAW REC: OFF", font=button_font, bg="#e74c3c", fg="white", 
                                  activebackground="#e74c3c", activeforeground="white", relief='flat',
                                  command=toggle_raw_screen_record, height=2, width=13)
    btn_raw_screen_record.pack(pady=(5, 0)) # Added padding to separate it slightly
    
    # --- ADD THE SIMULATE BUTTON
    tk.Label(middle_control_frame, text="SIMULATE", font=status_font, fg="#aaaaaa", bg="#1a1a1a").pack(pady=(50, 5))
    initial_sim_text = "SIMULATE: OFF" if shared_state.USE_CAMERA else "SIMULATE: ON"
    initial_sim_color = "#e74c3c" if shared_state.USE_CAMERA else "#2ecc71"
    btn_simulate = tk.Button(middle_control_frame, text=initial_sim_text, font=button_font, bg=initial_sim_color, fg="white", 
                                  activebackground=initial_sim_color, activeforeground="white", relief='flat',
                                  command=toggle_simulate_mode, height=2, width=13)
    btn_simulate.pack(pady=(5, 0))
    
    # --- ADD THE AUTO SET button:
    tk.Label(middle_control_frame, text="AUTO SET", font=status_font, fg="#aaaaaa", bg="#1a1a1a").pack(pady=(20, 5))
    btn_auto_cam_settings = tk.Button(middle_control_frame, text="AUTO: OFF", font=button_font, bg="#e74c3c", fg="white", 
                                      activebackground="#e74c3c", activeforeground="white", relief='flat',
                                      command=toggle_auto_cam_settings, height=2, width=13)
    btn_auto_cam_settings.pack()
    
    ################################################################################################################################

    # The Auto-Coalesce Button
    tk.Label(rhs_control_frame, text="COALESCE", font=status_font, fg="#aaaaaa", bg="#1a1a1a").pack(pady=(50, 5))
    btn_auto_coalesce = tk.Button(rhs_control_frame, text="AUTO: OFF", font=button_font, bg="#e74c3c", fg="white", 
                                  activebackground="#e74c3c", activeforeground="white", relief='flat',
                                  command=toggle_auto_coalesce, height=2, width=10)
    btn_auto_coalesce.pack()
    
    # The Auto-Confidence Button (Added)
    tk.Label(rhs_control_frame, text="CONF THRESH", font=status_font, fg="#aaaaaa", bg="#1a1a1a").pack(pady=(50, 5))
    btn_auto_confidence = tk.Button(rhs_control_frame, text="AUTO: OFF", font=button_font, bg="#e74c3c", fg="white", 
                                    activebackground="#e74c3c", activeforeground="white", relief='flat',
                                    command=toggle_auto_confidence, height=2, width=10)
    btn_auto_confidence.pack()
    
    # --- The Auto Camera Gain Button ---
    tk.Label(rhs_control_frame, text="CAM GAIN", font=status_font, fg="#aaaaaa", bg="#1a1a1a").pack(pady=(50, 5))
    btn_auto_cam_gain = tk.Button(rhs_control_frame, text="AUTO: OFF", font=button_font, bg="#e74c3c", fg="white", 
                                  activebackground="#e74c3c", activeforeground="white", relief='flat',
                                  command=toggle_auto_cam_gain, height=2, width=10)
    btn_auto_cam_gain.pack()
    
    # Average Confidence Display for Auto-Gain
    lbl_avg_conf_display = tk.Label(rhs_control_frame, text="Avg Conf: 0.00", font=slider_font, fg="#f1c40f", bg="#1a1a1a")
    lbl_avg_conf_display.pack(pady=(5, 0))

    # --- Content for 'Cameras with graph' Page ---
    # Modified with highlight attributes to create a thin white border
    graph_content_frame = tk.Frame(page_cameras_graph, bg="#1a1a1a",
                                   highlightbackground="white",
                                   highlightcolor="white",
                                   highlightthickness=1)
    graph_content_frame.pack(expand=True, fill='both', pady=10, padx=10)

    # Create a pure object-oriented Figure (safe for threads)
    # print("Attempting to produce figure:")
    fig = Figure(figsize=(6.0, 1.4), dpi=100, facecolor="#1a1a1a")
    fig.set_tight_layout(True) # Force the internal plot to fill all edge-to-edge space
    # print("Attempting to produce ax:")
    ax = fig.add_subplot(111)
    
    ax.set_facecolor("#111111")
    ax.tick_params(colors='white', labelsize=8)
    ax.grid(True, color='lightgray', linestyle='--')
    ax.set_ylabel("Time Delta (s)", color='white', fontsize=9)
    ax.set_xlabel("Time Since Start (Seconds)", color='white', fontsize=9)
    
    # --- ADD THIS LINE TO DISABLE THE SHIFTING OFFSET ---
    ax.ticklabel_format(useOffset=False, style='plain', axis='x')
    
    # Initialize blank plot lines
    line_green, = ax.plot([], [], color='green', linestyle='-', linewidth=1, label='Green Filtered')
    line_yolo, = ax.plot([], [], color='blue', linestyle='-', linewidth=1, label='YOLO Filtered')
    line_averaged, = ax.plot([], [], color='magenta', linestyle='-', linewidth=1, label='Averaged')
    line_predicted, = ax.plot([], [], color='red', linestyle='-', linewidth=1, label='Predicted', marker='o')
    line_light_bulb, = ax.plot([], [], color='yellow', label='Light Bulb Flash', linewidth=1, marker='o')
    
    # Initialize the legend in the correct 'upper left' position
    legend = ax.legend(loc='upper left', facecolor='#2c3e50', edgecolor='#7f8c8d', fontsize=8)
    for text in legend.get_texts():
        text.set_color('white')

    # print("Attempting to produce canvas:")
    canvas = FigureCanvasTkAgg(fig, master=graph_content_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side='top', expand=True, fill='both', pady=(0, 10))

    # Create a container frame to hold both the lightbulb and the video feed side-by-side
    # Added highlight attributes to create a clean, thin white border
    video_with_bulb_frame = tk.Frame(graph_content_frame, bg="#1a1a1a",
                                     highlightbackground="white",
                                     highlightcolor="white",
                                     highlightthickness=1)
    video_with_bulb_frame.pack(side='top', expand=True, fill='both', pady=(10, 0))

    # 1. Create a larger Lightbulb Canvas on the left (Scaled 6x: 80 * 6 = 480)
    # lightbulb_canvas = tk.Canvas(video_with_bulb_frame, width=48, height=48, bg="#1a1a1a", highlightthickness=0)
    # lightbulb_canvas.pack(side='left', padx=(20, 20))
    
    # Draw the larger circle (Coordinates scaled 6x: 10*6=60, 70*6=420)
    # bulb_id = lightbulb_canvas.create_oval(60, 60, 420, 420, fill="grey", outline="#444444", width=4)
    
    ##############################################################################################################################
    
    # Create a container frame for the Bulb and the Text
    bulb_container = tk.Frame(video_with_bulb_frame, bg="#1a1a1a")
    bulb_container.pack(side='left', padx=0, pady=10)
    
    # --- AUTO WEED BUTTON ---
    btn_auto_weed = tk.Button(bulb_container, text="AUTO WEED: OFF", font=button_font, bg="#e74c3c", fg="white", 
                                  activebackground="#e74c3c", activeforeground="white", relief='flat',
                                  command=toggle_auto_weed, height=2, width=15)
    btn_auto_weed.pack(side='top', pady=(0, 10))

    # Create the unique Canvas just for the Light Bulb indicator
    bulb_canvas = tk.Canvas(bulb_container, width=500, height=500, bg="#1a1a1a", highlightthickness=0)
    bulb_canvas.pack(side='top')
    
    # Create the Label to display the Expected Time Delta
    lbl_expected_delta = tk.Label(bulb_container, text="Expected Time Delta = 0.000 seconds", font=status_font, fg="white", bg="#1a1a1a")
    lbl_expected_delta.pack(side='top', pady=(5, 0))
    
    # --- Cosmetic Decoration: Bayonet Mounting ---
    # Metallic gray main cap
    bulb_canvas.create_rectangle(240, 372, 360, 468, fill="#95a5a6", outline="#7f8c8d", width=6, tags="bulb_base")
    # Left Bayonet Pin
    bulb_canvas.create_rectangle(216, 408, 240, 432, fill="#7f8c8d", outline="#7f8c8d", tags="bulb_base")
    # Right Bayonet Pin
    bulb_canvas.create_rectangle(360, 408, 384, 432, fill="#7f8c8d", outline="#7f8c8d", tags="bulb_base")
    # Black insulation contact point at the very bottom
    bulb_canvas.create_polygon(258, 468, 342, 468, 318, 492, 282, 492, fill="#2c3e50", outline="#2c3e50", tags="bulb_base")



    # --- Cosmetic Decoration: The Glass Bulb ---
    bulb_canvas.create_oval(150, 90, 450, 390, fill="grey", outline="#7f8c8d", width=12, tags="bulb_glass")

    # --- Cosmetic Decoration: Curly Filament ---
    filament_points = [
        264, 276,  # Left anchor point
        276, 228,  # First loop up
        288, 264,  # Dip down
        300, 204,  # Center high curl
        312, 264,  # Dip down
        324, 228,  # Right loop up
        336, 276   # Right anchor point
    ]

    # The thin white curly filament
    bulb_canvas.create_line(filament_points, fill="#555555", width=4, smooth=True, splinesteps=16, tags="bulb_filament")
    
    # --- Cosmetic Decoration: Support Wires (Extended by 10%) ---
    # Left angled support wire (thicker, grey, never illuminated)
    # Extended 10% past the base: X1 shifts from 276 to 277, Y1 shifts from 372 to 381
    # X2, Y2 remains locked at (264, 276) to meet the LEFT anchor of the filament
    bulb_canvas.create_line(277, 381, 264, 276, fill="#7f8c8d", width=6, tags="bulb_internal")

    # Right angled support wire (thicker, grey, never illuminated)
    # Extended 10% past the base: X1 shifts from 324 to 323, Y1 shifts from 372 to 381
    # X2, Y2 remains locked at (336, 276) to meet the RIGHT anchor of the filament
    bulb_canvas.create_line(323, 381, 336, 276, fill="#7f8c8d", width=6, tags="bulb_internal")
    
    #################################################################################################################################

    # 2. Pack the video label on the right
    video_label_graph = tk.Label(video_with_bulb_frame, bg="#000000")
    video_label_graph.pack(side='left', expand=True, fill='both')
    
    # Helper function to turn the bulb back off
    def reset_lightbulb():
        # lightbulb_canvas.itemconfig(bulb_id, fill="grey", outline="#444444")
        # Dim the filament to a dark unlit gray when off
        bulb_canvas.itemconfig("bulb_filament", fill="#555555", width=6)
        # Turn the small glass bulb grey
        bulb_canvas.itemconfig("bulb_glass", fill="grey")
    
    # --- The Auto Exposure Time Button ---
    tk.Label(rhs_control_frame, text="EXP TIME", font=status_font, fg="#aaaaaa", bg="#1a1a1a").pack(pady=(20, 5))
    btn_optimise_exp = tk.Button(rhs_control_frame, text="AUTO: OFF", font=button_font, bg="#e74c3c", fg="white", 
                                  activebackground="#e74c3c", activeforeground="white", relief='flat',
                                  command=toggle_optimise_exp_time, height=2, width=10)
    btn_optimise_exp.pack()

    # --- Content for 'Telemetry' Page ---
    # LEFT COLUMN (Now packed inside page_telemetry)
    col_left = tk.Frame(page_telemetry, bg='#1a1a1a', width=1100)
    col_left.pack_propagate(False)  # Stops the frame from resizing to fit its contents
    col_left.pack(side='left', fill='y')  # Fills available height ('y'), but respects fixed width

    # RIGHT COLUMN (Now packed inside page_telemetry)
    col_right = tk.Frame(page_telemetry, bg='#1a1a1a')
    col_right.pack(side='right', expand=True, fill='both')
    
    def create_block(parent, title, color="#00FF00", font_type="large"):
        block_frame = tk.Frame(parent, bg='#1a1a1a', highlightbackground="#444444", highlightthickness=2)
        block_frame.pack(pady=5, padx=10, fill='x')
        tk.Label(block_frame, text=title, font=header_font, fg="#aaaaaa", bg="#1a1a1a").pack(pady=(5, 0))
        use_font = data_font if font_type == "large" else small_data_font
        label = tk.Label(block_frame, text="---", font=use_font, fg=color, bg="#1a1a1a")
        label.pack(pady=(0, 5))
        return label

    # Left Column Blocks
    lbl_actual = create_block(col_left, "ACTUAL GPS", "#00FF00")
    lbl_desired = create_block(col_left, "DESIRED WP", "#3498db")
    lbl_dist = create_block(col_left, "DISTANCE TO GO (m)", "#f1c40f")
    lbl_wp_count = create_block(col_left, "WAYPOINTS LEFT", "#e74c3c")

    # Sliders Frame
    slider_frame = tk.Frame(col_left, bg='#1a1a1a', highlightbackground="#444444", highlightthickness=2)
    slider_frame.pack(pady=5, padx=10, fill='x')

    tk.Label(slider_frame, text="IMPLEMENT SETTINGS", font=header_font, fg="#aaaaaa", bg="#1a1a1a").pack(pady=(5, 0))

    slider1 = tk.Scale(slider_frame, from_=0, to=500, orient='horizontal', label="SLIDER 1",
                       font=slider_font, fg="#aaaaaa", bg="#1a1a1a", troughcolor="#444444",
                       highlightthickness=0, command=update_slider1,
                       sliderlength=80, width=50)
    slider1.set(shared_state.slider_1_val)
    slider1.pack(fill='x', padx=15, pady=(5, 15))

    slider2 = tk.Scale(slider_frame, from_=0, to=500, orient='horizontal', label="SLIDER 2",
                       font=slider_font, fg="#aaaaaa", bg="#1a1a1a", troughcolor="#444444",
                       highlightthickness=0, command=update_slider2,
                       sliderlength=80, width=50)
    slider2.set(shared_state.slider_2_val)
    slider2.pack(fill='x', padx=15, pady=(0, 15))

    # Right Column Blocks
    lbl_heading = create_block(col_right, "HEADING (deg)", "#9b59b6", "small")
    lbl_speed = create_block(col_right, "GPS SPEED (m/s)", "#1abc9c", "small")
    lbl_accuracy = create_block(col_right, "ACCURACY (mm)", "#ecf0f1", "small")
    lbl_rel_pos_acc = create_block(col_right, "REL POS ACC (mm)", "#ecf0f1", "small")
    lbl_carrier = create_block(col_right, "CARRIER SOL", "#e67e22", "small")

    throt_frame = tk.Frame(col_right, bg='#1a1a1a')
    throt_frame.pack(side='top', fill='x', pady=0)
    
    enc_frame = tk.Frame(col_right, bg='#1a1a1a')
    enc_frame.pack(side='top', fill='x', pady=0)

    frame_a = tk.Frame(throt_frame, bg='#1a1a1a')
    frame_a.pack(side='left', expand=True, fill='both', padx=0)
    lbl_throt_a = create_block(frame_a, "  THROT A  ", "#f39c12", "small")

    frame_b = tk.Frame(throt_frame, bg='#1a1a1a')
    frame_b.pack(side='left', expand=True, fill='both', padx=0)
    lbl_throt_b = create_block(frame_b, "  THROT B  ", "#f39c12", "small")
    
    frame_c = tk.Frame(enc_frame, bg='#1a1a1a')
    frame_c.pack(side='left', expand=True, fill='both', padx=0)
    lbl_wheel_encoder = create_block(frame_c, " WHEEL ENC ", "#e74c3c", "small")
    
    frame_d = tk.Frame(enc_frame, bg='#1a1a1a')
    frame_d.pack(side='left', expand=True, fill='both', padx=0)
    lbl_horiz_act_encoder = create_block(frame_d, " HORIZ ENC ", "#e74c3c", "small")
    
    frame_e = tk.Frame(enc_frame, bg='#1a1a1a')
    frame_e.pack(side='left', expand=True, fill='both', padx=0)
    lbl_drawbar_act_encoder = create_block(frame_e, " DRAWBAR ENC ", "#e74c3c", "small")

    # --- Main GUI Loop Updates ---
    def update_gui():
        with shared_state.data_lock:
            lbl_actual.config(text=f"{shared_state.act_lat:.8f}, {shared_state.act_lon:.8f}")
            lbl_desired.config(text=f"{shared_state.des_lat:.8f}, {shared_state.des_lon:.8f}")
            lbl_dist.config(text=f"{shared_state.distance_to_go:.4f} m")
            rem = max(0, len(shared_state.waypointsArray) - shared_state.current_waypoint_index)
            lbl_wp_count.config(text=f"{rem} / {len(shared_state.waypointsArray)}")

            lbl_heading.config(text=f"{shared_state.act_heading:.2f}°")
            lbl_speed.config(text=f"{shared_state.gps_speed:.5f}")
            lbl_accuracy.config(text=f"{shared_state.accuracyMM}")
            lbl_rel_pos_acc.config(text=f"{shared_state.rel_pos_acc:.2f}")
            lbl_carrier.config(text=shared_state.carrierSolutionType)
            lbl_throt_a.config(text=str(shared_state.act_throtA_val))
            lbl_throt_b.config(text=str(shared_state.act_throtB_val))
            lbl_wheel_encoder.config(text=str(shared_state.encImplWheelVal))
            lbl_horiz_act_encoder.config(text=str(shared_state.encHorizActVal))
            lbl_drawbar_act_encoder.config(text=str(shared_state.encDrawbarActVal))

            lbl_status_mcu0.config(text="MCU0: CONNECTED" if shared_state.MCU0_alive else "MCU0: LOST",
                                   fg="#2ecc71" if shared_state.MCU0_alive else "#e74c3c")
            lbl_status_mcu1.config(text="MCU1: CONNECTED" if shared_state.MCU1_alive else "MCU1: LOST",
                                   fg="#2ecc71" if shared_state.MCU1_alive else "#e74c3c")
                                   

            current_coalesce = shared_state.coalesce_distance_threshold
            is_auto_on = shared_state.auto_coalesce_enabled
            if is_auto_on:
                coalesce_slider.set(current_coalesce)

            current_conf = shared_state.confidence_threshold
            is_auto_conf_on = shared_state.auto_confidence_enabled
            if is_auto_conf_on:
                conf_slider.set(current_conf)
                
            current_gain = shared_state.camera_exposure_gain
            is_auto_gain_on = shared_state.auto_cam_gain_enabled
            if is_auto_gain_on:
                gain_slider.set(current_gain)
            # Update the Average Confidence Label
            lbl_avg_conf_display.config(text=f"Avg Conf: {shared_state.avg_detection_confidence:.2f}")
            
            current_exp = shared_state.camera_exposure_time
            is_auto_exp_on = shared_state.OPTIMISE_EXP_TIME_BY_COLOUR
            if is_auto_exp_on:
                exp_time_slider.set(current_exp)

            # Update the Video Feed Label:
            if shared_state.latest_frame is not None:
                import numpy as np
                
                # 1. Convert the PIL Image to an OpenCV-compatible NumPy array
                cv_img = np.array(shared_state.latest_frame)
                height, width, _ = cv_img.shape
                
                # 2. Use cv2 to draw a white square around the outer boundary
                # (255, 255, 255) represents white in RGB color space; thickness is 5
                cv2.rectangle(cv_img, (0, 0), (width - 1, height - 1), (255, 255, 255), 5)
                
                # 3. Convert back to a PIL Image for Tkinter compatibility
                bordered_frame = Image.fromarray(cv_img)
                
                # Create the PhotoImage on the MAIN thread
                tk_image = ImageTk.PhotoImage(image=bordered_frame)
                
                # Update the label on the 'Basic cameras' page
                video_label.config(image=tk_image)
                video_label.image = tk_image
                
                # Update the new label on the 'Cameras with graph' page
                video_label_graph.config(image=tk_image)
                video_label_graph.image = tk_image
                
                # --- Update the Hue Visualizer Strip ---
                # Create a 300x30 base image
                vis_height = 300
                vis_width = 30
                hue_gradient = np.zeros((vis_height, vis_width, 3), dtype=np.uint8)
            
                # Generate the vertical spectrum (0-179, inverted so 179 is top)
                for y in range(vis_height):
                    h = int((1.0 - (y / vis_height)) * 179)
                    hue_gradient[y, :, 0] = h    # Hue
                    hue_gradient[y, :, 1] = 255  # Sat
                    hue_gradient[y, :, 2] = 255  # Val
                
                # Apply the current mask bounds
                lower_bound = np.array([shared_state.hue_green_lower * 179, 50, 50])
                upper_bound = np.array([shared_state.hue_green_upper * 179, 255, 255])
            
                # Filter and convert to RGB for Tkinter
                vis_mask = cv2.inRange(hue_gradient, lower_bound, upper_bound)
                vis_filtered = cv2.bitwise_and(hue_gradient, hue_gradient, mask=vis_mask)
                vis_rgb = cv2.cvtColor(vis_filtered, cv2.COLOR_HSV2RGB)
            
                vis_img_pil = Image.fromarray(vis_rgb)
                tk_vis_img = ImageTk.PhotoImage(image=vis_img_pil)
            
                lbl_hue_vis.config(image=tk_vis_img)
                lbl_hue_vis.image = tk_vis_img # Keep reference to avoid garbage collection
                

        # --- ADD THIS LIGHTBULB LOGIC ---
        with shared_state.data_lock:
            # --- UPDATE THE TEXT DYNAMICALLY ---
            lbl_expected_delta.config(text=f"Expected Time Delta = {shared_state.expected_time_delta_val:.3f} seconds")
            # Check if the vision thread triggered a yellow flash
            if getattr(shared_state, 'yellow_flash_event', False):
                # Illuminate the bulb yellow
                # lightbulb_canvas.itemconfig(bulb_id, fill="#f1c40f", outline="#ffffff")
                # Make the filament glow white/yellow when turned on
                bulb_canvas.itemconfig("bulb_filament", fill="#ffffff", width=9)
                # Illuminate the small glass bulb
                bulb_canvas.itemconfig("bulb_glass", fill="#f1c40f")
                # Reset the flag so it doesn't trigger continuously
                shared_state.yellow_flash_event = False
                # Schedule the bulb to turn back to grey after 1000ms (1 second)
                root.after(1000, reset_lightbulb)

        # --- Live Graph Animation Engine ---
        with shared_state.data_lock:
            # Safely grab the lists of (timestamp, delta) tuples
            data_green = list(shared_state.graph_green_filtered)
            data_yolo = list(shared_state.graph_yolo_filtered)
            data_avg = list(shared_state.graph_averaged)
            data_pred = list(shared_state.graph_predicted)
            data_flash = list(shared_state.graph_light_bulb_flash)

        # Unpack tuples into separate X (epoch time) and Y (delta) arrays
        x_green, y_green = zip(*data_green) if data_green else ([], [])
        x_yolo, y_yolo = zip(*data_yolo) if data_yolo else ([], [])
        x_avg, y_avg = zip(*data_avg) if data_avg else ([], [])
        x_pred, y_pred = zip(*data_pred) if data_pred else ([], [])
        x_flash, y_flash = zip(*data_flash) if data_flash else ([], [])

        # Update artists
        line_green.set_data(x_green, y_green)
        line_yolo.set_data(x_yolo, y_yolo)
        line_averaged.set_data(x_avg, y_avg)
        line_predicted.set_data(x_pred, y_pred)
        line_light_bulb.set_data(x_flash, y_flash)

        # Dynamically scale limits based on actual epoch times (matches original logic)
        all_x = list(x_green) + list(x_yolo) + list(x_avg) + list(x_pred) + list(x_flash)
        all_y = list(y_green) + list(y_yolo) + list(y_avg) + list(y_pred) + list(y_flash)

        if all_x and all_y:
            x_min, x_max = min(all_x), max(all_x)
            y_min, y_max = min(all_y), max(all_y)
            
            # Add a small buffer to the limits
            ax.set_xlim(x_min - 0.1, x_max + 0.1)
            ax.set_ylim(y_min - 0.1, y_max + 0.1)
            
            # FORCE LEGEND POSITION HERE ON EVERY REDRAW
            # ax.legend(loc='upper left', facecolor='#2c3e50', edgecolor='#7f8c8d', labelcolor='white')
            
            # Trigger a GUI redraw
            canvas.draw_idle()

        root.after(200, update_gui)

    # Start the loops

    update_gui()
    root.mainloop()
