# Import required libraries
import dash  # Main Dash framework
from dash import html  # HTML components for Dash
import dash_bootstrap_components as dbc  # Bootstrap components for styling
from dash import dcc, html, Input, Output  # Dash core components and callbacks
import pandas as pd  # Data manipulation
import plotly.express as px  # Data visualization
import os  # File system operations
from datetime import datetime  # Date handling
import plotly.graph_objects as go  # Advanced plotting
import geopandas as gpd  # Geographic data handling
import json  # JSON data handling

# Initialize the Dash application
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG,  # Dark theme for the dashboard
        'assets/custom_dashboard_dash.css'  # Custom CSS file
    ],
    suppress_callback_exceptions=True  # Suppress callback exceptions for dynamic layouts
)
app.title = "Police Forecasting Dashboard"

# Data loading functions
def load_crime_data(month=None):
    """
    Load crime data for a specific month.
    
    Args:
        month (str, optional): Month in 'YYYY-MM' format. Defaults to most recent month.
    
    Returns:
        pandas.DataFrame: Crime data for the specified month
    """
    try:
        if month is None:
            # Default to most recent month if none specified
            month = "2022-04"
        
        # Construct file path for the specified month
        file_path = f'data/crime 2022-2025/{month}/{month}-metropolitan-street.csv'
        
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            print(f"File not found: {file_path}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error loading crime data: {str(e)}")
        return pd.DataFrame()

def load_deprivation_data():
    """
    Load deprivation index data for London areas.
    
    Returns:
        pandas.DataFrame: Deprivation data including IMD scores and domain indices
    """
    try:
        file_path = 'data/processed/deprivation_lsoa.parquet'
        if os.path.exists(file_path):
            return pd.read_parquet(file_path)
        else:
            print(f"File not found: {file_path}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error loading deprivation data: {str(e)}")
        return pd.DataFrame()

def load_census_data():
    """
    Load census data for London areas.
    
    Returns:
        pandas.DataFrame: Census data including population and demographic information
    """
    try:
        file_path = 'data/processed/census_lsoa.parquet'
        if os.path.exists(file_path):
            return pd.read_parquet(file_path)
        else:
            print(f"File not found: {file_path}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error loading census data: {str(e)}")
        return pd.DataFrame()

# Sidebar menu configuration
sidebar = dbc.Col([
    html.H4("Menu", className="text-white mt-4"),
    html.Hr(),
    dbc.Nav([
        # Main navigation links
        dbc.NavLink("Home", href="/", active="exact", className="nav-link"),
        dbc.NavLink("Data Explorer", href="/data", active="exact", className="nav-link"),
        # Data Explorer submenu
        html.Div(id="data-explorer-submenu", style={"display": "none"}, children=[
            dbc.NavLink("Crime Data", href="/data/crime", active="exact", className="nav-link ms-3"),
            dbc.NavLink("Deprivation Index", href="/data/deprivation", active="exact", className="nav-link ms-3"),
            dbc.NavLink("Census Data", href="/data/census", active="exact", className="nav-link ms-3"),
            dbc.NavLink("Summarized Data", href="/data/summary", active="exact", className="nav-link ms-3"),
        ]),
        # Additional main navigation links
        dbc.NavLink("Forecasting", href="/forecast", active="exact", className="nav-link"),
        dbc.NavLink("Map View", href="/map", active="exact", className="nav-link"),
        dbc.NavLink("About", href="/about", active="exact", className="nav-link")
    ], vertical=True, pills=True),
], width=2, className="sidebar")

# Page layout functions
def homepage():
    """
    Generate the homepage layout with project overview and key information.
    
    Returns:
        dbc.Card: Homepage layout component
    """
    return dbc.Card([
        dbc.CardBody([
            # Title and welcome message
            html.H1("Automated Police Demand Forecasting", className="card-title"),
            html.P("Welcome to the Police Demand Forecasting Dashboard.", className="card-text"),
            html.H2("Problem Description", className="mb-4 mt-4"),

            # Problem statement boxes
            html.Div([
                # High prevalence box
                html.Div([
                    html.Span("1", className="badge-number me-3"),
                    html.Span([
                        html.B("High Prevalence: "),
                        "Residential burglary accounts for 4.5% of all crimes in Greater London."
                    ])
                ], className="problem-box mb-3"),

                # Low resolution rate box
                html.Div([
                    html.Span("2", className="badge-number me-3"),
                    html.Span([
                        html.B("Low Resolution Rate: "),
                        "82% of residential burglaries went unsolved in 2022/2023, highlighting gaps in current policing effectiveness."
                    ])
                ], className="problem-box mb-3"),

                # Public trust box
                html.Div([
                    html.Span("3", className="badge-number me-3"),
                    html.Span([
                        html.B("Eroding Public Trust: "),
                        "The combination of frequency and lack of resolution undermines public confidence in police protection and safety."
                    ])
                ], className="problem-box mb-3"),
            ]),

            html.Hr(),

            # London image
            html.Img(src="/assets/london_image.jpg", style={"width": "100%", "maxWidth": "800px", "margin": "20px auto", "display": "block"}),

            html.Hr(),

            # Contributors section
            html.Div([
                html.H5("Contributors"),
                html.Ul([
                    html.Li("Niki Panayotov"),
                    html.Li("Jan Galic"),
                    html.Li("Pantelis Hadjipanayiotou"),
                    html.Li("Trinity Jan"),
                    html.Li("Team members from Eindhoven University of Technology"),
                ])
            ]),

            # Footer
            html.Footer("Project developed by team 31(Fantastic Four):", 
                        style={"fontSize": "0.85rem", "color": "#aaa", "marginTop": "2rem", "textAlign": "center"})
        ])
    ])

