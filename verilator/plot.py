import pandas as pd
import matplotlib.pyplot as plt

def plot_dac_output(csv_filepath):
    """
    Reads a CSV file and plots 'aout_active' vs 'time_ps' and
    'expected_out' vs 'time_ps' on two separate subplots.

    Args:
        csv_filepath (str): The path to the CSV file.
    """
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_filepath)

        # Create two subplots, sharing the x-axis
        fig, axs = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        
        # Add a main title for the entire figure
        fig.suptitle('DAC Output Comparison', fontsize=16)

        axs[0].plot(df['time_ps'], df['aout_active'], label='aout_active', color='blue')
        axs[0].set_title('Actual DAC Output (aout_active) vs. Time')
        axs[0].set_ylabel('Aout Active (V)')
        axs[0].legend()
        axs[0].grid(True)
        
        axs[1].plot(df['time_ps'], df['expected_out'], label='expected_out', color='green')
        axs[1].set_title('Expected DAC Output (expected_out) vs. Time')
        axs[1].set_xlabel('Time (ps)')
        axs[1].set_ylabel('Expected Out (V)')
        axs[1].legend()
        axs[1].grid(True)
        

        plt.tight_layout(rect=[0, 0.03, 1, 0.95]) 

        print(f"Successfully loaded '{csv_filepath}'. Displaying plots...")
        plt.show()

    except FileNotFoundError:
        print(f"Error: The file '{csv_filepath}' was not found.")
    except KeyError as e:
        print(f"Error: Column {e} not found in the CSV file. Please check the column names (requires 'time_ps', 'aout_active', 'expected_out').")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    plot_dac_output('top_dac.csv')
