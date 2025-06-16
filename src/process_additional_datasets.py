# == Imports ==
import pandas as pd
from pathlib import Path
import re

# == Variables and Constants ==
RENAME_COLS = {'Area Code': 'LSOA code', 'mnemonic': 'LSOA code', 'LSOA21CD': 'LSOA code', 'LSOA11CD': 'LSOA code', 'LSOA Code': 'LSOA code',
               'Area Name': 'LSOA name', 'Area': 'LSOA name', 'LSOA21NM': 'LSOA name', 'LSOA11NM': 'LSOA name', 'LSOA Name': 'LSOA name'}

LONDON_BOROUGHS = ["Barking and Dagenham", "Barnet", "Bexley", "Brent", "Bromley", "Camden", "City of London",
                   "Croydon", "Ealing", "Enfield", "Greenwich", "Hackney", "Hammersmith and Fulham", "Haringey",
                   "Harrow", "Havering", "Hillingdon", "Hounslow", "Islington", "Kensington and Chelsea",
                   "Kingston upon Thames", "Lambeth", "Lewisham", "Merton", "Newham", "Redbridge",
                   "Richmond upon Thames", "Southwark", "Sutton", "Tower Hamlets", "Waltham Forest", "Wandsworth",
                   "Westminster"]

# == Functions ==
def clean_column_names(df, lsoa=False):
    """
    Clean columns names for compatibility across different datasets.
    """
    df.rename(columns=RENAME_COLS, inplace=True)
    df.columns = [re.sub(r'\s*\((?!IMD\)).*?\)', '', col) for col in df.columns]
    if lsoa:
        df['LSOA name'] = df['LSOA name'].str.replace('lsoa2021:', '', regex=False)
    return df

def load_csv(path, skiprows=None, drop_last_n=None, usecols=None, lsoa=False):
    """
    Load and clean a csv file.
    """
    df = pd.read_csv(path, skiprows=skiprows, usecols=usecols)
    if drop_last_n:
        df = df.iloc[:-drop_last_n].copy()
    return clean_column_names(df, lsoa=lsoa)

def load_excel(path, sheet, skiprows=None, drop_last_n=None, usecols=None):
    """
    Load and clean an excel sheet.
    """
    df = pd.read_excel(path, sheet_name=sheet, skiprows=skiprows, usecols=usecols)
    return clean_column_names(df)

def group_age_bands(df):
    """Groups age bands."""
    df['Under 15 years'] = (
            df['Aged 4 years and under'] +
            df['Aged 5 to 9 years'] +
            df['Aged 10 to 15 years']
    )

    df['15 to 64 years'] = (
            df['Aged 16 to 19 years'] +
            df['Aged 20 to 24 years'] +
            df['Aged 25 to 34 years'] +
            df['Aged 35 to 49 years'] +
            df['Aged 50 to 64 years']
    )

    df['65 years and older'] = (
            df['Aged 65 to 74 years'] +
            df['Aged 75 to 84 years'] +
            df['Aged 85 years and over']
    )

    df = df.drop(columns=[
        'Aged 4 years and under', 'Aged 5 to 9 years', 'Aged 10 to 15 years',
        'Aged 16 to 19 years', 'Aged 20 to 24 years', 'Aged 25 to 34 years',
        'Aged 35 to 49 years', 'Aged 50 to 64 years', 'Aged 65 to 74 years',
        'Aged 75 to 84 years', 'Aged 85 years and over'
    ])

    df.rename(columns={'Total': 'Total population'}, inplace=True)

    return df

def population_weighted_agg(df, cols, weight_col):
    """Aggregates data based on population-weighted averages."""
    weighted = {}

    total_weight = df[weight_col].sum()

    for col in cols:
        weighted[col] = (df[col] * df[weight_col]).sum() / total_weight

    return pd.Series(weighted)

