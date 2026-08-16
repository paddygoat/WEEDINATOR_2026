# Do not ever remove the next 3 lines:
'''
cd && source python_env_01/bin/activate &&
cd /home/nano/Documents/WEEDINATOR/Code/Jetson_nano && python3 plot_loop_speed_data.py

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

def plot_all_metrics(file_path):
    # Load the data
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    
    # Remove the first ten datasets (rows)
    df = df.iloc[20:]

    # Identify all columns to plot (everything except the X-axis column)
    metrics_to_plot = [col for col in df.columns if col != 'elapsed_time_sec']

    # Create the figure with a slightly wider layout to fit the legend
    plt.figure(figsize=(14, 8))

    # Use a colormap with 20 distinct colors
    cmap = plt.get_cmap('tab20')

    # Plot each metric against elapsed_time_sec
    for i, col in enumerate(metrics_to_plot):
        plt.plot(
            df['elapsed_time_sec'], 
            df[col], 
            linestyle='-', 
            marker='', 
            color=cmap(i % 20), 
            label=col
        )

    # Add labels and title
    plt.xlabel('Elapsed Time (sec)')
    plt.ylabel('Metric Values (Log Scale)')
    plt.title('All Metrics Over Elapsed Time')
    
    # Use a logarithmic scale to handle the huge range of values
    # plt.yscale('log')
    
    # Add a grid for easier reading
    plt.grid(True, which="both", linestyle="--", alpha=0.6)

    # Place the legend just outside the right edge of the plot
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)

    # Ensure everything fits without getting cut off
    plt.tight_layout()

    # Save the plot
    plt.savefig('all_metrics_plot.png')
    
    plt.show()

if __name__ == "__main__":
    plot_all_metrics('loop_speed_data.txt')
