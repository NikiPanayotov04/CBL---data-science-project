import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import st_folium

@st.cache_data
def load_data():
    df = pd.read_csv('data/processed/ward level/census_by_ward.csv')
    return df

data = load_data()
st.title("London Burglary Dashboard")


# Create tabs for different visualizations
tab1, tab2, tab3 = st.tabs(["Population by Ward", "Stops map", "Additional Data"])

# Tab 1: Bar chart for total population by ward
with tab1:
    population_col = None
    for col in data.columns:
        if 'population' in col.lower() or 'total' in col.lower():
            population_col = col
            break
    if population_col:
        st.subheader(f"Total Population by Ward ({population_col})")
        fig, ax = plt.subplots(figsize=(10, 6))
        data_sorted = data.sort_values(population_col, ascending=False)
        ax.bar(data_sorted['Ward name'], data_sorted[population_col])
        ax.set_xlabel('Ward name')
        ax.set_ylabel(population_col)
        ax.set_xticklabels(data_sorted['Ward name'], rotation=90, fontsize=8)
        st.pyplot(fig)
    else:
        st.info("No population column found for bar chart.")

# Tab 2: Pie chart for accommodation type distribution
with tab2:
    st.subheader("Stops Map")
    with open('outputs/html/boundaries_and_stops_map.html', 'r') as f:
        html_data = f.read()
    st.components.v1.html(html_data, height=600)

# Tab 3: Additional Data
with tab3:
    st.subheader("Additional Data Visualizations")
    
    # Age data
    st.write("Age Data")
    df_age = pd.read_csv('data/processed/lsoa level/age_london.csv')
    st.dataframe(df_age.head())
    
    # Household composition data
    st.write("Household Composition Data")
    df_household = pd.read_csv('data/processed/lsoa level/household_composition_london.csv')
    st.dataframe(df_household.head())
    
    # Dwelling occupancy data
    st.write("Dwelling Occupancy Data")
    df_occupancy = pd.read_csv('data/processed/lsoa level/dwelling_occupancy_london.csv')
    st.dataframe(df_occupancy.head())
    
    # Accommodation type data
    st.write("Accommodation Type Data")
    df_accommodation = pd.read_csv('data/processed/lsoa level/accommodation_type_london.csv')
    st.dataframe(df_accommodation.head())
    
    # Deprivation data
    st.write("Deprivation Data")
    df_deprivation = pd.read_csv('data/processed/lsoa level/deprivation_11_to_21_london.csv')
    st.dataframe(df_deprivation.head())
    
    # Stops data
    st.write("Stops Data")
    df_stops = pd.read_csv('data/processed/lsoa level/stops_london.csv')
    st.dataframe(df_stops.head())

# (Optional) Add more visualizations as needed
# Add markers or layers to the map
