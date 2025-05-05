# == Imports ==
import pandas as pd
from pathlib import Path
import re

# == Paths ==
ROOT_DIR = Path('../data')
CRIME_DIR = ROOT_DIR / 'crime'
ADDITIONAL_RAW = ROOT_DIR / 'additional' / 'raw'
ADDITIONAL_PROCESSED = ROOT_DIR / 'additional' / 'processed'
BOUNDARY_DIR = ROOT_DIR / 'boundaries'
LOOKUP_DIR = ROOT_DIR / 'lookups'

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

def get_london_lsoas(year=2021):
    """
    Obtain LSOA names and codes from either 2011 or 2021.
    """
    filename = f'LSOA names and codes {year}.csv'
    path = LOOKUP_DIR / filename
    df_lsoa = load_csv(path, usecols=[0, 1])
    boroughs = df_lsoa['LSOA name'].str.extract(r'^(.*?)(?: \d{3}[A-Z])?$')[0]
    return df_lsoa[boroughs.isin(LONDON_BOROUGHS)][['LSOA code']]

def match_deprivation_to_2021():
    """
    Loads deprivation data for 2011, maps it to 2021 LSOA codes using lookup table, and returns a DataFrame with
    2021 LSOA names, codes, and (averaged) deprivation metrics.
    """
    df_lsoa_21 = pd.read_csv(LOOKUP_DIR / 'LSOA names and codes 2021.csv', usecols=[0, 1])
    df_lookup = pd.read_csv(LOOKUP_DIR / 'Look up LSOA 2011 to LSOA 2021.csv', usecols=[0, 2])
    df_dep_11 = pd.read_excel(ADDITIONAL_RAW / 'Indices of deprivation 2019.xlsx', sheet_name=1, usecols='A, B, E:T')

    merged = pd.merge(df_lookup, df_dep_11, left_on='LSOA11CD', right_on='LSOA code (2011)', how='left')
    df_agg = merged.groupby('LSOA21CD').mean(numeric_only=True).reset_index()

    df_dep_21 = pd.merge(df_lsoa_21, df_agg, on='LSOA21CD', how='left')
    return clean_column_names(df_dep_21)


# == Load and preprocess ==
df_lsoa_london_21 = get_london_lsoas(2021)
df_lsoa_london_11 = get_london_lsoas(2011)

df_age = load_csv(ADDITIONAL_RAW / 'Age by broad age bands 2021.csv', skiprows=[0, 1, 2, 3, 6, 7], lsoa=True)
df_age_london = pd.merge(df_age, df_lsoa_london_21, on='LSOA code', how='inner')

df_household = load_csv(ADDITIONAL_RAW / 'Household composition 2021.csv', skiprows=[0, 1, 2, 3, 4, 5, 8, 9],
                        drop_last_n=5, lsoa=True)
df_household_london = pd.merge(df_household, df_lsoa_london_21, on='LSOA code', how='inner')

df_occupancy = load_excel(ADDITIONAL_RAW / 'Dwelling characteristics - occupancy and type 2021.xlsx', '1c', skiprows=3)
df_occupancy_london = pd.merge(df_occupancy, df_lsoa_london_21, on='LSOA code', how='inner')

df_accommodation = load_excel(ADDITIONAL_RAW / 'Dwelling characteristics - occupancy and type 2021.xlsx', '2c',
                              skiprows=3)
df_accommodation_london = pd.merge(df_accommodation, df_lsoa_london_21, on='LSOA code', how='inner')

df_dep_11 = load_excel(ADDITIONAL_RAW / 'Indices of deprivation 2019.xlsx', sheet=1, usecols='A, B, E:T')
df_dep_11_london = pd.merge(df_dep_11, df_lsoa_london_11, on='LSOA code', how='inner')

df_dep_21 = match_deprivation_to_2021()
df_dep_21_london = pd.merge(df_dep_21, df_lsoa_london_21, on='LSOA code', how='inner')

df_stops = pd.read_csv(ADDITIONAL_RAW / 'Stops.csv', low_memory=False, usecols=[
    'ATCOCode', 'CommonName', 'NptgLocalityCode', 'LocalityName', 'Longitude', 'Latitude', 'Status'])
df_stops_london = df_stops[df_stops['ATCOCode'].str.startswith('490')] # ATCO Codes in London start with 490

# == Save to processed directory ==
df_age_london.to_csv(ADDITIONAL_PROCESSED / 'age_london.csv', index=False)
df_household_london.to_csv(ADDITIONAL_PROCESSED / 'household_composition_london.csv', index=False)
df_occupancy_london.to_csv(ADDITIONAL_PROCESSED / 'dwelling_occupancy_london.csv', index=False)
df_accommodation_london.to_csv(ADDITIONAL_PROCESSED / 'accommodation_type_london.csv', index=False)
df_dep_11_london.to_csv(ADDITIONAL_PROCESSED / 'deprivation_11_london.csv', index=False)
df_dep_21_london.to_csv(ADDITIONAL_PROCESSED / 'deprivation_london.csv', index=False)
df_stops_london.to_csv(ADDITIONAL_PROCESSED / 'stops_london.csv', index=False)