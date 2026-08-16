# plot_analysis_data.py
'''
cd && source python_env_01/bin/activate &&
cd /home/nano/Documents/WEEDINATOR/Code/Jetson_nano && python3 plot_analysis_data.py
'''
import os
import pandas as pd
import matplotlib.pyplot as plt

# File path to analysis data
DATA_FILE_PATH = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/data_for_analysis.txt"

def main():
    if not os.path.exists(DATA_FILE_PATH):
        print(f"[Error] File not found: {DATA_FILE_PATH}")
        return

    # Read data from the CSV file
    df = pd.read_csv(DATA_FILE_PATH)

    # Ensure x-axis column exists
    if 'elapsed_app_time' not in df.columns:
        print("[Error] 'elapsed_app_time' column missing from data file.")
        return

    x = df['elapsed_app_time']
    y_columns = [col for col in df.columns if col != 'elapsed_app_time']

    # Set up subplots for each metric (so differing scale ranges don't compress each line)
    fig, axes = plt.subplots(nrows=len(y_columns), ncols=1, figsize=(12, 2.5 * len(y_columns)), sharex=True)

    if len(y_columns) == 1:
        axes = [axes]

    # Plot each metric against elapsed_app_time with lines and no markers
    for ax, col_name in zip(axes, y_columns):
        ax.plot(x, df[col_name], label=col_name, linestyle='-', marker='', linewidth=1.5)
        ax.set_ylabel(col_name)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(loc='upper right')

    axes[-1].set_xlabel('elapsed_app_time (s)')
    fig.suptitle('Telemetry & Loop Analysis Data', fontsize=14, fontweight='bold')

    plt.tight_layout()
    
    # Save the plot image next to the data file
    output_plot_path = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/analysis_plot.png"
    plt.savefig(output_plot_path, dpi=300)
    print(f"[Success] Plot saved to: {output_plot_path}")

    # Display window
    plt.show()

if __name__ == "__main__":
    main()
