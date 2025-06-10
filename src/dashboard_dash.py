import dash
from dash import html
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
import plotly.graph_objects as go
import geopandas as gpd
import json
import numpy as np


app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG,
        'assets/custom_dashboard_dash.css'  # Updated path to be relative to src directory
    ],
    suppress_callback_exceptions=True  # Add this line to suppress callback exceptions
)
app.title = "Police Forecasting Dashboard"


# Data loading functions
def load_crime_data(month=None):
    try:
        if month is None:
            # Default to most recent month
            month = "2022-04"

        # Construct file path
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

def load_borough_data():
    try:
        # Construct file path
        file_path = 'data/lookups/Look up LSOA 2011 to LSOA 2021.csv'

        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            print(f"File not found: {file_path}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error loading crime data: {str(e)}")
        return pd.DataFrame()

def load_census_data():
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


# Sidebar menu
sidebar = html.Div(
    [
        html.H4("Menu", className="text-white mt-4 mb-4", style={"paddingLeft": "1rem"}),
        html.Hr(style={"borderColor": "rgba(255,255,255,0.2)"}),
        dbc.Nav([
            dbc.NavLink("Home", href="/", active="exact", className="nav-link ps-3"),
            dbc.NavLink("Data Explorer", href="/data", active="exact", className="nav-link ps-3"),
            html.Div(id="data-explorer-submenu", style={"display": "none"}, children=[
                dbc.NavLink("Crime Data", href="/data/crime", active="exact", className="nav-link ps-5"),
                dbc.NavLink("Deprivation Data", href="/data/deprivation", active="exact", className="nav-link ps-5"),
                dbc.NavLink("Census Data", href="/data/census", active="exact", className="nav-link ps-5"),
                dbc.NavLink("Summarized Data", href="/data/summary", active="exact", className="nav-link ps-5"),
            ]),
            dbc.NavLink("Forecasting", href="/forecast", active="exact", className="nav-link ps-3"),
            dbc.NavLink("Map View", href="/map", active="exact", className="nav-link ps-3"),
            dbc.NavLink("About", href="/about", active="exact", className="nav-link ps-3"),
        ], vertical=True, pills=True),
    ],
    style={
        "position": "fixed",
        "top": 0,
        "left": 0,
        "height": "100vh",
        "overflowY": "auto",
        "paddingTop": "1rem",
        "paddingBottom": "1rem",
        "paddingRight": "0.5rem",
        "paddingLeft": 0,
        "backgroundColor": "#212529",
        "zIndex": 1000,
        "width": "250px",
        "boxShadow": "2px 0 5px rgba(0,0,0,0.3)",
    },
    className="sidebar"
)

# Main content area
from dash import html
import dash_bootstrap_components as dbc

def homepage():
    return html.Div([
        # Title Section
        html.Div([
            dbc.Row([
                dbc.Col(html.Img(src="/assets/metropolitan_police_service_logo.png",
                                 style={"height": "70px", "objectFit": "contain"}), width="auto"),
                dbc.Col([
                    html.H1(
                        "SAFEWARD",
                        className="display-4 fw-bold",
                        style={
                            "textTransform": "uppercase",
                            "letterSpacing": "2px",
                            "marginBottom": "0.3rem",
                            "fontSize": "60px"
                        }
                    ),
                    html.P(
                        "Welcome to the Police Demand Forecasting Dashboard.",
                        className="lead",
                        style={"fontWeight": "500", "color": "#e0e0e0"}
                    )
                ], className="text-center"),
                dbc.Col(html.Img(src="/assets/city_of_london_police_logo.png",
                                 style={"height": "80px", "objectFit": "contain"}), width="auto"),
            ], align="center", justify="between"),
        ], style={
            "backgroundColor": "#000000",
            "color": "white",
            "textAlign": "center",
            "boxShadow": "0 8px 16px rgba(26, 35, 126, 0.4)",
            "width": "100%",
            "marginLeft": "250px",
            "padding": "2.5rem 2rem"
        }),

        # Main Content Container (with sidebar margin)
        dbc.Container([

            # 2x2 Grid of Cards
            dbc.Row([
                # Stakeholders and Scope
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("️Stakeholders and Scope", className="mb-3 fw-semibold"),
                            html.Ul([
                                html.Li(html.Span(
                                    [html.B("For: "), "Metropolitan Police Service & City of London Police"])),
                                html.Li(html.Span([html.B("Crime: "), "Burglaries"])),
                                html.Li(html.Span([html.B("Area: "), "Greater London"])),
                            ])
                        ])
                    ]),
                    width=6,
                    className="mb-4"
                ),
                # Problem Description
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Problem Description", className="mb-3 fw-semibold"),
                            html.Ol([
                                html.Li([
                                    html.B("High Prevalence: "),
                                    "Residential burglary accounts for 4.5% of all crimes in Greater London."
                                ]),
                                html.Li([
                                    html.B("Low Resolution Rate: "),
                                    "82% of residential burglaries went unsolved in 2022/2023, highlighting gaps in current policing effectiveness."
                                ]),
                                html.Li([
                                    html.B("Eroding Public Trust: "),
                                    "The combination of frequency and lack of resolution undermines public confidence in police protection and safety."
                                ]),
                            ])
                        ])
                    ]),
                    width=6,
                    className="mb-4"
                ),
            ]),

            dbc.Row([

                # Goals
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Goals", className="mb-3 fw-semibold"),
                            html.P(html.I(
                                "Transforming static, reactive responses into dynamic, predictive strategies for smarter crime prevention.")),
                            html.Ol([
                                html.Li("Develop an automated police demand forecasting system."),
                                html.Li("Reduce residential burglary through improved predictive capabilities."),
                                html.Li("Ensure efficient and effective resource allocation."),
                            ])
                        ])
                    ]),
                    width=6,
                    className="mb-4"
                ),

                # How to use this tool
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("How to Use This Tool", className="mb-3 fw-semibold"),
                            html.Ol([
                                html.Li(
                                    "Explore crime, deprivation, and census data to understand contributing factors."),
                                html.Li("Review summarized data for quick insights."),
                                html.Li("Access forecasts to see expected burglary rates by ward and time."),
                                html.Li("Use the map view to guide patrol planning and resource distribution.")
                            ])
                        ])
                    ]),
                    width=6,
                    className="mb-4"
                ),
            ]),

            html.Hr(),

            # Image
            html.Div([
                html.Img(src="/assets/london_image.jpg",
                         style={"width": "100%", "maxWidth": "800px", "margin": "40px auto", "display": "block", "borderRadius": "12px"}),
            ]),

            html.Hr(),

            # Contributors
            dbc.Row([
                dbc.Col([
                    html.H6("Contributors", className="text-muted"),
                    html.H6("Team members from Eindhoven University of Technology"),
                    html.Ul([
                        html.Li("Niki Panayotov"),
                        html.Li("Jan Galic"),
                        html.Li("Pantelis Hadjipanayiotou"),
                        html.Li("Trinity Jan"),
                    ])
                ], width=12)
            ], className="mb-3"),

            html.Footer("Project developed by Team 31 – Fantastic Four",
                        style={"fontSize": "0.85rem", "color": "#999", "textAlign": "center", "marginBottom": "0.5rem"})

        ], fluid=True, style={"marginLeft": "250px", "padding": "2rem 3rem"})
    ])

