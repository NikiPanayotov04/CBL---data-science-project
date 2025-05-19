import pandas as pd
import geopandas as gpd

# == Shapefiles ==
# load shapefiles
london_boundary = gpd.read_file('data/boundaries/greater london boundary/London_GLA_Boundary.shp')
wards = gpd.read_file('data/boundaries/ward boundaries 2018/London_Ward_CityMerged.shp')
centroids = gpd.read_file(
    'data/raw/LLSOA_Dec_2021_PWC_for_England_and_Wales_2022_4975765757449378936/LSOA_PopCentroids_EW_2021_V3.shp')
centroids = centroids.to_crs(london_boundary.crs)

# filter centroids that fall within the same london boundary
centroids = centroids[centroids.geometry.within(london_boundary.union_all())]

# save to shapefile
centroids.to_file('data/boundaries/lsoa population weighted centroids 2021/centroids_within_london.shp')

# == Match LSOA to Ward ==
# spatial join: assign each centroid to the ward it falls inside
centroids_in_wards = gpd.sjoin(centroids, wards, how="left", predicate="intersects")

lsoa_to_ward_temp = centroids_in_wards[['LSOA21CD', 'NAME', 'GSS_CODE']]
lsoa_to_ward_temp.columns = ['LSOA code', 'Ward name', 'Ward code']
# updating 'Ward name' from "Castle Banyard" to "City of London" (since City of London is merged)
lsoa_to_ward = lsoa_to_ward_temp.copy()
lsoa_to_ward.loc[lsoa_to_ward['Ward name'] == 'Castle Baynard', 'Ward name'] = 'City of London'

# == Join Ward to Census Data ==
# load and merge census data, ensure numerical values
df_age_london = pd.read_csv('data/processed/lsoa level/age_london.csv')
df_accom_type = pd.read_csv('data/processed/lsoa level/accommodation_type_london.csv')
df_occup = pd.read_csv('data/processed/lsoa level/dwelling_occupancy_london.csv')
df_house_comp = pd.read_csv('data/processed/lsoa level/household_composition_london.csv')

df_census = df_age_london.merge(df_accom_type, on=['LSOA code', 'LSOA name']) \
                         .merge(df_occup, on=['LSOA code', 'LSOA name']) \
                         .merge(df_house_comp, on=['LSOA code', 'LSOA name'])

# merge
df_census = df_census.merge(lsoa_to_ward, on='LSOA code')

df_census_with_ward = df_census.copy()

# non-numeric cols
id_cols = ['LSOA code', 'LSOA name', 'Ward code', 'Ward name', 'District']

# convert should-be numeric columns
for col in df_census_with_ward.columns:
    if col not in id_cols:
        df_census_with_ward[col] = pd.to_numeric(df_census_with_ward[col], errors='coerce')

# group and aggregate counts by ward
df_census_ward = df_census_with_ward.groupby(['Ward code', 'Ward name']).sum(numeric_only=True).reset_index()

# save
df_census_ward.to_csv('data/processed/ward level/census_by_ward.csv', index=False)

