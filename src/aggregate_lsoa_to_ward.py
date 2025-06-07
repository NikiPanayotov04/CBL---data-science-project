import pandas as pd
import geopandas as gpd

comment = '''
These are examples of the datasets aggregated to ward. I have not decided to save them (yet). But these can (and should) certainly 
be used for feature engineering. 
'''

# --- Load Ward Boundaries Shapefile ---
gdf_ward_boundaries = gpd.read_file('data/boundaries/ward boundaries 2024/london_wards_merged.shp')

# --- Load Census Data at LSOA Level ---
df_census = pd.read_parquet('data/processed/census_lsoa.parquet')

# Aggregate Census data by Ward (sum numeric columns)
df_census_ward = df_census.groupby(['Ward code', 'Ward name']).sum(numeric_only=True).reset_index()

# --- Load Deprivation Data at LSOA Level ---
df_dep = pd.read_parquet('data/processed/deprivation_lsoa.parquet')
# Aggregate Deprivation data by Ward (mean numeric columns)
df_dep_ward = df_dep.groupby(['Ward code', 'Ward name']).mean(numeric_only=True).reset_index()
# Rename deprivation columns to indicate these are averages by ward
df_dep_ward.rename(
    columns={col: f'Avg {col}' for col in df_dep_ward.columns if col not in ['Ward code', 'Ward name']},
    inplace=True
)

# --- Load Burglary Crime Data ---
df_burglaries = pd.read_parquet('data/processed/burglaries.parquet')
# Aggregate burglary counts by Ward
df_burglaries_ward = df_burglaries.groupby('Ward code').size().reset_index(name='Crime count')

print(df_dep['LSOA code'].nunique())
print(df_census['LSOA code'].nunique())