def match_deprivation_to_2021():
    """
    Maps deprivation data from 2011 LSOA to 2021 LSOA using a lookup table and aggregates using population-weighted averages.
    """
    # load deprivation data including population
    df_dep_11_london = pd.read_excel('data/raw/ID 2019 for London.xlsx', sheet_name=1, usecols='A:AB')
    pop_df = pd.read_excel('data/raw/ID 2019 for London.xlsx', sheet_name='Population figures', usecols="A, E")
    df_dep_11_london = pd.merge(df_dep_11_london, pop_df, on="LSOA code (2011)")

    # load df_lookup
    df_lookup = pd.read_csv('data/lookups/look up LSOA 2011 to LSOA 2021.csv', usecols=[0, 2])

    # merge the lookup table with the deprivation data (mapping 2011 LSOA to 2021 LSOA)
    merged = pd.merge(df_lookup, df_dep_11_london, left_on='LSOA11CD', right_on='LSOA code (2011)', how='right')

    # list of deprivation score columns
    cols = df_dep_11_london.columns[4:-1]

    # aggregating the data based on LSOA 2021
    # create a list to hold aggregated results
    results = []

    # group by LSOA21CD
    for lsoa21cd, group in merged.groupby('LSOA21CD'):
        aggregated = population_weighted_agg(group, cols, "Total population: mid 2015 (excluding prisoners)")
        aggregated['LSOA21CD'] = lsoa21cd  # add the group key back
        results.append(aggregated)

    # combine into a DataFrame
    df_dep_21_london = pd.DataFrame(results)
    return df_dep_21_london

def save_to_processed_parquet(df, filename):
    """Save dataframe to the processed directory in parquet format, creating directory if necessary."""
    processed_path = Path('data/processed') / filename
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(processed_path, index=False)
    print(f"Saved {filename} to processed directory in parquet format.")

# == Load and Preprocess ==
df_lsoa_21 = load_csv('data/lookups/LSOA names and codes 2021.csv', usecols=[0, 1])
boroughs = df_lsoa_21['LSOA name'].str.extract(r'^(.*?)(?: \d{3}[A-Z])?$')[0]
df_lsoa_london_21 = df_lsoa_21[boroughs.isin(LONDON_BOROUGHS)][['LSOA code']]

print("Processing age data...")
df_age = load_csv('data/raw/Age by broad age bands 2021.csv', skiprows=[0, 1, 2, 3, 6, 7], lsoa=True)
df_age_london = pd.merge(df_age, df_lsoa_london_21, on='LSOA code', how='inner')
df_age_london = group_age_bands(df_age_london)

print("Processing household composition data...")
df_household = load_csv('data/raw/Household composition 2021.csv', skiprows=[0, 1, 2, 3, 4, 5, 8, 9], drop_last_n=5, lsoa=True)
df_household_london = pd.merge(df_household, df_lsoa_london_21, on='LSOA code', how='inner')

print("Processing dwelling occupancy data...")
df_occupancy = load_excel('data/raw/Dwelling characteristics - occupancy and type 2021.xlsx', '1c', skiprows=3)
df_occupancy = df_occupancy.iloc[:, [0, 1, 2, 3, 6]]
df_occupancy_london = pd.merge(df_occupancy, df_lsoa_london_21, on='LSOA code', how='inner')

print("Processing accommodation type data...")
df_accommodation = load_excel('data/raw/Dwelling characteristics - occupancy and type 2021.xlsx', '2c', skiprows=3)
df_accommodation_london = pd.merge(df_accommodation, df_lsoa_london_21, on='LSOA code', how='inner')

print("Processing indices of deprivation data...")
df_dep_11_to_21_london = clean_column_names(match_deprivation_to_2021())

print("Processing stops data...")
df_stops = pd.read_csv('data/raw/Stops.csv', low_memory=False, usecols=['ATCOCode', 'CommonName', 'NptgLocalityCode', 'LocalityName', 'Longitude', 'Latitude', 'Status'])
df_stops_london = df_stops[df_stops['ATCOCode'].str.startswith('490')]  # ATCO Codes in London start with 490

# == Merge Census Data ==
df_census_london = (
    df_age_london
    .merge(df_household_london, on=['LSOA code', 'LSOA name'], how='inner')
    .merge(df_accommodation_london, on=['LSOA code', 'LSOA name'], how='inner')
    .merge(df_occupancy_london, on=['LSOA code', 'LSOA name'], how='inner')
)
# convert all non-id columns to float
for col in df_census_london.columns:
    if col not in ['LSOA code', 'LSOA name']:
        df_census_london[col] = pd.to_numeric(df_census_london[col], errors='coerce')

# == Match LSOA to ward ==
df_lsoa_to_ward = pd.read_csv('data/lookups/look up LSOA 2021 to ward 2024 merged.csv')
# include ward and borough codes/names
df_census_london = df_census_london.merge(df_lsoa_to_ward, on=['LSOA code', 'LSOA name'])
df_dep_11_to_21_london = df_dep_11_to_21_london.merge(df_lsoa_to_ward, on=['LSOA code'])


# == Save Files ==
save_to_processed_parquet(df_census_london, 'census_lsoa.parquet')
save_to_processed_parquet(df_dep_11_to_21_london, 'deprivation_lsoa.parquet')
save_to_processed_parquet(df_stops_london, 'stops_lsoa.parquet')



