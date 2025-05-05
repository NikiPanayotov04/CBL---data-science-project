import os
import pandas as pd
import folium
from folium.plugins import HeatMap

base_path = r"C:\Users\20230920\OneDrive - TU Eindhoven\TUE\Year 2\4rth Quarter\Multidiciplinary CBL\Metropolitan and city of london 22-25"

# Loop through all 12 months of 2022
for month in range(1, 13):
    month_str = f"2022-{month:02d}"
    city_file = os.path.join(base_path, month_str, f"{month_str}-city-of-london-street.csv")
    metro_file = os.path.join(base_path, month_str, f"{month_str}-metropolitan-street.csv")


    monthly_data = []
    
    for path in [city_file, metro_file]:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df = df[df["Crime type"].str.lower() == "burglary"]
            df = df.dropna(subset=["Latitude", "Longitude"])
            monthly_data.extend(df[["Latitude", "Longitude"]].values.tolist())

    if monthly_data:
        print(f"\n--- {month_str} ---")
        m = folium.Map(location=[51.509865, -0.118092], zoom_start=11)
        HeatMap(monthly_data, radius=10).add_to(m)
        display(m)
    else:
        print(f"{month_str}: No data found or no burglaries.")

# Loop through all 12 months of 2023
for month in range(1, 13):
    month_str = f"2023-{month:02d}"
    city_file = os.path.join(base_path, month_str, f"{month_str}-city-of-london-street.csv")
    metro_file = os.path.join(base_path, month_str, f"{month_str}-metropolitan-street.csv")


    monthly_data = []
    
    for path in [city_file, metro_file]:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df = df[df["Crime type"].str.lower() == "burglary"]
            df = df.dropna(subset=["Latitude", "Longitude"])
            monthly_data.extend(df[["Latitude", "Longitude"]].values.tolist())

    if monthly_data:
        print(f"\n--- {month_str} ---")
        m = folium.Map(location=[51.509865, -0.118092], zoom_start=11)
        HeatMap(monthly_data, radius=10).add_to(m)
        display(m)
    else:
        print(f"{month_str}: No data found or no burglaries.")
# Loop through all 12 months of 2024
for month in range(1, 13):
    month_str = f"2024-{month:02d}"
    city_file = os.path.join(base_path, month_str, f"{month_str}-city-of-london-street.csv")
    metro_file = os.path.join(base_path, month_str, f"{month_str}-metropolitan-street.csv")


    monthly_data = []
    
    for path in [city_file, metro_file]:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df = df[df["Crime type"].str.lower() == "burglary"]
            df = df.dropna(subset=["Latitude", "Longitude"])
            monthly_data.extend(df[["Latitude", "Longitude"]].values.tolist())

    if monthly_data:
        print(f"\n--- {month_str} ---")
        m = folium.Map(location=[51.509865, -0.118092], zoom_start=11)
        HeatMap(monthly_data, radius=10).add_to(m)
        display(m)
    else:
        print(f"{month_str}: No data found or no burglaries.")
# Loop through 2 months of 2025
for month in range(1, 3):
    month_str = f"2025-{month:02d}"
    city_file = os.path.join(base_path, month_str, f"{month_str}-city-of-london-street.csv")
    metro_file = os.path.join(base_path, month_str, f"{month_str}-metropolitan-street.csv")


    monthly_data = []
    
    for path in [city_file, metro_file]:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df = df[df["Crime type"].str.lower() == "burglary"]
            df = df.dropna(subset=["Latitude", "Longitude"])
            monthly_data.extend(df[["Latitude", "Longitude"]].values.tolist())

    if monthly_data:
        print(f"\n--- {month_str} ---")
        m = folium.Map(location=[51.509865, -0.118092], zoom_start=11)
        HeatMap(monthly_data, radius=10).add_to(m)
        display(m)
    else:
        print(f"{month_str}: No data found or no burglaries.")