def data_explorer():
    """
    Generate the data explorer page layout with dataset descriptions and navigation buttons.
    
    Returns:
        dbc.Card: Data explorer layout component
    """
    return dbc.Card([
        dbc.CardBody([
            # Title and description
            html.H1("Data Explorer", className="card-title"),
            html.P("Welcome to the Data Explorer section. Here you can access and analyze various datasets related to police demand forecasting in London.", className="card-text text-center"),
            html.P("Our datasets include:", className="card-text mt-4 text-center"),
            
            # Dataset list
            html.Div([
                html.Ul([
                    html.Li("Crime Data: Monthly burglary statistics across London boroughs from 2022 to 2025", className="text-center"),
                    html.Li("Demographic Data: Information about population, household composition, and dwelling occupancy", className="text-center"),
                    html.Li("Census Data: Ward-level demographic information from the latest census", className="text-center"),
                    html.Li("Summarized Data: Key insights and aggregated statistics from all datasets", className="text-center")
                ], className="card-text mb-4", style={"listStyle": "none", "padding": "0"})
            ], className="d-flex justify-content-center"),
            
            # Navigation buttons
            html.P("Select a dataset below to begin exploring:", className="card-text text-center"),
            html.Div([
                dbc.Button("Crime Data", href="/data/crime", color="primary", className="me-3"),
                dbc.Button("Deprivation Data", href="/data/deprivation", color="primary", className="me-3"),
                dbc.Button("Census Data", href="/data/census", color="primary", className="me-3"),
                dbc.Button("Summarized Data", href="/data/summary", color="primary", className="me-3"),
            ], className="mt-4 text-center")
        ])
    ])

def crime_data():
    return dbc.Card([
        dbc.CardBody([
            html.H1("Crime Data (2022-2025)", className="card-title"),
            html.P("Select a month to view the corresponding crime data:", className="card-text text-center"),
            
            # Month picker
            html.Div([
                dcc.Dropdown(
                    id='month-picker',
                    options=[
                        {'label': f"{year}-{month:02d}", 'value': f"{year}-{month:02d}"}
                        for year in range(2022, 2026)
                        for month in range(1, 13)
                        if not (year == 2022 and month < 4) and not (year == 2025 and month > 3)  # Only show from Apr 2022 to Feb 2025
                    ],
                    value="2022-04",  # Default value set to April 2022
                    clearable=False,
                    className="mb-4",
                    style={'width': '200px'}
                )
            ], className="d-flex justify-content-center"),
            
            # Data display
            html.Div(id="crime-data-table", className="mt-3"),
            
            # Error message container
            html.Div(id="crime-data-error", className="text-danger text-center mt-3")
        ])
    ])

