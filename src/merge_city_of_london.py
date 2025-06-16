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

# === Get London boundary polygon (assuming single polygon) ===
london_boundary = gdf_london.unary_union

# === Filter wards whose centroid is within London boundary ===
gdf_wards_in_london = gdf_wards[gdf_wards.centroid.within(london_boundary)]

# === Clip wards to Greater London boundary (optional) ===
gdf_wards_london_clipped = gpd.clip(gdf_wards_in_london, gdf_london)

# === Save unmerged version ===
gdf_london_wards_separate = gdf_wards_london_clipped.copy()

# === Merge City of London wards ===
print("Merging City of London wards...")
is_city = gdf_london_wards_separate['LAD24NM'] == 'City of London'
gdf_city_of_london = gdf_london_wards_separate[is_city].copy()
gdf_non_city_of_london = gdf_london_wards_separate[~is_city].copy()

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

df_lsoa_to_ward.loc[is_city_2, 'WD24CD'] = 'E09000001'
df_lsoa_to_ward.loc[is_city_2, 'WD24NM'] = 'City of London'

df_lsoa_to_ward_merged = df_lsoa_to_ward[['LSOA21CD', 'LSOA21NM', 'WD24CD', 'WD24NM', 'LAD24CD', 'LAD24NM']].copy()
df_lsoa_to_ward_merged.rename(columns={'LSOA21CD': 'LSOA code', 'LSOA21NM': 'LSOA name', 'WD24CD': 'Ward code', 'WD24NM': 'Ward name', 'LAD24CD': 'Borough code', 'LAD24NM': 'Borough name'}, inplace=True)
df_lsoa_to_ward_merged.to_csv('data/lookups/look up LSOA 2021 to ward 2024 merged.csv', index=False)


print('Updated to merged ward boundaries and lookup version.')
