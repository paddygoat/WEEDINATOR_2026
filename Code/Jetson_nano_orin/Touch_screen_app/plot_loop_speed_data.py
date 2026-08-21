# Do not ever remove the next 3 lines:
'''
cd && source python_env_01/bin/activate &&
cd /home/nano/Documents/WEEDINATOR/Code/Jetson_nano && python3 plot_loop_speed_data.py

cd /home/rat/Documents/WEEDINATOR/python_environments && source my_venv_01/bin/activate &&
cd /home/rat/Downloads && python3 plot_loop_speed_data.py

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

# X-axis limits
MIN_X_AXIS_VALUE = 0
MAX_X_AXIS_VALUE = 2000

def plot_all_metrics(file_path):
    # Load the data
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    
    # Remove the first 20 rows
    df = df.iloc[20:]

    # Identify all columns to plot
    metrics_to_plot = [col for col in df.columns if col != 'elapsed_time_sec']

    # Create the figure
    plt.figure(figsize=(14, 8))
    # plt.figure(figsize=(28, 16))

    # Use a colormap for other lines
    cmap = plt.get_cmap('tab20')

    # Plot each metric against elapsed_time_sec
    for i, col in enumerate(metrics_to_plot):
        
        # Default styling for standard metrics
        line_color = cmap(i % 20)
        line_width = 1.0
        z_order = 1
        line_style = '-'

        # Override strictly for TIME_C
        if col == 'TIME_C':
            line_color = '#FF0000'  # Pure Hex Red
            line_width = 1.0
            z_order = 10            # Top layer
            line_style = '--'       # Dashed
            print(f"--> Overriding {col}: Color set to {line_color}")
            
        # Override strictly for TIME_C
        if col == 'GPU':
            line_color = '#000000'  # Pure Hex Black
            line_width = 1.0
            z_order = 10            # Top layer
            line_style = '--'       # Dashed
            print(f"--> Overriding {col}: Color set to {line_color}")

        plt.plot(
            df['elapsed_time_sec'], 
            df[col], 
            linestyle=line_style, 
            marker='', 
            color=line_color, 
            linewidth=line_width,
            zorder=z_order,
            label=col
        )

    # Add labels and title
    plt.xlabel('Elapsed Time (sec)')
    plt.ylabel('Metric Values')
    plt.title('All Metrics Over Elapsed Time')
    
    # Uncomment if you want log scale
    # plt.yscale('log')
    
    # Add a grid
    plt.grid(True, which="both", linestyle="--", alpha=0.6)

    # Place the legend outside the plot
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)

    # Apply the X-axis limits
    plt.xlim(MIN_X_AXIS_VALUE, MAX_X_AXIS_VALUE)

    # Ensure everything fits
    plt.tight_layout()

    # Save and show
    plt.savefig('all_metrics_plot.png')
    plt.show()

if __name__ == "__main__":
    plot_all_metrics('loop_speed_data.txt')