def data_explorer():
    return dbc.Card([
        dbc.CardBody([
            html.H1("Data Explorer", className="card-title"),
            html.P(
                "Welcome to the Data Explorer section. Here you can access and analyze various datasets related to police demand forecasting in London.",
                className="card-text text-center"),
            html.P("Our datasets include:", className="card-text mt-4 text-center"),
            html.Div([
                html.Ul([
                    html.Li("Crime Data: Monthly burglary statistics across London boroughs from 2022 to 2025",
                            className="text-center"),
                    html.Li(
                        "Deprivation Data: Measure relative deprivation in small areas",
                        className="text-center"),
                    html.Li("Census Data: Information about population demography, household composition, dwelling occupancy, and dwelling characteristics",
                            className="text-center"),
                    html.Li("Summarized Data: Key insights and aggregated statistics from all datasets",
                            className="text-center")
                ], className="card-text mb-4", style={"listStyle": "none", "padding": "0"})
            ], className="d-flex justify-content-center"),
            html.P("Select a dataset below to begin exploring:", className="card-text text-center"),
            html.Div([
                dbc.Button("Crime Data", href="/data/crime", color="primary", className="me-3"),
                dbc.Button("Deprivation Data", href="/data/deprivation", color="primary", className="me-3"),
                dbc.Button("Census Data", href="/data/census", color="primary", className="me-3"),
                dbc.Button("Summarized Data", href="/data/summary", color="primary", className="me-3"),
            ], className="mt-4 text-center")
        ])
    ], style={"marginLeft": "250px", "width": "100%"})



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
                        if not (year == 2022 and month < 4) and not (year == 2025 and month > 3)
                        # Only show from Apr 2022 to Feb 2025
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
    ], style={"marginLeft": "250px", "width": "100%"})

import dash_bootstrap_components as dbc
from dash import html, Input, Output, callback
from dash import dash_table

