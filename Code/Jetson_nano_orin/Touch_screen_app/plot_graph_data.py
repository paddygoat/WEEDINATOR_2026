
'''
cd /home/rat/Documents/WEEDINATOR/Code/Jetson_nano && python3 plot_graph_data.py
'''

import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

FILE_PATH = '/home/rat/Downloads/graph_data.txt'

def main():
    # 1. Load and parse the JSON data
    try:
        with open(FILE_PATH, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Error: The file {FILE_PATH} was not found.")
        return

    # Helper function to unpack [x, y] coordinates
    def get_xy(dataset_name):
        dataset = data.get(dataset_name, [])
        x = [point[0] for point in dataset]
        y = [point[1] for point in dataset]
        return x, y

    # Extract coordinates for each line
    green_x, green_y = get_xy("GREEN_TIME_DELTA_ARRAY_FILTERED")
    yolo_x, yolo_y = get_xy("YOLO_TIME_DELTA_ARRAY_FILTERED")
    avg_x, avg_y = get_xy("AVERAGED_TIME_DELTA_ARRAY")
    pred_x, pred_y = get_xy("PREDICTED_TIME_DELTA_ARRAY")
    light_x, light_y = get_xy("LIGHT_BULB_FLASH_DELTA_ARRAY")

    # 2. Setup the Plot using the provided Style Guide
    fig = Figure(figsize=(20, 5), dpi=100, facecolor="#1a1a1a")
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
    
    # Populate the initialized plot lines with data. 
    # Adjusted to linestyle='none' and added markers to create a true scatter plot effect.
    line_green, = ax.plot(green_x, green_y, color='green', linestyle='-', linewidth=1, label='Green Filtered')
    line_yolo, = ax.plot(yolo_x, yolo_y, color='blue', linestyle='-', linewidth=1, label='YOLO Filtered')
    line_averaged, = ax.plot(avg_x, avg_y, color='magenta', linestyle='-', linewidth=1, marker='o', markersize=3, label='Averaged')
    line_predicted, = ax.plot(pred_x, pred_y, color='red', linestyle='-', linewidth=1, marker='o', markersize=3, label='Predicted')
    
    # Keeping the lightbulb flash as an empty initialization for your legend
    line_light_bulb, = ax.plot([light_x], [light_y], color='yellow', label='Light Bulb Flash', linewidth=1, marker='o', linestyle='-', markersize=3)
    
    # Initialize the legend in the correct 'upper left' position
    legend = ax.legend(loc='upper left', facecolor='#2c3e50', edgecolor='#7f8c8d', fontsize=8)
    for text in legend.get_texts():
        text.set_color('white')

    # 3. Save the figure (since we are using matplotlib.figure.Figure standalone)
    canvas = FigureCanvas(fig)
    output_filename = "scatter_plot_output.png"
    canvas.print_figure(output_filename)
    print(f"Success! Plot saved as {output_filename}")

if __name__ == "__main__":
    main()
