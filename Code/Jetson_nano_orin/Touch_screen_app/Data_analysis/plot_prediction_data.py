# Do not ever remove the next 3 lines:
'''
cd && source python_env_01/bin/activate &&
cd /home/nano/Documents/WEEDINATOR/Code/Jetson_nano && python3 plot_prediction_data.py

cd /home/rat/Documents/WEEDINATOR/python_environments && source my_venv_01/bin/activate &&
cd /home/rat/Downloads && python3 plot_prediction_data.py

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

import pandas as pd
import matplotlib.pyplot as plt

# Configuration Variables
file_path = "prediction_data.txt"
GPS_SPEED_DATA_DISPLAY_FACTOR = 100  # Arbitrary multiplier for gps_speed data

def plot_weedinator_data():
    try:
        # Load the CSV data into a pandas DataFrame
        df = pd.read_csv(file_path)
        
        # Define a color dictionary to match your live GUI colors
        color_map = {
            'green': 'green',
            'yolo': 'blue',
            'avg': 'magenta',
            'pred': 'red',
            'flash': 'yellow',
            'gps_speed': 'cyan'
        }

        # Create the plot figure
        plt.figure(figsize=(10, 6))

        # Group the data by 'data_type' so we can plot them as separate series
        for data_type, group in df.groupby('data_type'):
            
            # Fetch the assigned color, default to black if it's an unknown type
            line_color = color_map.get(data_type, 'black')
            
            # SORT the group by epoch_time so the lines draw sequentially left to right
            group = group.sort_values(by='epoch_time')
            
            # Conditionally set the marker: No marker for gps_speed, 'o' for everything else
            current_marker = None if data_type == 'gps_speed' else 'o'
            
            # Apply the display factor to gps_speed data
            y_values = group['delta']
            if data_type == 'gps_speed':
                y_values = y_values * GPS_SPEED_DATA_DISPLAY_FACTOR
            
            # Create the line plot with modified Y values and conditional markers
            plt.plot(group['epoch_time'], y_values, 
                     color=line_color, label=data_type, 
                     marker=current_marker, alpha=0.8, markeredgecolor='k', 
                     markersize=8, linestyle='-', linewidth=2)

        # Formatting and styling the graph
        plt.title('Weedinator Time Delta Analysis', fontsize=14, fontweight='bold')
        plt.xlabel('Epoch Time (Seconds)', fontsize=12)
        plt.ylabel('Time Delta / Value', fontsize=12)
        
        # Disable the scientific notation/offset on the x-axis for raw epoch time
        plt.ticklabel_format(useOffset=False, style='plain', axis='x')
        
        # Add a grid and a legend (Moved to top-left corner)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(title='Data Source', loc='upper left')
        plt.tight_layout()

        # Display the graph window
        plt.show()

    except FileNotFoundError:
        print(f"Error: Could not find '{file_path}'.")
        print("Please ensure the script is in the same directory as your data file, or update the file_path variable.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    plot_weedinator_data()
