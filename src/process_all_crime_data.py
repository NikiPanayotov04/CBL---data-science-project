import pandas as pd
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point

def load_and_filter_burglary_spatial(crime_root_dir, gdf_ward_boundaries):
    """Load burglary records and spatially join them with ward geometries."""
    crime_records = []

    # Loop through all year-month folders
    for folder in Path(crime_root_dir).glob("*/"):
        for file in folder.glob("*-street.csv"):
            print(f"Processing {file.name}")
            df = pd.read_csv(file, low_memory=False)

            # Filter burglary only, drop missing coordinates
            df = df[df['Crime type'] == 'Burglary'].copy()
            df.dropna(subset=['Longitude', 'Latitude'], inplace=True)

            # Convert to GeoDataFrame
            geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
            gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

            # Reproject to match ward boundaries CRS
            gdf = gdf.to_crs(gdf_ward_boundaries.crs)

            # Spatial join with ward polygons
            gdf_joined = gpd.sjoin(gdf, gdf_ward_boundaries[['geometry', 'WD24CD', 'WD24NM']], how='inner', predicate='intersects')

            # Rename for consistency
            gdf_joined.rename(columns={'WD24CD': 'Ward code', 'WD24NM': 'Ward name'}, inplace=True)

            gdf_joined['Month'] = pd.to_datetime(gdf_joined['Month'])

            # Keep only relevant columns
            columns = list(df.columns) + ['Ward code', 'Ward name']

            crime_records.append(gdf_joined[columns])

    # Concatenate all months
    gdf_all = pd.concat(crime_records, ignore_index=True)
    return gdf_all

# === Load ward polygons ===
gdf_ward_boundaries = gpd.read_file('data/boundaries/ward boundaries 2024/london_wards_merged.shp')
gdf_ward_boundaries = gdf_ward_boundaries.to_crs(epsg=27700)  # British National Grid

# === Load and process burglary records ===
df_burglaries = load_and_filter_burglary_spatial("data/crime 2022-2025", gdf_ward_boundaries)

# === Include Borough code/name ==
lookup = pd.read_csv('data/lookups/look up LSOA 2021 to ward 2024 merged.csv')[['LSOA code', 'Borough code', 'Borough name']]
df_burglaries_full = df_burglaries.merge(lookup, on=['LSOA code'], how='left')

# === Save to Parquet ===
output_path = Path("data/processed/burglaries.parquet")
output_path.parent.mkdir(parents=True, exist_ok=True)
df_burglaries_full.to_parquet(output_path, index=False)

print(f"Saved burglary records to {output_path}")