def deprivation_data():
    return dbc.Card([
        dbc.CardBody([
            html.H1("Deprivation Data", className="card-title"),
            html.P("Explore The English Indices of Deprivation 2019 for London.", className="card-text text-center mb-4"),

            html.Div([
                # Attribute descriptions
                html.Div([
                    html.H4("About Data Attributes", className="mt-4 mb-3 text-start"),
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
                            html.Strong("Education, Skills and Training Domain: "),
                            "Measures lack of attainment and skills in the local population."
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Health Deprivation and Disability Domain: "),
                            "Measures morbidity, disability, and premature mortality."
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Crime Domain: "),
                            "Measures recorded crime rates for violence, burglary, theft, and criminal damage."
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Barriers to Housing and Services Domain: "),
                            "Measures physical and financial accessibility to housing and key local services."
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Living Environment Domain: "),
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

                # Show data button
                html.Div([
                    dbc.Button("Show Deprivation Data", id="btn-deprivation", color="primary", className="mt-3")
                ], className="text-center"),

                # Content container that appears after button click
                html.Hr(),

                html.Div([

                    # LSOA-Ward toggle
                    html.Div([
                        html.H5("Choose Data Level", className="mt-4 mb-2"),
                        dbc.Row([
                            dbc.Col(html.Div("LSOA", className="text-end"), width="auto"),
                            dbc.Col(
                                dbc.Checklist(
                                    options=[{"label": "", "value": "ward"}],
                                    value=[],  # unchecked means LSOA
                                    id="deprivation-toggle",
                                    switch=True,
                                    className="mx-3",
                                    inline=True,
                                ),
                                width="auto",
                                className="d-flex align-items-center"
                            ),
                            dbc.Col(html.Div("Ward", className="text-start"), width="auto"),
                        ], justify="center", align="center", className="mb-4"),
                        html.Small(
                            "Toggle to switch between LSOA-level (off) and Ward-level (on) data.",
                            className="text-muted"
                        ),
                    ], className="text-center"),

                    # Deprivation Table
                    html.Div(id="deprivation-data-table"),
                ], id="deprivation-content", style={"display": "none"})  # Initially hidden
            ], className="p-3")
        ])
    ], style={"marginLeft": "250px", "width": "100%"})


def census_data():
    return dbc.Card([
        dbc.CardBody([
            html.H1("Census Data", className="card-title"),
            html.P("Explore 2021 census data for London.",
                   className="card-text text-center mb-4"),

            # Description section
            html.Div([
                html.H4("About Data Attributes", className="mt-4 mb-3 text-start"),

                html.Ul([
                    html.Li([
                        html.Strong("Population Demography: "),
                        "Detailed breakdown of population by age groups (under 15, 15-64, 65+)"
                    ], className="text-start"),
                    html.Li([
                        html.Strong("Household Composition: "),
                        "Breakdown of household composition including single-person households and family structures"
                    ], className="text-start"),
                    html.Li([
                        html.Strong("Dwelling Types: "),
                        "Distribution of different dwelling types (detached, semi-detached, terraced, flats)"
                    ], className="text-start"),
                    html.Li([
                        html.Strong("Occupancy Rating: "),
                        "Breaks down total number of dwellings into occupied and unoccupied dwellings"
                    ], className="text-start"),

                ], className="card-text", style={"listStylePosition": "inside", "paddingLeft": "0"}),
                # Centered button
                html.Div([
                    dbc.Button("Show Census Data", id="btn-census", color="primary", className="mt-3")
                ], className="text-center"),

                html.Hr(),

                html.Div([

                    # LSOA-Ward toggle
                    html.Div([
                        html.H5("Choose Data Level", className="mt-4 mb-2"),
                        dbc.Row([
                            dbc.Col(html.Div("LSOA", className="text-end"), width="auto"),
                            dbc.Col(
                                dbc.Checklist(
                                    options=[{"label": "", "value": "ward"}],
                                    value=[],  # unchecked means LSOA
                                    id="census-toggle",
                                    switch=True,
                                    className="mx-3",
                                    inline=True,
                                ),
                                width="auto",
                                className="d-flex align-items-center"
                            ),
                            dbc.Col(html.Div("Ward", className="text-start"), width="auto"),
                        ], justify="center", align="center", className="mb-4"),
                        html.Small(
                            "Toggle to switch between LSOA-level (off) and Ward-level (on) data.",
                            className="text-muted"
                        ),
                    ], className="text-center"),

                    # Deprivation Table
                    html.Div(id="census-data-table"),
                ], id="census-content", style={"display": "none"})  # Initially hidden
            ], className="p-3")
        ])
    ], style={"marginLeft": "250px", "width": "100%"})


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
            html.P(
                "This section will display predicted crime counts and recommended resource allocation for each ward in London.",
                className="card-text text-center mb-4"),

            # Description of the table
            html.Div([
                html.H4("Forecast Data", className="mt-3 text-center"),
                html.P(
                    "The table below shows ward-level predictions and resource allocation recommendations. These will be populated once the forecasting model is implemented.",
                    className="card-text text-center"),

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
    ], style={"marginLeft": "250px", "width": "100%"})


deprivation_df = load_deprivation_data()
burglaries_df = pd.read_parquet("data/processed/burglaries.parquet")
stop_counts_df = pd.read_csv("data/processed/stop_counts_per_ward.csv")
gdf_wards = gpd.read_file("data/boundaries/ward boundaries 2024/london_wards_merged.shp").to_crs("EPSG:4326")
forecasts_df = pd.read_csv("data/processed/ward_hour_allocation_LP_method.csv")
crime_counts_df = pd.read_csv("data/processed/monthly_burglary_per_ward.csv")

# --- Map View Layout ---
def map_view():
    return dbc.Card([
        dbc.CardBody([
            html.H1("Map View", className="card-title"),
            html.P("Geospatial analysis of crime patterns.", className="card-text"),

            dbc.Row([
                dbc.Col(html.Div(id="ward1-details"), md=6),
                dbc.Col(html.Div(id="ward2-details"), md=6)
            ], className="mb-4"),

            dbc.Row([
                dbc.Col(
                    dcc.Loading(
                        id="loading-map1",
                        type="circle",
                        children=dcc.Graph(id="map1", style={"height": "600px", "width": "100%"})
                    ),
                    md=6
                ),
                dbc.Col(
                    dcc.Loading(
                        id="loading-map2",
                        type="circle",
                        children=dcc.Graph(id="map2", style={"height": "600px", "width": "100%"})
                    ),
                    md=6
                )
            ])
        ])
    ], style={"marginLeft": "250px", "width": "100%"})


# --- Callback ---
@app.callback(
    [Output("ward1-details", "children"),
     Output("ward2-details", "children"),
     Output("map1", "figure"),
     Output("map2", "figure")],
    [Input("map1", "clickData"),
     Input("map2", "clickData")]
)
def update_ward_details(clickData1, clickData2):
    fig1 = update_map(clickData1, gdf_wards, burglaries_df)
    fig2 = update_map(clickData2, gdf_wards, burglaries_df)

    return (
        generate_details(clickData1, deprivation_df, stop_counts_df),
        generate_details(clickData2, deprivation_df, stop_counts_df),
        fig1,
        fig2
    )


def update_map(clickData, gdf_wards, df_burglaries):
    selected_ward = clickData["points"][0].get("location") if clickData and "points" in clickData else None

    merged = gdf_wards.merge(df_burglaries, left_on="WD24CD", right_on="Ward code", how="left")
    merged["highlight"] = merged["WD24CD"].apply(lambda x: "Selected Ward" if x == selected_ward else "Other Wards")

    fig = px.choropleth_mapbox(
        merged,
        geojson=json.loads(gdf_wards.to_crs("EPSG:4326").to_json()),
        locations="WD24CD",
        featureidkey="properties.WD24CD",
        color="highlight",
        color_discrete_map={"Other Wards": "#672DAA", "Selected Ward": "#C7C73B"},
        mapbox_style="carto-positron",
        center={"lat": 51.5, "lon": -0.1},
        zoom=9,
        opacity=0.6,
        hover_name="WD24NM"
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def get_stop_count(ward_code, stop_counts_df):
    match = stop_counts_df.loc[stop_counts_df["Ward code"] == ward_code, "stop_count"]
    return int(match.values[0]) if not match.empty else "N/A"


def generate_details(clickData, deprivation_df, stop_counts_df):
    if clickData and "points" in clickData:
        ward_code = clickData["points"][0].get("location")
        ward_name = clickData["points"][0].get("hovertext", "Unknown Ward")


        previous_month_crimes = crime_counts_df.loc[(crime_counts_df["Ward code"] == ward_code) & (crime_counts_df["Month"] == "2025-03-01"), "burglary_count"].values
        previous_month_crimes = previous_month_crimes[0] if len(previous_month_crimes) > 0 else 0

        predicted_crimes = forecasts_df.loc[forecasts_df["Ward code"] == ward_code, "Predicted_Crime_Count"].values
        predicted_crimes = round(predicted_crimes[0], 2) if len(predicted_crimes) > 0 else "N/A"

        diff = round(predicted_crimes - previous_month_crimes, 2) if isinstance(predicted_crimes, (float, int)) else "N/A"
        trend_arrow = "↑" if diff > 0 else "↓"
        trend_color = "text-danger" if diff > 0 else "text-success"

        resource_allocation = forecasts_df.loc[forecasts_df["Ward code"] == ward_code, "Allocated_Officers_Rounded"].values
        resource_allocation = int(resource_allocation[0]) if len(resource_allocation) > 0 else "N/A"

        imd_score = deprivation_df.loc[deprivation_df["Ward code"] == ward_code, "Index of Multiple Deprivation (IMD) Score"].values
        imd_score = round(imd_score[0], 2) if len(imd_score) > 0 else "N/A"

        transport_stops = get_stop_count(ward_code, stop_counts_df)

        return dbc.Card([
            dbc.CardBody([
                html.H4(ward_name, className="card-title mb-4"),
                dbc.Row([
                    dbc.Col([
                        html.Div("Predicted Crimes", className="text-muted"),
                        html.Div([
                            html.Span(f"{predicted_crimes} ", className="fs-3 fw-bold me-2"),
                            html.Span(f"{trend_arrow} {abs(diff)}", className=f"fs-5 {trend_color}")
                        ])
                    ], width=6),
                    dbc.Col([
                        html.Div("Resource Recommendation", className="text-muted"),
                        html.Span(f"{resource_allocation} policing hours", className="fs-3 fw-bold me-2"),
                    ], width=6)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Div("IMD Score", className="text-muted"),
                        html.Div(imd_score, className="fs-3 fw-bold")
                    ], width=6),
                    dbc.Col([
                        html.Div("Transport Stops", className="text-muted"),
                        html.Div(transport_stops, className="fs-3 fw-bold")
                    ], width=6)
                ]),
            ])
        ])
    else:
        return dbc.Card([
            dbc.CardBody([
                html.P("Select ward on the map to inspect details.", className="text-muted mb-0")
            ])
        ])


def about():
    return dbc.Card([
        dbc.CardBody([
            html.H1("About", className="card-title text-center mb-4"),

            # Project Overview
            html.Div([
                html.H3("Project Overview", className="mb-3 text-center"),
                html.P(
                    "This Police Demand Forecasting project aims to improve resource allocation and crime prevention strategies in London by analyzing burglary patterns and predicting future trends. The project combines crime data with demographic and deprivation information to provide actionable insights for law enforcement.",
                    className="card-text text-center")
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
    ], style={"marginLeft": "250px", "width": "100%"})


# Final layout with sidebar + content
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),  # Track URL

    dbc.Row([
        sidebar,  # Your left menu
        dbc.Col(id='page-content', width=10)  # Dynamic content goes here
    ])
], fluid=True)


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
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


def summarized_data():
    # Get list of available months
    months = []
    for year in range(2022, 2026):
        for month in range(1, 13):
            if (year == 2022 and month < 4) or (year == 2025 and month > 3):
                continue
            months.append(f"{year}-{month:02d}")

    # Set default month to March 2025
    default_month = "2025-03"

    return dbc.Card([
        dbc.CardBody([
            html.H1("Summarized Data", className="card-title text-center mb-4"),
            html.P("Ward-level burglary statistics", className="card-text text-center mb-4"),

            # Month picker
            html.Div([
                dcc.Dropdown(
                    id='summary-month-picker',
                    options=[{'label': month, 'value': month} for month in months],
                    value=default_month,
                    clearable=False,
                    className="mb-4",
                    style={'width': '200px', 'margin': '0 auto'}
                )
            ], className="text-center"),

            # Content container that will be updated by the callback
            html.Div(id="summarized-data-content", children=update_summarized_data(default_month, 'rate', 'rate'))
        ])
    ], style={"marginLeft": "250px", "width": "100%"})

@app.callback(
    Output("summarized-data-content", "children"),
    [Input("summary-month-picker", "value"),
     Input("borough-sort-options", "value"),
     Input("ward-sort-options", "value")],
    prevent_initial_call=True
)
def update_summarized_data(selected_month, borough_sort, ward_sort):
    if not selected_month:
        selected_month = "2025-03"  # Default to March 2025 if no month selected
    if not borough_sort:
        borough_sort = 'rate'  # Default to rate sorting
    if not ward_sort:
        ward_sort = 'rate'  # Default to rate sorting

    try:
        # Get list of available months
        months = []
        for year in range(2022, 2026):
            for month in range(1, 13):
                if (year == 2022 and month < 4) or (year == 2025 and month > 3):
                    continue
                months.append(f"{year}-{month:02d}")

        # Find the index of the selected month
        month_index = months.index(selected_month)
        if month_index > 0:
            previous_month = months[month_index - 1]
        else:
            previous_month = selected_month

        # Load data for both months
        current_data = load_crime_data(selected_month)
        previous_data = load_crime_data(previous_month)
        borough_data = load_borough_data()

        # Filter for burglaries
        current_burglaries = current_data[current_data["Crime type"] == "Burglary"]
        previous_burglaries = previous_data[previous_data["Crime type"] == "Burglary"]

        # Load census data and calculate ward populations
        census_df = load_census_data()
        population_ward_df = census_df.groupby('Ward name')['Total population'].sum().reset_index()

        # Get ward statistics for both months
        current_ward_counts = pd.merge(census_df, current_burglaries, on='LSOA name', how='inner')
        current_ward_counts = pd.merge(current_ward_counts, borough_data, left_on='LSOA code_x', right_on='LSOA21CD')
        current_ward_counts = current_ward_counts.groupby(['Ward name', 'LAD22NM']).size().reset_index(name='current_count')

        previous_ward_counts = pd.merge(census_df, previous_burglaries, on='LSOA name', how='inner')
        previous_ward_counts = pd.merge(previous_ward_counts, borough_data, left_on='LSOA code_x', right_on='LSOA21CD')
        previous_ward_counts = previous_ward_counts.groupby(['Ward name', 'LAD22NM']).size().reset_index(name='previous_count')

        # Get LSOA statistics for both months
        current_lsoa_counts = current_burglaries.groupby('LSOA name').size().reset_index(name='current_count')
        previous_lsoa_counts = previous_burglaries.groupby('LSOA name').size().reset_index(name='previous_count')

        # Calculate growth and rates
        ward_stats = pd.merge(current_ward_counts, population_ward_df, on='Ward name', how='left')
        ward_stats = pd.merge(ward_stats, previous_ward_counts, on=['Ward name', 'LAD22NM'], how='left')
        ward_stats['previous_count'] = ward_stats['previous_count'].fillna(0)
        ward_stats['rate_per_1000'] = (ward_stats['current_count'] / ward_stats['Total population']) * 1000
        ward_stats['growth'] = ((ward_stats['current_count'] - ward_stats['previous_count']) / ward_stats['previous_count']) * 100
        ward_stats['growth'] = ward_stats['growth'].replace([np.inf, -np.inf], np.nan).fillna(0)

        # Calculate LSOA growth
        lsoa_stats = pd.merge(current_lsoa_counts, previous_lsoa_counts, on='LSOA name', how='left')
        lsoa_stats['previous_count'] = lsoa_stats['previous_count'].fillna(0)
        lsoa_stats['growth'] = ((lsoa_stats['current_count'] - lsoa_stats['previous_count']) / lsoa_stats['previous_count']) * 100
        lsoa_stats['growth'] = lsoa_stats['growth'].replace([np.inf, -np.inf], np.nan).fillna(0)

        # Sort and format the tables
        ward_stats = ward_stats.sort_values('rate_per_1000', ascending=False)
        ward_stats['current_count'] = ward_stats['current_count'].astype(int)
        ward_stats['Total population'] = ward_stats['Total population'].astype(int)
        ward_stats['rate_per_1000'] = ward_stats['rate_per_1000'].round(2)
        ward_stats['growth'] = ward_stats['growth'].round(1)

        lsoa_stats = lsoa_stats.sort_values('current_count', ascending=False)
        lsoa_stats['current_count'] = lsoa_stats['current_count'].astype(int)
        lsoa_stats['previous_count'] = lsoa_stats['previous_count'].astype(int)
        lsoa_stats['growth'] = lsoa_stats['growth'].round(1)

        # Get top LSOA
        top_lsoa = lsoa_stats.iloc[0]

        # Rename columns for display
        ward_stats.columns = ['Ward Name', 'Borough', 'Current Count', 'Population', 'Previous Count', 'Rate per 1,000', 'Growth %']

        # Calculate total burglaries and growth
        total_current = len(current_burglaries)
        total_previous = len(previous_burglaries)
        total_growth = ((total_current - total_previous) / total_previous) * 100

        # Calculate borough-level statistics
        borough_stats = ward_stats.groupby('Borough').agg({
            'Current Count': 'sum',
            'Population': 'sum',
            'Previous Count': 'sum'
        }).reset_index()

        # Calculate borough-level rates and growth
        borough_stats['rate_per_1000'] = (borough_stats['Current Count'] / borough_stats['Population']) * 1000
        borough_stats['growth'] = ((borough_stats['Current Count'] - borough_stats['Previous Count']) / borough_stats['Previous Count']) * 100
        borough_stats['growth'] = borough_stats['growth'].replace([np.inf, -np.inf], np.nan).fillna(0)

        # Sort boroughs by rate
        borough_stats = borough_stats.sort_values('rate_per_1000', ascending=False)
        borough_stats['rate_per_1000'] = borough_stats['rate_per_1000'].round(2)
        borough_stats['growth'] = borough_stats['growth'].round(1)

        # Rename columns for display
        borough_stats.columns = ['Borough', 'Current Count', 'Population', 'Previous Count', 'Rate per 1,000', 'Growth %']

        # Get the borough with highest crime rate
        highest_rate_borough = borough_stats.iloc[0]

        # Sort based on selected options
        if borough_sort == 'rate':
            borough_stats = borough_stats.sort_values('Rate per 1,000', ascending=False)
        elif borough_sort == 'count':
            borough_stats = borough_stats.sort_values('Current Count', ascending=False)
        elif borough_sort == 'growth':
            borough_stats = borough_stats.sort_values('Growth %', ascending=False)

        if ward_sort == 'rate':
            ward_stats = ward_stats.sort_values('Rate per 1,000', ascending=False)
        elif ward_sort == 'count':
            ward_stats = ward_stats.sort_values('Current Count', ascending=False)
        elif ward_sort == 'growth':
            ward_stats = ward_stats.sort_values('Growth %', ascending=False)

        return [
            # Main Container with all statistics
            html.Div([
                # Header Section
                html.Div([
                    html.H4(f"Data Period: {selected_month}", className="text-center text-muted mb-3"),
                    html.Div([
                        html.Span(f"Total Burglaries: {total_current:,} ", className="me-4"),
                        html.Span(
                            f"Change from previous month: {total_growth:+.1f}%",
                            className=f"text-{'success' if total_growth < 0 else 'danger'}"
                        )
                    ], className="text-center mb-4")
                ], className="mb-4"),

                # Statistics Cards Row
                dbc.Row([
                    # Highest Borough Rate Card
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Highest Crime Rate Borough", className="text-center mb-3"),
                                html.H3(highest_rate_borough['Borough'], className="text-center text-danger mb-3"),
                                html.Div([
                                    html.Div([
                                        html.Span("Rate: ", className="text-muted"),
                                        html.Span(f"{highest_rate_borough['Rate per 1,000']} per 1,000", className="fw-bold")
                                    ], className="mb-2"),
                                    html.Div([
                                        html.Span("Total Incidents: ", className="text-muted"),
                                        html.Span(f"{highest_rate_borough['Current Count']:,}", className="fw-bold")
                                    ], className="mb-2"),
                                    html.Div([
                                        html.Span("Growth: ", className="text-muted"),
                                        html.Span(
                                            f"{highest_rate_borough['Growth %']:+.1f}%",
                                            className=f"fw-bold text-{'success' if highest_rate_borough['Growth %'] < 0 else 'danger'}"
                                        )
                                    ])
                                ], className="text-center")
                            ])
                        ], className="shadow-sm h-100")
                    ], md=4),

                    # Most Affected Ward Card
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Most Affected Ward", className="text-center mb-3"),
                                html.H3(ward_stats.iloc[0]['Ward Name'], className="text-center text-primary mb-2"),
                                html.P(f"Borough: {ward_stats.iloc[0]['Borough']}", className="text-center text-muted mb-3"),
                                html.Div([
                                    html.Div([
                                        html.Span("Rate: ", className="text-muted"),
                                        html.Span(f"{ward_stats.iloc[0]['Rate per 1,000']} per 1,000", className="fw-bold")
                                    ], className="mb-2"),
                                    html.Div([
                                        html.Span("Incidents: ", className="text-muted"),
                                        html.Span(f"{ward_stats.iloc[0]['Current Count']:,}", className="fw-bold")
                                    ], className="mb-2"),
                                    html.Div([
                                        html.Span("Growth: ", className="text-muted"),
                                        html.Span(
                                            f"{ward_stats.iloc[0]['Growth %']:+.1f}%",
                                            className=f"fw-bold text-{'success' if ward_stats.iloc[0]['Growth %'] < 0 else 'danger'}"
                                        )
                                    ])
                                ], className="text-center")
                            ])
                        ], className="shadow-sm h-100")
                    ], md=4),

                    # Most Affected LSOA Card
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Most Affected Area (LSOA)", className="text-center mb-3"),
                                html.H3(top_lsoa['LSOA name'], className="text-center text-primary mb-3"),
                                html.Div([
                                    html.Div([
                                        html.Span("Incidents: ", className="text-muted"),
                                        html.Span(f"{top_lsoa['current_count']:,}", className="fw-bold")
                                    ], className="mb-2"),
                                    html.Div([
                                        html.Span("Growth: ", className="text-muted"),
                                        html.Span(
                                            f"{top_lsoa['growth']:+.1f}%",
                                            className=f"fw-bold text-{'success' if top_lsoa['growth'] < 0 else 'danger'}"
                                        )
                                    ])
                                ], className="text-center")
                            ])
                        ], className="shadow-sm h-100")
                    ], md=4)
                ], className="mb-4"),

                # Tables Section
                dbc.Row([
                    # Borough Statistics Table
                    dbc.Col([
                        html.Div([
                            html.H4("Borough-Level Statistics", className="text-center mb-3"),
                            # Borough sorting options
                            html.Div([
                                dbc.RadioItems(
                                    id='borough-sort-options',
                                    options=[
                                        {'label': 'Sort by Rate', 'value': 'rate'},
                                        {'label': 'Sort by Count', 'value': 'count'},
                                        {'label': 'Sort by Growth', 'value': 'growth'}
                                    ],
                                    value=borough_sort,
                                    inline=True,
                                    className="mb-3"
                                )
                            ], className="text-center"),
                            dbc.Table.from_dataframe(
                                borough_stats,
                                striped=True,
                                bordered=True,
                                hover=True,
                                responsive=True,
                                className="table-dark"
                            )
                        ], className="mb-4", style={
                            'height': '800px',
                            'overflowY': 'auto'
                        })
                    ], md=6),

                    # Ward Statistics Table
                    dbc.Col([
                        html.Div([
                            html.H4("Ward-Level Statistics", className="text-center mb-3"),
                            # Ward sorting options
                            html.Div([
                                dbc.RadioItems(
                                    id='ward-sort-options',
                                    options=[
                                        {'label': 'Sort by Rate', 'value': 'rate'},
                                        {'label': 'Sort by Count', 'value': 'count'},
                                        {'label': 'Sort by Growth', 'value': 'growth'}
                                    ],
                                    value=ward_sort,
                                    inline=True,
                                    className="mb-3"
                                )
                            ], className="text-center"),
                            dbc.Table.from_dataframe(
                                ward_stats[['Ward Name', 'Borough', 'Current Count', 'Population', 'Rate per 1,000', 'Growth %']],
                                striped=True,
                                bordered=True,
                                hover=True,
                                responsive=True,
                                className="table-dark"
                            )
                        ], style={
                            'height': '800px',
                            'overflowY': 'auto'
                        })
                    ], md=6)
                ]),

                # Key Insights Section
                html.Div([
                    html.H3("Key Insights", className="text-center mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.Ul([
                                html.Li([
                                    html.Strong("Highest Borough Rate: "),
                                    f"{highest_rate_borough['Borough']} has the highest borough-level burglary rate at {highest_rate_borough['Rate per 1,000']} per 1,000 people."
                                ], className="mb-3"),
                                html.Li([
                                    html.Strong("Highest Ward Rate: "),
                                    f"{ward_stats.iloc[0]['Ward Name']} in {ward_stats.iloc[0]['Borough']} has the highest ward-level burglary rate at {ward_stats.iloc[0]['Rate per 1,000']} per 1,000 people."
                                ], className="mb-3")
                            ])
                        ], md=6),
                        dbc.Col([
                            html.Ul([
                                html.Li([
                                    html.Strong("Most Incidents: "),
                                    f"{ward_stats.loc[ward_stats['Current Count'].idxmax()]['Ward Name']} in {ward_stats.loc[ward_stats['Current Count'].idxmax()]['Borough']} had the highest number of incidents with {ward_stats['Current Count'].max()} burglaries."
                                ], className="mb-3"),
                                html.Li([
                                    html.Strong("Trend: "),
                                    f"Overall burglary incidents have {'decreased' if total_growth < 0 else 'increased'} by {abs(total_growth):.1f}% compared to the previous month."
                                ], className="mb-3")
                            ])
                        ], md=6)
                    ])
                ], className="mt-4 p-4 bg-light rounded")
            ], className="p-4")
        ]
    except Exception as e:
        print(f"Error updating summarized data: {str(e)}")
        return html.Div("Error loading data. Please try again later.", className="text-danger text-center")
    return None


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
                    html.H4("About Data Attributes", className="mt-4 mb-3 text-start"),
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


