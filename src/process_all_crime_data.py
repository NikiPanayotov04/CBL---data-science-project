import pandas as pd
from pathlib import Path
import geopandas as gpd

def load_and_filter_burglary(crime_root_dir, lsoa_to_ward_df):
    """Go through all crime folders and filter it for only burglary crimes."""
    crime_records = []

    # walk through all year-month folders
    for folder in Path(crime_root_dir).glob("*/"):
        for file in folder.glob("*-street.csv"):
            print(f"Processing {file.name}")
            df = pd.read_csv(file, low_memory=False)

            # filter only burglary crimes
            df_burglary = df[df['Crime type'] == 'Burglary'].copy()

            # drop rows with missing LSOA code
            df_burglary.dropna(subset=['LSOA code'], inplace=True)

            # merge with ward info
            df_burglary = df_burglary.merge(lsoa_to_ward_df, on='LSOA code', how='left')

            crime_records.append(df_burglary)

    # concatenate all months into one DataFrame
    df_all_burglary = pd.concat(crime_records, ignore_index=True)
    return df_all_burglary

# Load LSOA-to-ward mapping
df_lsoa_to_ward = pd.read_csv('data/lookups/look up LSOA 2021 to ward 2024 merged.csv')
df_lsoa_to_ward.rename(columns={'LSOA21CD': 'LSOA code', 'WD24CD': 'Ward code', 'WD24NM': 'Ward name'}, inplace=True)

# Load crime data
df_burglary = load_and_filter_burglary("data/crime 2022-2025", df_lsoa_to_ward)

# Strictly filter only London crimes using ward codes from shapefile
gdf_ward_boundaries = gpd.read_file('data/boundaries/ward boundaries 2024/london_wards_merged.shp')
gdf_ward_boundaries.rename(columns={'WD24CD': 'Ward code'}, inplace=True)  # Ensure consistency

# Get list of valid London ward codes
london_ward_codes = set(gdf_ward_boundaries['Ward code'].unique())

# Filter only burglary crimes within London wards
df_burglary_london_only = df_burglary[df_burglary['Ward code'].isin(london_ward_codes)].copy()

# Save filtered data
output_path = Path("data/processed/burglaries.parquet")
output_path.parent.mkdir(parents=True, exist_ok=True)
df_burglary_london_only.to_parquet(output_path, index=False)

print(f"Saved strict London-only burglary records to {output_path}")