def deprivation_data():
    return dbc.Card([
        dbc.CardBody([
            html.H1("Deprivation Index", className="card-title"),
            html.P("Explore deprivation index dataset for London wards:", className="card-text text-center mb-4"),
            
            html.Div([
                html.P("This dataset contains deprivation indices for London areas from 2011 to 2021, including income, employment, health, education, and living environment indicators.", className="card-text text-center"),
                
                # Add attribute descriptions
                html.Div([
                    html.H4("Data Attributes", className="mt-4 mb-3 text-start"),
                    html.Ul([
                        html.Li([
                            html.Strong("Index of Multiple Deprivation (IMD): "),
                            "Overall measure of relative deprivation combining all other domains. Higher scores indicate higher deprivation."
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Income Domain: "),
                            "Measures income deprivation including benefits, tax credits, and low income."
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Employment Domain: "),
                            "Measures employment deprivation including unemployment and incapacity benefits."
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Education, Skills and Training: "),
                            "Measures lack of attainment and skills in the local population."
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Health Deprivation and Disability: "),
                            "Measures morbidity, disability, and premature mortality."
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Crime Domain: "),
                            "Measures recorded crime rates for violence, burglary, theft, and criminal damage."
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Barriers to Housing and Services: "),
                            "Measures physical and financial accessibility to housing and key local services."
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Living Environment: "),
                            "Measures quality of the local environment including air quality and housing conditions."
                        ], className="text-start"),
                        html.Li([
                            html.Strong("LSOA code: "),
                            "Lower Layer Super Output Area identifier - small area statistical geography."
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Ward code & name: "),
                            "Local authority ward identifier and name."
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Ranks & Deciles: "),
                            "Relative measures where 1 is most deprived and 10 is least deprived. Ranks show absolute position, deciles divide areas into 10 equal groups."
                        ], className="text-start")
                    ], className="card-text", style={"listStylePosition": "inside", "paddingLeft": "0"})
                ], className="mb-4"),
                
                html.Div([
                    dbc.Button("Show Deprivation Data", id="btn-deprivation", color="primary", className="mt-3")
                ], className="text-center"),
                html.Div(id="deprivation-data-table", className="mt-3"),
                html.Div([
                    dbc.Pagination(
                        id="deprivation-pagination",
                        max_value=1,  # Will be updated by callback
                        first_last=True,
                        previous_next=True,
                        fully_expanded=False,
                        size="sm",
                        className="mt-3 justify-content-center"
                    )
                ], id="deprivation-pagination-container", style={"display": "none"})
            ], className="p-3")
        ])
    ])

def census_data():
    return dbc.Card([
        dbc.CardBody([
            html.H1("Census Data", className="card-title"),
            html.P("Explore ward-level demographic information from the latest census data for London.", className="card-text text-center mb-4"),
            
            # Description section
            html.Div([
                html.H4("About the Census Data", className="mt-3 text-center"),
                html.P("This dataset provides comprehensive demographic information at the ward level, including:", className="card-text text-center"),
                html.Ul([
                        html.Li([
                            html.Strong("Population Structure: "),
                            "Detailed breakdown of population by age groups (under 15, 15-64, 65+)"
                        ], className="text-center"),
                        html.Li([
                            html.Strong("Household Composition: "),
                            "Information about household types including single-person households and family structures"
                        ], className="text-center"),
                        html.Li([
                            html.Strong("Housing Types: "),
                            "Distribution of different housing types (detached, semi-detached, terraced, flats) and occupancy status"
                        ], className="text-center"),
                        html.Li([
                            html.Strong("Geographic Coverage: "),
                            "Data available at both LSOA (Lower Layer Super Output Area) and ward levels across London"
                        ], className="text-center")
                    ], className="card-text", style={"listStylePosition": "inside", "paddingLeft": "0"}),
                # Centered button
                html.Div([
                    dbc.Button("Show Census Data", id="btn-census", color="primary", className="mt-3")
                ], className="text-center"),
                
                # Data table container
                html.Div(id="census-data-table", className="mt-3")
            ], className="p-3")
        ])
    ])

