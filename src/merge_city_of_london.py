import geopandas as gpd
import pandas as pd
from pathlib import Path

# === Load data ===
gdf_wards = gpd.read_file('data/raw/Wards_December_2024_Boundaries_UK_BGC/WD_DEC_24_UK_BGC.shp')
gdf_london = gpd.read_file('data/boundaries/greater london boundary/London_GLA_Boundary.shp')

df_lsoa_to_ward = pd.read_csv('data/lookups/look up LSOA 2021 to ward 2024.csv')

# === Reproject to British National Grid ===
gdf_wards = gdf_wards.to_crs(epsg=27700)
gdf_london = gdf_london.to_crs(epsg=27700)

# === Clip wards to Greater London ===
gdf_wards_london_full = gpd.clip(gdf_wards, gdf_london)

# === Save unmerged version ===
gdf_london_wards_separate = gdf_wards_london_full.copy()

# === Merge City of London wards ===
print("Merging City of London wards...")
is_city = gdf_wards_london_full['LAD24NM'] == 'City of London'
gdf_city_of_london = gdf_wards_london_full[is_city].copy()
gdf_non_city_of_london = gdf_wards_london_full[~is_city].copy()

gdf_city_dissolved = gdf_city_of_london.dissolve().reset_index(drop=True)
gdf_city_dissolved['WD24NM'] = 'City of London'
gdf_city_dissolved['WD24CD'] = 'E09000001'

gdf_london_wards_merged = pd.concat([gdf_non_city_of_london, gdf_city_dissolved], ignore_index=True)

# === Save spatial outputs ===
save_dir = Path('data/boundaries/ward boundaries 2024')
save_dir.mkdir(parents=True, exist_ok=True)

gdf_london_wards_separate.to_file(save_dir / "london_wards.shp")
gdf_london_wards_merged.to_file(save_dir / "london_wards_merged.shp")

# === Update lookup table: merge City of London ward codes ===
is_city_2 = df_lsoa_to_ward['LAD24NM'] == 'City of London'

# update ward code and ward name for City of London rows
df_lsoa_to_ward.loc[is_city_2, 'WD24CD'] = 'E09000001'
df_lsoa_to_ward.loc[is_city_2, 'WD24NM'] = 'City of London'

# save merged lookup version
df_lsoa_to_ward_merged = df_lsoa_to_ward[['LSOA21CD', 'WD24CD', 'WD24NM']]
df_lsoa_to_ward_merged.to_csv('data/lookups/look up LSOA 2021 to ward 2024 merged.csv', index=False)

print('Updated to merged ward boundaries and lookup version.')
