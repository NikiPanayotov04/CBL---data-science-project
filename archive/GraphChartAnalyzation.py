import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# Path to your root directory (adjust this)
root_dir = 'data\crime 2022-2025'

# Store monthly burglary counts
monthly_burglary_counts = []

# Loop through all monthly folders
for folder in os.listdir(root_dir):
    folder_path = os.path.join(root_dir, folder)
    
    if os.path.isdir(folder_path):
        # Construct expected filename
        csv_filename1 = f"{folder}-city-of-london-street.csv"
        csv_filename2 = f"{folder}-metropolitan-street.csv"
        csv_path1 = os.path.join(folder_path, csv_filename1)
        csv_path2 = os.path.join(folder_path, csv_filename2)
        if os.path.isfile(csv_path1) or os.path.isfile(csv_path2):
            try:
                df = pd.read_csv(csv_path1)
                
                # Filter where Crime type is 'Burglary'
                burglary_df = df[df['Crime type'] == 'Burglary']
                
                # Count the rows
                count = len(burglary_df)
                
                # Store result
                monthly_burglary_counts.append({'Month': folder, 'Burglary Count': count})
            
            except Exception as e:
                print(f"Error processing {csv_path1}: {e}")

# Create DataFrame
burglary_df = pd.DataFrame(monthly_burglary_counts)
burglary_df = burglary_df.sort_values('Month')

# Plot the burglary trend
burglary_df['Month'] = pd.to_datetime(burglary_df['Month'], format='%Y-%m')

# Plot
plt.figure(figsize=(15, 7))
plt.plot(burglary_df['Month'], burglary_df['Burglary Count'], marker='.', linestyle='-', linewidth=2)

# Format x-axis to show 1 label per year
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

plt.title('Monthly Burglary Count in London (2022-2025)', fontsize=14)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Burglary Count', fontsize=12)

plt.grid(True, linestyle='--', alpha=0.5)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()