def summarized_data():
    """
    Generates a summary view of burglary statistics across London wards.
    This function:
    1. Loads the most recent crime data
    2. Calculates ward-level statistics
    3. Computes population-standardized rates
    4. Displays the results in a dashboard format
    """
    # Load the most recent crime data
    try:
        # Generate list of available months from April 2022 to February 2025
        months = [f"{year}-{month:02d}" for year in range(2022, 2026) 
                 for month in range(1, 13) 
                 if not (year == 2022 and month < 4) and not (year == 2025 and month > 3)]
        
        # Get the two most recent months for comparison
        current_month = months[-1]  # Most recent month
        previous_month = months[-2]  # Second most recent month
        
        # Load crime data for both months
        current_data = load_crime_data(current_month)
        previous_data = load_crime_data(previous_month)
        
        # Filter data to focus only on burglary incidents
        current_burglaries = current_data[current_data["Crime type"] == "Burglary"]
        previous_burglaries = previous_data[previous_data["Crime type"] == "Burglary"]
        
        # Load census data and calculate total population for each ward
        census_df = load_census_data()
        population_ward_df = census_df.groupby('Ward name')['Total population'].sum().reset_index()
        
        # Calculate burglary counts for each ward
        # Merge census data with current burglaries to get ward-level statistics
        ward_counts = pd.merge(census_df, current_burglaries, on='LSOA name', how='inner')
        ward_counts = ward_counts.groupby('Ward name').size().reset_index(name='count')
        
        # Calculate population-standardized rates (burglaries per 1,000 people)
        ward_stats = pd.merge(ward_counts, population_ward_df, on='Ward name', how='left')
        ward_stats['rate_per_1000'] = (ward_stats['count'] / ward_stats['Total population']) * 1000
        
        # Sort wards by crime rate and format the statistics
        ward_stats = ward_stats.sort_values('rate_per_1000', ascending=False)
        ward_stats['rate_per_1000'] = ward_stats['rate_per_1000'].round(2)  # Round rates to 2 decimal places
        ward_stats['count'] = ward_stats['count'].astype(int)  # Convert counts to integers
        ward_stats['Total population'] = ward_stats['Total population'].astype(int)  # Convert population to integers
        
        # Calculate LSOA-level statistics
        # Get the LSOA with the highest number of burglaries
        lsoa_counts = current_burglaries.groupby('LSOA name').size().reset_index(name='count')
        lsoa_counts = lsoa_counts.sort_values('count', ascending=False)
        top_lsoa = lsoa_counts.iloc[0]  # Get the LSOA with most burglaries
        
        # Rename columns for better display in the table
        ward_stats.columns = ['Ward Name', 'Burglary Count', 'Population', 'Rate per 1,000']
        
        # Calculate overall statistics
        total_current = len(current_burglaries)  # Total burglaries in current month
        total_previous = len(previous_burglaries)  # Total burglaries in previous month
        total_growth = ((total_current - total_previous) / total_previous) * 100  # Calculate percentage change
        
    except Exception as e:
        # Handle any errors in data processing
        print(f"Error processing crime data: {str(e)}")
        return dbc.Card([
            dbc.CardBody([
                html.H1("Summarized Data", className="card-title text-center mb-4"),
                html.P("Error loading data. Please try again later.", className="text-danger text-center")
            ])
        ])

    # Create the dashboard layout
    return dbc.Card([
        dbc.CardBody([
            # Title and description
            html.H1("Summarized Data", className="card-title text-center mb-4"),
            html.P("Ward-level burglary statistics for the most recent month", className="card-text text-center mb-4"),
            
            # Time Period and Overview section
            html.Div([
                html.H4(f"Data Period: {current_month}", className="text-center text-muted mb-3"),
                html.Div([
                    html.Span(f"Total Burglaries: {total_current:,} ", className="me-4"),
                    html.Span(
                        f"Change from previous month: {total_growth:+.1f}%",
                        className=f"text-{'success' if total_growth < 0 else 'danger'}"  # Green for decrease, red for increase
                    )
                ], className="text-center mb-4")
            ]),
            
            # Top Areas Summary section - Shows most affected ward and LSOA
            dbc.Row([
                # Most affected ward card
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Most Affected Ward", className="text-center"),
                            html.H2(ward_stats.iloc[0]['Ward Name'], className="text-center text-primary"),
                            html.P(f"{ward_stats.iloc[0]['Burglary Count']} incidents", className="text-center"),
                            html.P(f"Rate: {ward_stats.iloc[0]['Rate per 1,000']} per 1,000 people", className="text-center text-muted")
                        ])
                    ], className="mb-3 shadow-sm")
                ], md=6),
                # Most affected LSOA card
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Most Affected Area (LSOA)", className="text-center"),
                            html.H2(top_lsoa['LSOA name'], className="text-center text-primary"),
                            html.P(f"{top_lsoa['count']} incidents", className="text-center")
                        ])
                    ], className="mb-3 shadow-sm")
                ], md=6)
            ], className="mb-4"),
            
            # Main table section - Shows ward-level statistics
            html.Div([
                dbc.Table.from_dataframe(
                    ward_stats,
                    striped=True,
                    bordered=True,
                    hover=True,
                    responsive=True,
                    className="table-dark mt-4"
                )
            ], style={
                'height': '600px',  # Fixed height for the table
                'overflowY': 'auto',  # Enable vertical scrolling
                'marginTop': '20px'
            }),
            
            # Key Insights section - Highlights important findings
            html.Div([
                html.H3("Key Insights", className="mb-3 text-center mt-4"),
                html.Ul([
                    # Insight about highest crime rate
                    html.Li([
                        html.Strong("Highest Rate: "),
                        f"{ward_stats.iloc[0]['Ward Name']} has the highest burglary rate at {ward_stats.iloc[0]['Rate per 1,000']} per 1,000 people."
                    ], className="mb-2"),
                    # Insight about most incidents
                    html.Li([
                        html.Strong("Most Incidents: "),
                        f"{ward_stats.loc[ward_stats['Burglary Count'].idxmax()]['Ward Name']} had the highest number of incidents with {ward_stats['Burglary Count'].max()} burglaries."
                    ], className="mb-2"),
                    # Insight about overall trend
                    html.Li([
                        html.Strong("Trend: "),
                        f"Overall burglary incidents have {'decreased' if total_growth < 0 else 'increased'} by {abs(total_growth):.1f}% compared to the previous month."
                    ], className="mb-2")
                ], className="card-text", style={"listStylePosition": "inside", "paddingLeft": "0"})
            ])
        ])
    ])