from dash import Input, Output, State

@app.callback(
    [
        Output("deprivation-data-table", "children"),
        Output("deprivation-content", "style"),
    ],
    [
        Input("btn-deprivation", "n_clicks"),
        Input("deprivation-toggle", "value"),
    ],
    prevent_initial_call=True
)
def display_deprivation_data(n_clicks, toggle_value):
    # toggle_value: [] means LSOA (off), ["ward"] means Ward (on)

    if not n_clicks or n_clicks % 2 == 0:
        # Hide content if button hasn't been clicked or on even clicks
        return None, {"display": "none"}

    deprivation_df = load_deprivation_data()  # Your data loading function

    if deprivation_df.empty:
        return (
            html.Div("No deprivation data available", className="text-danger"),
            {"display": "none"},
        )

    if "ward" in toggle_value:
        # Aggregate to ward level (simple mean as per your original code)
        ward_df = deprivation_df.groupby(['Ward code', 'Ward name']).mean(numeric_only=True).reset_index()
        display_df = ward_df
    else:
        # Show LSOA level data
        cols_to_move_up = ['LSOA code', 'Ward code', 'Ward name']
        deprivation_df = deprivation_df.set_index(cols_to_move_up).reset_index()
        display_df = deprivation_df

    display_df = display_df.round(2)

    # Prepare columns for DataTable
    columns = [{"name": col, "id": col} for col in display_df.columns]

    # Dash DataTable with native sorting enabled and pagination (page size = 6)
    table = dash_table.DataTable(
        data=display_df.to_dict('records'),
        columns=columns,
        page_size=6,
        sort_action='native',
        style_table={
            'overflowX': 'auto',
            'maxWidth': '100%',
            'margin': 'auto',
            'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        },

        style_header={
            'backgroundColor': '#205081',  # Medium Navy Blue header
            'color': '#f0f4f8',  # Very light grey text
            'fontWeight': '600',
            'fontSize': '15px',
            'border': '1px solid #183b6e',
            'textAlign': 'center',
            'whiteSpace': 'normal',
            'letterSpacing': '0.03em',
        },

        style_cell={
            'backgroundColor': '#e7edf7',  # Very light blue background for cells
            'color': '#102a54',  # Darker blue text for contrast
            'padding': '10px 14px',
            'fontSize': '14px',
            'border': '1px solid #c1c9de',
            'textAlign': 'left',
            'whiteSpace': 'normal',
            'lineHeight': '1.4',
            'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        },

        style_data_conditional=[
            {
                'if': {'row_index': 'even'},
                'backgroundColor': '#d7e0f4',  # Slightly darker light blue for even rows
            },
            {
                'if': {'state': 'active'},  # Hover / active row
                'backgroundColor': '#aac4f7',
                'border': '1px solid #517acc',
            },
            {
                'if': {'state': 'selected'},  # Selected rows
                'backgroundColor': '#8aa6e8',
                'border': '1px solid #3f5f9e',
                'color': '#f9fafc',  # lighter text on selected
                'fontWeight': '600',
            },
            {
                'if': {'filter_query': '{Income Domain} > 50'},  # conditional red text example
                'color': '#b3302f',
                'fontWeight': '700',
            },
        ],

        style_cell_conditional=[
            {'if': {'column_id': 'LSOA code'}, 'textAlign': 'center', 'fontWeight': '600'},
            {'if': {'column_id': 'Ward code'}, 'textAlign': 'center', 'fontWeight': '600'},
        ],

        page_action='native',
        filter_action='none',
    )

    return table, {"display": "block"}

@app.callback(
    [
        Output("census-data-table", "children"),
        Output("census-content", "style"),
    ],
    [
        Input("btn-census", "n_clicks"),
        Input("census-toggle", "value"),
    ],
    prevent_initial_call=True
)
def display_census_data(n_clicks, toggle_value):
    # toggle_value: [] means LSOA (off), ["ward"] means Ward (on)

    if not n_clicks or n_clicks % 2 == 0:
        # Hide content if button hasn't been clicked or on even clicks
        return None, {"display": "none"}

    census_df = load_census_data()  # Your data loading function

    if census_df.empty:
        return (
            html.Div("No deprivation data available", className="text-danger"),
            {"display": "none"},
        )

    if "ward" in toggle_value:
        # Aggregate to ward level (simple mean as per your original code)
        ward_df = census_df.groupby(['Ward code', 'Ward name']).mean(numeric_only=True).reset_index()
        display_df = ward_df
    else:
        # Show LSOA level data
        cols_to_move_up = ['LSOA code', 'LSOA name', 'Ward code', 'Ward name']
        census_df = census_df.set_index(cols_to_move_up).reset_index()
        display_df = census_df

    display_df = display_df.round(2)

    # Prepare columns for DataTable
    columns = [{"name": col, "id": col} for col in display_df.columns]

    # Dash DataTable with native sorting enabled and pagination (page size = 6)
    table = dash_table.DataTable(
        data=display_df.to_dict('records'),
        columns=columns,
        page_size=6,
        sort_action='native',
        style_table={
            'overflowX': 'auto',
            'maxWidth': '100%',
            'margin': 'auto',
            'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        },

        style_header={
            'backgroundColor': '#205081',  # Medium Navy Blue header
            'color': '#f0f4f8',  # Very light grey text
            'fontWeight': '600',
            'fontSize': '15px',
            'border': '1px solid #183b6e',
            'textAlign': 'center',
            'whiteSpace': 'normal',
            'letterSpacing': '0.03em',
        },

        style_cell={
            'backgroundColor': '#e7edf7',  # Very light blue background for cells
            'color': '#102a54',  # Darker blue text for contrast
            'padding': '10px 14px',
            'fontSize': '14px',
            'border': '1px solid #c1c9de',
            'textAlign': 'left',
            'whiteSpace': 'normal',
            'lineHeight': '1.4',
            'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        },

        style_data_conditional=[
            {
                'if': {'row_index': 'even'},
                'backgroundColor': '#d7e0f4',  # Slightly darker light blue for even rows
            },
            {
                'if': {'state': 'active'},  # Hover / active row
                'backgroundColor': '#aac4f7',
                'border': '1px solid #517acc',
            },
            {
                'if': {'state': 'selected'},  # Selected rows
                'backgroundColor': '#8aa6e8',
                'border': '1px solid #3f5f9e',
                'color': '#f9fafc',  # lighter text on selected
                'fontWeight': '600',
            },
            {
                'if': {'filter_query': '{Income Domain} > 50'},  # conditional red text example
                'color': '#b3302f',
                'fontWeight': '700',
            },
        ],

        style_cell_conditional=[
            {'if': {'column_id': 'LSOA code'}, 'textAlign': 'center', 'fontWeight': '600'},
            {'if': {'column_id': 'Ward code'}, 'textAlign': 'center', 'fontWeight': '600'},
        ],

        page_action='native',
        filter_action='none',
    )

    return table, {"display": "block"}

# Add callback to control submenu visibility
@app.callback(
    Output("data-explorer-submenu", "style"),
    Input("url", "pathname")
)
def toggle_data_explorer_submenu(pathname):
    if pathname in ["/data", "/data/crime", "/data/deprivation", "/data/census", "/data/summary"]:
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


# Add new callbacks for sorting
@app.callback(
    Output("borough-sort-options", "value"),
    Input("borough-sort-options", "value")
)
def update_borough_sort(sort_option):
    return sort_option

@app.callback(
    Output("ward-sort-options", "value"),
    Input("ward-sort-options", "value")
)
def update_ward_sort(sort_option):
    return sort_option


if __name__ == '__main__':
    app.run(debug=False)  # Change debug to False to hide debug messages