def forecasting():
    # Load ward information from the lookup file
    try:
        ward_df = pd.read_csv('data/lookups/look up LSOA 2021 to ward 2024 merged.csv')
        # Get unique ward codes and names
        ward_df = ward_df[['WD24CD', 'WD24NM']].drop_duplicates()
        # Add placeholder columns for predictions and resource allocation
        ward_df['Predicted Crime Count'] = ''
        ward_df['Resource Allocation'] = ''
        # Rename columns for display
        ward_df.columns = ['Ward Code', 'Ward Name', 'Predicted Crime Count', 'Resource Allocation']
    except Exception as e:
        print(f"Error loading ward data: {str(e)}")
        ward_df = pd.DataFrame(columns=['Ward Code', 'Ward Name', 'Predicted Crime Count', 'Resource Allocation'])

    return dbc.Card([
        dbc.CardBody([
            html.H1("Forecasting", className="card-title text-center mb-4"),
            html.P("This section will display predicted crime counts and recommended resource allocation for each ward in London.", className="card-text text-center mb-4"),
            
            # Description of the table
            html.Div([
                html.H4("Forecast Data", className="mt-3 text-center"),
                html.P("The table below shows ward-level predictions and resource allocation recommendations. These will be populated once the forecasting model is implemented.", className="card-text text-center"),
                
                # Search and sort controls
                html.Div([
                    # Search field
                    dbc.Input(
                        id="ward-search",
                        type="text",
                        placeholder="Search by ward name...",
                        className="mb-3",
                        style={"maxWidth": "300px", "margin": "0 auto"}
                    ),
                    
                    # Sort radio buttons
                    html.Div([
                        dbc.RadioItems(
                            id="sort-options",
                            options=[
                                {"label": "No Sort", "value": "none"},
                                {"label": "Sort by Predicted Crime Count", "value": "crime"},
                                {"label": "Sort by Resource Allocation", "value": "resource"}
                            ],
                            value="none",
                            inline=True,
                            className="mb-3"
                        )
                    ], className="text-center")
                ], className="text-center"),
                
                # Scrollable container for the table
                html.Div([
                    dbc.Table.from_dataframe(
                        ward_df,
                        striped=True,
                        bordered=True,
                        hover=True,
                        responsive=True,
                        className="table-dark mt-4",
                        id="forecast-table"
                    )
                ], style={
                    'height': '600px',  # Fixed height to show approximately 15 rows
                    'overflowY': 'auto',  # Enable vertical scrolling
                    'marginTop': '20px'
                })
            ], className="p-3")
        ])
    ])

def map_view():
    return dbc.Card([
        dbc.CardBody([
            html.H1("Map View", className="card-title"),
            html.P("Geospatial analysis of crime patterns.", className="card-text"),
            
            # Ward details section
            dbc.Row([
                dbc.Col(html.Div(id="ward1-details"), md=6),
                dbc.Col(html.Div(id="ward2-details"), md=6)
            ], className="mb-4"),

            # Filters section
            dbc.Row([
                dbc.Col(
                    [
                        html.Label("Filters for Map 1"),
                        dcc.Dropdown(
                            id="filter1",
                            options=[
                                {"label": "Select a filter", "value": None},
                                {"label": "IMD", "value": "imd"},
                                {"label": "Transportation Stops", "value": "transport"},
                                {"label": "Age", "value": "age"},
                                {"label": "Household Composition", "value": "household"},
                                {"label": "Accommodation Type", "value": "accommodation"}
                            ],
                            value=None
                        )
                    ]
               , md=6),
                dbc.Col(
                    [
                        html.Label("Filters for Map 2"),
                        dcc.Dropdown(
                            id="filter2",
                            options=[
                                {"label": "Select a filter", "value": None},
                                {"label": "IMD", "value": "imd"},
                                {"label": "Transportation Stops", "value": "transport"},
                                {"label": "Age", "value": "age"},
                                {"label": "Household Composition", "value": "household"},
                                {"label": "Accommodation Type", "value": "accommodation"}
                            ],
                            value=None
                        )
                    ]
               , md=6)
            ], className="filters mb-4"),

            # Map component
            dbc.Row([
                dbc.Col(dcc.Graph(id="map1", style={"height": "600px", "width": "100%"}), md=6),
                dbc.Col(dcc.Graph(id="map2", style={"height": "600px", "width": "100%"}), md=6)
            ])
        ])
    ])

# Callbacks for clickable map and ward details
def update_map(clickData, selected_filter, gdf_wards, df_burglaries, deprivation_df):

    selected_ward = None
    if clickData and "points" in clickData:
        selected_ward = clickData["points"][0].get("location")

    merged = gdf_wards.merge(df_burglaries, left_on="WD24CD", right_on="Ward code", how="left")

    if selected_filter == "imd" and deprivation_df is not None:
        # Standardize column names
        deprivation_df = deprivation_df.rename(columns={
            "Ward code": "WD24CD",
            "Index of Multiple Deprivation (IMD) Score": "imd_score"
        })
        merged = merged.merge(deprivation_df, on="WD24CD", how="left")
        # Drop one of the duplicate 'Ward name' columns and rename the other
        if 'Ward name_x' in merged.columns and 'Ward name_y' in merged.columns:
            merged = merged.drop(columns=["Ward name_x"])
            merged = merged.rename(columns={"Ward name_y": "Ward name"})
        
        merged["centroid"] = merged.geometry.centroid
        merged["lon"] = merged["centroid"].x
        merged["lat"] = merged["centroid"].y
        merged = merged.to_crs("EPSG:4326")

        fig = px.scatter_mapbox(
            merged,
            lat="lat",
            lon="lon",
            color="imd_score",
            color_continuous_scale="YlOrRd",
            size_max=15,
            zoom=9,
            mapbox_style="carto-positron",
            hover_name="WD24CD",
            hover_data=["imd_score", "Ward name"],
            opacity=0.7
        )
    else:
        # Fallback: highlight clicked ward
        merged["highlight"] = merged["WD24CD"].apply(
            lambda x: "Selected Ward" if x == selected_ward else "Other Wards"
        )
        fig = px.choropleth_mapbox(
            merged,
            geojson=json.loads(gdf_wards.to_crs("EPSG:4326").to_json()),
            locations="WD24CD",
            featureidkey="properties.WD24CD",
            color="highlight",
            color_discrete_map={
                "Other Wards": "#672DAA",
                "Selected Ward": "#C7C73B"
            },
            mapbox_style="carto-positron",
            center={"lat": 51.5, "lon": -0.1},
            zoom=9,
            opacity=0.6,
            hover_name="WD24NM"
        )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


@app.callback(
    [Output("ward1-details", "children"), Output("ward2-details", "children"), Output("map1", "figure"), Output("map2", "figure")],
    [Input("filter1", "value"), Input("filter2", "value"), Input("map1", "clickData"), Input("map2", "clickData")]
)

def update_ward_details(filter1, filter2, clickData1, clickData2):
    try:
        gdf_wards = gpd.read_file("data/boundaries/ward boundaries 2024/london_wards_merged.shp").to_crs("EPSG:4326")
        df_burglaries = pd.read_parquet('data/processed/burglaries.parquet')
        df_burglaries = df_burglaries[~df_burglaries['Ward code'].isin(['E05012399', 'E05015729'])]
    except Exception as e:
        return dbc.Card(), dbc.Card(), px.scatter_mapbox(title=f"Error loading data: {str(e)}"), px.scatter_mapbox(title=f"Error loading data: {str(e)}")

    ward1_details = dbc.Card([
        dbc.CardBody([
            html.P("Select ward on the map to inspect details.", className="text-muted mb-0")
        ])
    ])

    ward2_details = dbc.Card([
        dbc.CardBody([
            html.P("Select ward on the map to inspect details.", className="text-muted mb-0")
        ])
    ])

    if clickData1 and "points" in clickData1:
        ward_code = clickData1["points"][0].get("location")
        ward_name = clickData1["points"][0].get("hovertext", "Unknown Ward")
        ward1_details = dbc.Card([
            dbc.CardBody([
                html.H4(ward_name, className="card-title"),
                html.P("Predicted Crimes: 123", className="card-text"),  
                html.P("Recommended Resource Allocation: 2 patrol units", className="card-text"),
                dbc.Button("Inspect Details", id="inspect-details-btn", color="primary", className="mt-2")
            ])
        ])

    if clickData2 and "points" in clickData2:
        ward_code = clickData2["points"][0].get("location")
        ward_name = clickData2["points"][0].get("hovertext", "Unknown Ward")
        ward2_details = dbc.Card([
            dbc.CardBody([
                html.H4(ward_name, className="card-title"),
                html.P("Predicted Crimes: 123", className="card-text"),
                html.P("Recommended Resource Allocation: 2 patrol units", className="card-text"),
                dbc.Button("Inspect Details", id="inspect-details-btn", color="primary", className="mt-2")
            ])
        ])

    deprivation_df = load_deprivation_data()
    fig1 = update_map(clickData1, filter1, gdf_wards, df_burglaries, deprivation_df)
    fig2 = update_map(clickData2, filter2, gdf_wards, df_burglaries, deprivation_df)



    return ward1_details, ward2_details, fig1, fig2

def about():
    return dbc.Card([
        dbc.CardBody([
            html.H1("About", className="card-title text-center mb-4"),
            
            # Project Overview
            html.Div([
                html.H3("Project Overview", className="mb-3 text-center"),
                html.P("This Police Demand Forecasting project aims to improve resource allocation and crime prevention strategies in London by analyzing burglary patterns and predicting future trends. The project combines crime data with demographic and deprivation information to provide actionable insights for law enforcement.", className="card-text text-center")
            ], className="mb-4"),
            
            # Data Sources
            html.Div([
                html.H3("Data Sources", className="mb-3 text-center"),
                html.Ul([
                    html.Li("Crime data from Metropolitan Police (2022-2025)", className="text-center"),
                    html.Li("Census data from the Office for National Statistics", className="text-center"),
                    html.Li("Deprivation indices from the UK government", className="text-center"),
                    html.Li("Ward boundaries and geographical data", className="text-center")
                ], className="card-text", style={"listStyle": "none", "padding": "0"})
            ], className="mb-4"),
            
            # Technical Stack
            html.Div([
                html.H3("Technical Stack", className="mb-3 text-center"),
                html.Ul([
                    html.Li("Python - Main programming language", className="text-center"),
                    html.Li("Dash and Plotly - Interactive dashboard", className="text-center"),
                    html.Li("Pandas - Data manipulation", className="text-center"),
                    html.Li("GeoPandas - Spatial analysis", className="text-center"),
                    html.Li("Other key libraries for data analysis and visualization", className="text-center")
                ], className="card-text", style={"listStyle": "none", "padding": "0"})
            ], className="mb-4"),
            
            # Key Features
            
            # Project Timeline
            html.Div([
                html.H3("Project Timeline", className="mb-3 text-center"),
                html.Ul([
                    html.Li("Project Start: 2025", className="text-center"),
                    html.Li("Data Collection and Processing", className="text-center"),
                    html.Li("Dashboard Development", className="text-center"),
                    html.Li("Analysis and Forecasting Implementation", className="text-center"),
                    html.Li("Future: Enhanced prediction models and real-time updates", className="text-center")
                ], className="card-text", style={"listStyle": "none", "padding": "0"})
            ], className="mb-4"),
            
            # Acknowledgments
            html.Div([
                html.H3("Acknowledgments", className="mb-3 text-center"),
                html.P("Special thanks to:", className="card-text text-center"),
                html.Ul([
                    html.Li("Hetvi Chaniyara for the guidance", className="text-center"),
                    html.Li("Metropolitan Police for crime data", className="text-center"),
                    html.Li("Office for National Statistics", className="text-center"),
                    html.Li("Trinity College London for support and resources", className="text-center"),
                    html.Li("All team members and contributors", className="text-center")
                ], className="card-text", style={"listStyle": "none", "padding": "0"})
            ], className="mb-4"),
            
            # Contact Information
            html.Div([
                html.H3("Contact", className="mb-3 text-center"),
                html.P("For more information about this project, please contact:", className="card-text text-center"),
                html.P("nikolapanayotov04@gmail.com", className="card-text text-center"),
            ], className="mb-4"),
            
            # Footer
            html.Footer("Project developed by team 31(Fantastic Four):", 
                        style={"fontSize": "0.85rem", "color": "#aaa", "marginTop": "2rem", "textAlign": "center"})
        ], style={"maxWidth": "800px", "margin": "0 auto"})  # Center the card body content
    ])


# Final layout with sidebar + content
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),  # Track URL
    
    dbc.Row([
        sidebar,                   # Your left menu
        dbc.Col(id='page-content', width=10)  # Dynamic content goes here
    ])
], fluid=True)

@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/":
        return homepage()
    elif pathname == "/data":
        return data_explorer()
    elif pathname == "/data/crime":
        return crime_data()
    elif pathname == "/data/deprivation":
        return deprivation_data()
    elif pathname == "/data/census":
        return census_data()
    elif pathname == "/data/summary":
        return summarized_data()
    elif pathname == "/forecast":
        return forecasting()
    elif pathname == "/map":
        return map_view()
    elif pathname == "/about":
        return about()
    else:
        return html.H1("404 - Page not found")

# Callbacks for data display
@app.callback(
    [Output("crime-data-table", "children"),
     Output("crime-data-error", "children")],
    [Input("month-picker", "value")],
    prevent_initial_call=True
)
def display_crime_data(month):
    if month:
        try:
            # Validate month format
            year, month_num = map(int, month.split('-'))
            
            # Check if date is within valid range
            if (year == 2022 and month_num < 4) or year < 2022 or (year == 2025 and month_num > 3) or year > 2025:
                return None, "Selected month is out of range. Please select a month between April 2022 and February 2025."
            
            # Load data for selected month
            crime_df = load_crime_data(month)
            filterd_crime_df = crime_df[crime_df["Crime type"] == "Burglary"]
            
            if not crime_df.empty:
                # Create attribute descriptions
                attribute_descriptions = html.Div([
                    html.H4("Data Attributes", className="mt-4 mb-3 text-start"),
                    html.Ul([
                        html.Li([
                            html.Strong("Crime ID: "),
                            "Unique identifier for each crime incident"
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Month: "),
                            "The month when the crime was reported"
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Reported by: "),
                            "The police force that recorded the crime"
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Falls within: "),
                            "The police force responsible for the area"
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Longitude & Latitude: "),
                            "Geographic coordinates of the crime location"
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Location: "),
                            "Street name or area where the crime occurred"
                        ], className="text-start"),
                        html.Li([
                            html.Strong("LSOA code & name: "),
                            "Lower Layer Super Output Area identifier and name"
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Crime type: "),
                            "Category of the crime committed"
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Last outcome category: "),
                            "The most recent status or resolution of the case"
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Context: "),
                            "Additional information about the crime incident"
                        ], className="text-start")
                    ], className="card-text", style={"listStylePosition": "inside", "paddingLeft": "0"})
                ], className="mb-4")

                return (
                    html.Div([
                        attribute_descriptions,
                        dbc.Table.from_dataframe(
                            filterd_crime_df.head(10),
                            striped=True,
                            bordered=True,
                            hover=True,
                            responsive=True,
                            className="table-dark"
                        )
                    ]),
                    ""
                )
            else:
                return None, f"No data available for {month}"
        except Exception as e:
            return None, f"Error loading data: {str(e)}"
    return None, ""

@app.callback(
    [Output("deprivation-data-table", "children"),
     Output("deprivation-pagination", "max_value"),
     Output("deprivation-pagination-container", "style")],
    [Input("btn-deprivation", "n_clicks"),
     Input("deprivation-pagination", "active_page")],
    prevent_initial_call=True
)
def display_deprivation_data(n_clicks, page):
    if not n_clicks:
        return None, 1, {"display": "none"}
    deprivation_df = load_deprivation_data()
    # Only show data on odd clicks
    if n_clicks % 2 == 1:
        if not deprivation_df.empty:
            # Calculate total number of pages (10 rows per page)
            rows_per_page = 10
            total_pages = (len(deprivation_df) + rows_per_page - 1) // rows_per_page
            
            # Get the current page (default to 1 if None)
            current_page = page if page is not None else 1
            
            # Calculate start and end indices for the current page
            start_idx = (current_page - 1) * rows_per_page
            end_idx = min(start_idx + rows_per_page, len(deprivation_df))
            
            # Get the data for the current page
            page_data = deprivation_df.iloc[start_idx:end_idx]
            
            return [
                dbc.Table.from_dataframe(
                    page_data,
                    striped=True,
                    bordered=True,
                    hover=True,
                    responsive=True,
                    className="table-dark"
                ),
                total_pages,
                {"display": "block"}
            ]
        else:
            return [
                html.Div("No deprivation data available", className="text-danger"),
                1,
                {"display": "none"}
            ]
    else:  # Hide data on even clicks
        return None, 1, {"display": "none"}

@app.callback(
    Output("census-data-table", "children"),
    Input("btn-census", "n_clicks"),
    prevent_initial_call=True
)
def display_census_data(n_clicks):
    census_df = load_census_data()
    if n_clicks and n_clicks % 2 == 1:  # Show data on odd clicks
        if not census_df.empty:
            return dbc.Table.from_dataframe(
                census_df.head(10),
                striped=True,
                bordered=True,
                hover=True,
                responsive=True,
                className="table-dark"
            )
        else:
            return html.Div("No census data available", className="text-danger")
    else:  # Hide data on even clicks
        return None

# Add callback to control submenu visibility
@app.callback(
    Output("data-explorer-submenu", "style"),
    Input("url", "pathname")
)
def toggle_data_explorer_submenu(pathname):
    if pathname in ["/data", "/data/crime", "/data/deprivation", "/data/census"]:
        return {"display": "block"}
    return {"display": "none"}

# Add callback for ward search and sorting
@app.callback(
    Output("forecast-table", "children"),
    [Input("ward-search", "value"),
     Input("sort-options", "value")]
)
def filter_and_sort_wards(search_value, sort_option):
    try:
        ward_df = pd.read_csv('data/lookups/look up LSOA 2021 to ward 2024 merged.csv')
        ward_df = ward_df[['WD24CD', 'WD24NM']].drop_duplicates()
        ward_df['Predicted Crime Count'] = ''
        ward_df['Resource Allocation'] = ''
        ward_df.columns = ['Ward Code', 'Ward Name', 'Predicted Crime Count', 'Resource Allocation']
        
        # Filter based on search
        if search_value:
            ward_df = ward_df[ward_df['Ward Name'].str.contains(search_value, case=False, na=False)]
        
        # Sort based on radio selection
        if sort_option == "crime":
            ward_df = ward_df.sort_values('Predicted Crime Count', ascending=False)
        elif sort_option == "resource":
            ward_df = ward_df.sort_values('Resource Allocation', ascending=False)
        # If sort_option is "none", no sorting is applied
        
        return dbc.Table.from_dataframe(
            ward_df,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            className="table-dark mt-4"
        )
    except Exception as e:
        print(f"Error in ward search/sort: {str(e)}")
        return None

if __name__ == '__main__':
    app.run(debug=False)  # Change debug to False to hide debug messages
