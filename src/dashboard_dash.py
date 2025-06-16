import dash
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
from dash import dash_table
from dash import callback_context as ctx
import plotly.io as pio
from heatmap_generator import generate_imd_heatmap, generate_forecasted_crime_counts_heatmap, generate_transport_stops_scatter, generate_base_ward_map
from dash.exceptions import PreventUpdate
import base64
import uuid
import folium
from branca.element import Figure

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG,
        'assets/custom_dashboard_dash.css',  # Updated path to be relative to src directory
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" # Bootstrap Icons (arrows)
    ],
    suppress_callback_exceptions=True  # Add this line to suppress callback exceptions
)
app.title = "Police Forecasting Dashboard"


# Data loading functions
# unprocessed: includes ALL raw crime data, including those outside of London, those without locations, etc.
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

# load wards and wards options
gdf_ward_boundaries = gpd.read_file('data/boundaries/ward boundaries 2024/london_wards_merged.shp')
gdf_ward_boundaries.rename(columns={'WD24CD': 'Ward code', 'WD24NM': 'Ward name'}, inplace=True)
wards = gdf_ward_boundaries[['Ward code', 'Ward name']].drop_duplicates()
ward_options = [
        {'label': f"{row['Ward code']}, {row['Ward name']}", 'value': row['Ward code']}
        for _, row in wards.sort_values('Ward name').iterrows()
    ]


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
            dbc.NavLink("Forecasting & Planning", href="/forecast", active="exact", className="nav-link ps-3"),
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
            html.H1("Crime Data", className="card-title"),
            html.P(
                "Explore street-level burglary crime data from 2022–2025 reported by the Metropolitan Police Service and City of London Police.",
                className="card-text text-center mb-4"
            ),

            html.Div([
                # About Data Attributes
                html.Div([
                    html.H4("About Data Attributes", className="mt-4 mb-3 text-start"),
                    html.Ul([
                        html.Li([html.Strong("Crime ID: "), "Unique identifier for each crime incident."], className="text-start"),
                        html.Li([html.Strong("Month: "), "The month when the crime was reported"], className="text-start"),
                        html.Li([html.Strong("Reported by: "), "The police force that recorded the crime"], className="text-start"),
                        html.Li([html.Strong("Falls within: "), "The police force responsible for the area"], className="text-start"),
                        html.Li([html.Strong("Longitude & Latitude: "), "Geographic coordinates of the crime location"], className="text-start"),
                        html.Li([html.Strong("Location: "), "Street name or area where the crime occurred"], className="text-start"),
                        html.Li([html.Strong("LSOA code & name: "), "Lower Layer Super Output Area identifier and name"], className="text-start"),
                        html.Li([html.Strong("Crime type: "), "Category of the crime committed (all are burglary)"], className="text-start"),
                        html.Li([html.Strong("Last outcome category: "), "The most recent status or resolution of the case"], className="text-start"),
                        html.Li([html.Strong("Context: "), "Additional information about the crime incident"], className="text-start"),
                    ], className="card-text", style={"listStylePosition": "inside", "paddingLeft": "0"})
                ], className="mb-4"),

                html.Hr(),

                # Filters
                html.Div([
                    html.H5("Filter Crime Data", className="text-center mt-4 mb-3"),

                    # Month selector
                    html.Div([
                        html.Label("Choose Month", className="mb-1"),
                        dcc.Dropdown(
                            id='month-picker',
                            options=[
                                {'label': f"{year}-{month:02d}", 'value': f"{year}-{month:02d}"}
                                for year in range(2022, 2026)
                                for month in range(1, 13)
                                if not (year == 2022 and month < 4) and not (year == 2025 and month > 3)
                            ],
                            value=None,
                            clearable=True,
                            searchable=True,
                            style={'width': '100%'}
                        )
                    ], style={"width": "250px"}, className="me-3"),

                    # Ward name selector
                    html.Div([
                        html.Label("Search by Ward", className="mb-1"),
                        dcc.Dropdown(
                            id='ward-picker',
                            options=ward_options,
                            placeholder="Type to search ward...",
                            clearable=True,
                            searchable=True,
                            style={'width': '100%'}
                        )
                    ], style={"width": "300px"}),

                ], className="d-flex justify-content-center flex-wrap gap-3 mb-4"),


                # Data Table
                html.Div([
                    html.Div(id="crime-data-table"),
                    html.Div(id="crime-data-error", className="text-danger text-center mt-3")
                ]),

                # Visualizations Placeholder (shown only when filters applied)
                html.Div(id="crime-visualizations", className="mt-5")

            ], className="p-3")
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
                ], id="deprivation-content", style={"display": "none"}),  # Initially hidden

                    # Correlation Heatmap of Deprivation Scores
                    html.Div(id="deprivation-visualizations", className="mt-5")

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
                        html.Strong("Accommodation Types: "),
                        "Distribution of different accommodation types (detached, semi-detached, terraced, flats)"
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

                    # Census Table
                    html.Div(id="census-data-table"),
                ], id="census-content", style={"display": "none"}),  # Initially hidden

                    # Census Visualizations (Barcharts for Four Areas)
                    html.Div(id="census-visualizations", className="mt-5")

            ], className="p-3")
        ])
    ], style={"marginLeft": "250px", "width": "100%"})


### TODO: WORK ON FORECASTING LAYOUT AND FINISH IT TODAY !!!

# TODO: downloads and dataframes etc.
boroughs = {
     'E09000001': 'City of London',
     'E09000002': 'Barking and Dagenham',
     'E09000003': 'Barnet',
     'E09000004': 'Bexley',
     'E09000005': 'Brent',
     'E09000006': 'Bromley',
     'E09000007': 'Camden',
     'E09000008': 'Croydon',
     'E09000009': 'Ealing',
     'E09000010': 'Enfield',
     'E09000011': 'Greenwich',
     'E09000012': 'Hackney',
     'E09000013': 'Hammersmith and Fulham',
     'E09000014': 'Haringey',
     'E09000015': 'Harrow',
     'E09000016': 'Havering',
     'E09000017': 'Hillingdon',
     'E09000018': 'Hounslow',
     'E09000019': 'Islington',
     'E09000020': 'Kensington and Chelsea',
     'E09000021': 'Kingston upon Thames',
     'E09000022': 'Lambeth',
     'E09000023': 'Lewisham',
     'E09000024': 'Merton',
     'E09000025': 'Newham',
     'E09000026': 'Redbridge',
     'E09000027': 'Richmond upon Thames',
     'E09000028': 'Southwark',
     'E09000029': 'Sutton',
     'E09000030': 'Tower Hamlets',
     'E09000031': 'Waltham Forest',
     'E09000032': 'Wandsworth',
     'E09000033': 'Westminster'}

borough_options = [
        {'label': f"{key}, {value}", 'value': key}
        for key, value in boroughs.items()
    ]
def forecasting():
    return dbc.Card([
        dbc.CardBody([
            html.H1("Forecasting & Planning", className="card-title"),
            html.P(
                "Use this tool to view forecasted residential burglary and recommended police resource allocations across London boroughs.",
                className="card-text text-center mb-4"
            ),

            html.Div([
                # About Forecasting & Planning
                html.Div([
                    html.H4("About Forecasts and Resource Allocation", className="mt-4 mb-3 text-start"),
                    html.Ul([
                        html.Li([
                            html.Strong("3-Month Forecasts: "),
                            "View predicted residential burglary counts for each ward over the next three months."
                            "Use this to identify medium-term trends and assess where crime is expected to rise or fall."
                        ], className="text-start"),
                        html.Li([
                            html.Strong("Next-Month Resource Allocation: "),
                            "See recommended allocations of police working hours for the next month across wards to match anticipated needs."
                            "These allocations are designed to help align deployment with projected demand."
                        ], className="text-start"),
                    ], className="card-text", style={"listStylePosition": "inside", "paddingLeft": "0"})
                ], className="mb-4"),

                html.Hr(),

                html.Div([
                    html.H5("Select Borough(s): ", className="mt-4 mb-2"),

                    # Dropdown
                    dcc.Dropdown(
                        id="borough-dropdown",
                        options=borough_options,
                        multi=True,
                        placeholder="Select one or more boroughs...",
                        style={
                            "width": "100%",
                            "color": "#0a2147",
                            "fontSize": "15px",
                        }
                    ),

                    html.Br(),

                    html.Small(
                        "Switch between forecasts and allocation.",
                        className="text-muted"
                    ),
                    # Tabs with custom styling
                    dcc.Tabs(
                        id="forecast-tabs",
                        value="forecasts",
                        children=[
                            dcc.Tab(
                                label="3-Month Forecasts",
                                value="forecasts",
                                style={
                                    "backgroundColor": "#dce6f7",
                                    "border": "1px solid #a8b6d4",
                                    "color": "#1a2e55",
                                    "fontWeight": "500",
                                },
                                selected_style={
                                    "backgroundColor": "#1f3c88",
                                    "color": "white",
                                    "border": "2px solid #1f3c88",
                                    "fontWeight": "700"
                                }
                            ),
                            dcc.Tab(
                                label="Next-Month Resource Allocation",
                                value="allocation",
                                style={
                                    "backgroundColor": "#dce6f7",
                                    "border": "1px solid #a8b6d4",
                                    "color": "#1a2e55",
                                    "fontWeight": "500",
                                },
                                selected_style={
                                    "backgroundColor": "#1f3c88",
                                    "color": "white",
                                    "border": "2px solid #1f3c88",
                                    "fontWeight": "700"
                                }
                            ),
                        ],
                        style={"marginBottom": "16px"}
                    ),

                    # Output with consistent height
                    html.Div(
                        id="forecasting-content",
                        className="mt-3",
                        style={
                            "minHeight": "400px",
                            "transition": "all 0.3s ease-in-out"
                        }
                    )
                ], className="text-center")
            ], className="p-4")
        ])
    ], style={"marginLeft": "250px", "width": "100%"})



# DATASETS
deprivation_df = load_deprivation_data()
burglaries_df = pd.read_parquet("data/processed/burglaries.parquet")
transport_stops_df = pd.read_parquet("data/processed/stops_lsoa.parquet")
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
            ], className="mb-4"),

            html.Hr(),
            html.H4("Density Heatmaps", className="mb-3"),

            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        id="heatmap-selector",
                        options=[
                            {"label": "Ward Boundaries", "value": "base"},
                            {"label": "IMD Score", "value": "imd"},
                            {"label": "Forecasted Crime Count Density", "value": "crime_density"},
                        ],
                        value="base",
                        multi=False, 
                        clearable=False,
                        style={"width": "300px"}
                    )
                )
            ], className="mb-3"),

            dbc.Row([
                dbc.Col(
                    dcc.Loading(
                        id="loading-map3",
                        type="circle",
                        children=html.Iframe(
                        id="heatmap-container",
                        style={"width": "100%", "height": "600px", "border": "none"}
                        )
                    ),
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
    merged["Highlight"] = merged["WD24CD"].apply(lambda x: "Selected Ward" if x == selected_ward else "Other Wards")

    fig = px.choropleth_mapbox(
        merged,
        geojson=json.loads(gdf_wards.to_crs("EPSG:4326").to_json()),
        locations="WD24CD",
        featureidkey="properties.WD24CD",
        color="Highlight",
        color_discrete_map={"Other Wards": "#672DAA", "Selected Ward": "#C7C73B"},
        mapbox_style="carto-positron",
        center={"lat": 51.5, "lon": -0.1},
        zoom=8.8,
        opacity=0.6,
        hover_name="WD24NM",
        hover_data={
            "Ward code": True,
            "Highlight": False,
            "WD24CD": False,
        }
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

        previous_month_crimes = crime_counts_df.loc[
            (crime_counts_df["Ward code"] == ward_code) &
            (crime_counts_df["Month"] == "2025-03-01"),
            "burglary_count"
        ].values
        previous_month_crimes = previous_month_crimes[0] if len(previous_month_crimes) > 0 else 0

        predicted_crimes = forecasts_df.loc[
            forecasts_df["Ward code"] == ward_code,
            "Predicted_Crime_Count"
        ].values
        predicted_crimes = round(predicted_crimes[0], 2) if len(predicted_crimes) > 0 else "N/A"

        diff = round(predicted_crimes - previous_month_crimes, 2) if isinstance(predicted_crimes, (float, int)) else "N/A"
        trend_arrow = "bi-arrow-up" if diff > 0 else "bi-arrow-down"
        trend_color = "text-danger" if diff > 0 else "text-success"
        diff_pct = round(abs(diff) / previous_month_crimes * 100, 2) if previous_month_crimes else 0

        resource_allocation = forecasts_df.loc[
            forecasts_df["Ward code"] == ward_code,
            "Allocated_Officers_Rounded"
        ].values
        resource_allocation = int(resource_allocation[0]) if len(resource_allocation) > 0 else "N/A"

        imd_score = deprivation_df.loc[
            deprivation_df["Ward code"] == ward_code,
            "Index of Multiple Deprivation (IMD) Score"
        ].values
        imd_score = round(imd_score[0], 2) if len(imd_score) > 0 else "N/A"

        transport_stops = get_stop_count(ward_code, stop_counts_df)

        return dbc.Card([
            dbc.CardBody([
                html.H4(ward_name, className="card-title mb-4"),

                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Span(f"{predicted_crimes}", className="fs-3 fw-bold me-2"),
                            html.Span([
                                html.I(className=f"bi {trend_arrow} me-1 {trend_color}", id="trend-icon"),
                                f"{diff_pct}%"
                            ], className=f"fs-6 {trend_color}"),
                            dbc.Tooltip("Change in residential burglary count vs previous month", target="trend-icon")
                        ])
                    ], width=6),
                    dbc.Col([
                        html.Div("Resource Recommendation", className="text-muted"),
                        html.Div(f"{resource_allocation} policing hours", className="fs-3 fw-bold")
                    ], width=6)
                ], className="mb-3"),

                html.Hr(className="my-2"),

                dbc.Row([
                    dbc.Col([
                        html.Div([
                            "IMD Score ",
                            html.I(className="bi bi-info-circle", id={"type": "imd-tooltip-icon", "index": ward_code}),
                            dbc.Tooltip("Index of Multiple Deprivation (higher = more deprived)", target={"type": "imd-tooltip-icon", "index": ward_code}),
                        ], className="text-muted"),
                        html.Div(imd_score, className="fs-3 fw-bold")
                    ], width=6),
                    dbc.Col([
                        html.Div([
                            "Transport Stops",
                            html.I(className="bi bi-info-circle", id={"type": "transport_stops-tooltip-icon", "index": ward_code}),
                            dbc.Tooltip("Number of Transportatation Stops (bus, train, etc.)", target={"type": "transport_stops-tooltip-icon", "index": ward_code}),
                        ], className="text-muted"),
                        html.Div(transport_stops, className="fs-3 fw-bold")
                    ], width=6)
                ]),
            ])
        ], className="shadow-sm")
    else:
        return dbc.Card([
            dbc.CardBody([
                html.P("Select ward on the map to inspect details.", className="text-muted mb-0")
            ])
        ])

@app.callback(
    Output("heatmap-container", "srcDoc"),
    Input("heatmap-selector", "value")
)
def update_heatmap(selected_layers):
    if not selected_layers:
        raise PreventUpdate

    # Determine which maps to include
    base = "base" in selected_layers
    imd = "imd" in selected_layers
    crime = "crime_density" in selected_layers

    # Generate the base map with wards
    if base:
        return generate_base_ward_map(gdf_wards, transport_stops_df)
    elif imd:
        return generate_imd_heatmap(gdf_wards, deprivation_df, transport_stops_df)
    elif crime:
        return generate_forecasted_crime_counts_heatmap(gdf_wards, forecasts_df, transport_stops_df)

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


from dash import dash_table

from dash import Output, Input, dcc
import dash_table
import plotly.express as px

@app.callback(
    [Output("crime-data-table", "children"),
     Output("crime-data-error", "children"),
     Output("crime-visualizations", "children")],
    [Input("month-picker", "value"),
     Input("ward-picker", "value")],
    prevent_initial_call=True
)
def display_crime_data(month, ward):
    if month:
        try:
            year, month_num = map(int, month.split('-'))
            if (year == 2022 and month_num < 4) or year < 2022 or (year == 2025 and month_num > 3) or year > 2025:
                return None, "Selected month is out of range. Please select a month between April 2022 and March 2025.", None

            selected_month = pd.Timestamp(year=year, month=month_num, day=1)

            # Filter for display table
            crime_df = burglaries_df[burglaries_df['Month'] == selected_month].copy()
            crime_df['Month'] = month
            if ward:
                crime_df = crime_df[crime_df["Ward code"] == ward]

            # Full time range for line/bar chart
            all_months = pd.date_range(start="2022-04-01", end="2025-03-01", freq='MS')

            # Prepare trend df
            trend_df = burglaries_df.copy()
            if ward:
                trend_df = trend_df[trend_df["Ward code"] == ward]

            trend_counts = (
                trend_df.groupby("Month")
                .size()
                .reindex(all_months, fill_value=0)
                .reset_index(name="Crime count")
                .rename(columns={"index": "Month"})
            )

            # Line chart with red marker for selected month
            line_fig = px.line(trend_counts, x="Month", y="Crime count",
                               title=f"Monthly Burglary Trend{' for Ward code ' + ward if ward else ''}",
                               markers=True)

            # Add red dot for selected month
            if selected_month in trend_counts["Month"].values:
                selected_point = trend_counts[trend_counts["Month"] == selected_month]

            # Improve layout
            # DARK MODE
            line_fig.update_layout(
                plot_bgcolor="#1e1e2f",  # dark plot area
                paper_bgcolor="#1e1e2f",  # darker outer area
                font=dict(color="#f0f0f0"),  # light text
                title_font_size=18,
                margin=dict(t=40, b=40, l=40, r=40),
                xaxis=dict(gridcolor='#333333'),
                yaxis=dict(gridcolor="#333333"),
                legend=dict(
                    x=0.99, y=0.99,
                    xanchor="right", yanchor="top",
                    bgcolor="rgba(30,30,30,0.6)",  # semi-dark background
                    bordercolor="#444444",
                    borderwidth=1,
                    font=dict(size=12, color="#ffffff")
                )
            )
            line_fig.update_traces(line=dict(color="#00cfff"), marker=dict(color="#00cfff"))

            line_fig.add_scatter(
                x=selected_point["Month"],
                y=selected_point["Crime count"],
                mode="markers",
                marker=dict(color="#ff0000", size=12),
                name="Selected Month"
            )
            # Monthly seasonal pattern
            seasonal_df = trend_df.copy()
            seasonal_df['Month name'] = seasonal_df['Month'].dt.month_name()

            month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December']

            monthly_counts = (seasonal_df.groupby("Month name")
                              .size()
                              .reindex(month_order, fill_value=0)
                              .reset_index(name="Crime count"))

            bar_fig = px.bar(monthly_counts, x="Month name", y="Crime count",
                             title=f"Total Crimes by Month{' for Ward code ' + ward if ward else ''}")

            # DARK MODe
            bar_fig.update_layout(
                plot_bgcolor="#1e1e2f",
                paper_bgcolor="#1e1e2f",
                font=dict(color="#f0f0f0"),
                title_font_size=18,
                margin=dict(t=40, b=40, l=40, r=40),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="#333333"),
                legend=dict(visible=False)
            )
            bar_fig.update_traces(marker_color="#00cfff")

            visualizations = html.Div([
                html.Hr(),
                html.H4("Crime Trends", className="text-start mb-3"),
                dcc.Graph(figure=line_fig),
                html.Hr(),
                dcc.Graph(figure=bar_fig)
            ])

            # If filtered table has content
            if not crime_df.empty:
                table = dash_table.DataTable(
                    data=crime_df.to_dict('records'),
                    columns=[{"name": col, "id": col} for col in crime_df.columns],
                    page_size=5,
                    style_table={
                        'overflowX': 'auto', 'maxWidth': '100%', 'margin': 'auto',
                        'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                    },
                    style_header={
                        'backgroundColor': '#205081', 'color': '#f0f4f8', 'fontWeight': '600',
                        'fontSize': '15px', 'border': '1px solid #183b6e',
                        'textAlign': 'center', 'whiteSpace': 'normal', 'letterSpacing': '0.03em',
                    },
                    style_data_conditional=[
                        {'if': {'row_index': 'even'}, 'backgroundColor': '#d7e0f4'},
                        {'if': {'state': 'active'}, 'backgroundColor': '#aac4f7', 'border': '1px solid #517acc'},
                        {'if': {'state': 'selected'}, 'backgroundColor': '#8aa6e8',
                         'border': '1px solid #3f5f9e', 'color': '#f9fafc', 'fontWeight': '600'},
                    ],
                    style_cell={
                        'backgroundColor': '#e7edf7', 'color': '#102a54',
                        'padding': '10px 14px', 'fontSize': '14px',
                        'border': '1px solid #c1c9de', 'textAlign': 'left',
                        'whiteSpace': 'normal', 'lineHeight': '1.4',
                        'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                    },
                    page_action='native',
                    filter_action='native',
                    style_cell_conditional=[
                        {'if': {'column_id': 'LSOA code'}, 'textAlign': 'center', 'fontWeight': '600'},
                        {'if': {'column_id': 'Ward code'}, 'textAlign': 'center', 'fontWeight': '600'},
                        {'if': {'column_id': 'Borough code'}, 'textAlign': 'center', 'fontWeight': '600'}
                    ],
                )
                return table, "", visualizations
            else:
                return None, f"No data available for {month}" if not ward else f"No data for {ward} in {month}", visualizations

        except Exception as e:
            return None, f"Error loading data: {str(e)}", None

    return None, "", None


from dash import Input, Output, State

import plotly.express as px
from dash import dcc

@app.callback(
    [
        Output("deprivation-data-table", "children"),
        Output("deprivation-visualizations", "children"),
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
        return None, None, {"display": "none"}

    deprivation_df = load_deprivation_data()  # Your data loading function

    if deprivation_df.empty:
        return (
            html.Div("No deprivation data available", className="text-danger"),
            None,
            {"display": "none"},
        )

    if "ward" in toggle_value:
        # Aggregate to ward level (simple mean)
        display_df = deprivation_df.groupby(['Ward code', 'Ward name']).mean(numeric_only=True).reset_index()
    else:
        # Show LSOA level data
        cols_to_move_up = ['LSOA code', 'LSOA name']
        deprivation_df = deprivation_df.set_index(cols_to_move_up).reset_index()
        display_df = deprivation_df

    display_df = display_df.round(2)

    # Prepare columns for DataTable
    columns = [{"name": col, "id": col} for col in display_df.columns]

    # Create DataTable
    table = dash_table.DataTable(
        data=display_df.to_dict('records'),
        columns=columns,
        page_size=5,
        sort_action='native',
        style_table={
            'overflowX': 'auto',
            'maxWidth': '100%',
            'margin': 'auto',
            'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        },
        style_header={
            'backgroundColor': '#205081',
            'color': '#f0f4f8',
            'fontWeight': '600',
            'fontSize': '15px',
            'border': '1px solid #183b6e',
            'textAlign': 'center',
            'whiteSpace': 'normal',
            'letterSpacing': '0.03em',
        },
        style_cell={
            'backgroundColor': '#e7edf7',
            'color': '#102a54',
            'padding': '10px 14px',
            'fontSize': '14px',
            'border': '1px solid #c1c9de',
            'textAlign': 'left',
            'whiteSpace': 'normal',
            'lineHeight': '1.4',
            'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        },
        style_data_conditional=[
            {'if': {'row_index': 'even'}, 'backgroundColor': '#d7e0f4'},
            {'if': {'state': 'active'}, 'backgroundColor': '#aac4f7', 'border': '1px solid #517acc'},
            {'if': {'state': 'selected'}, 'backgroundColor': '#8aa6e8',
             'border': '1px solid #3f5f9e', 'color': '#f9fafc', 'fontWeight': '600'},
        ],
        style_cell_conditional=[
            {'if': {'column_id': 'LSOA code'}, 'textAlign': 'center', 'fontWeight': '600'},
            {'if': {'column_id': 'Ward code'}, 'textAlign': 'center', 'fontWeight': '600'},
            {'if': {'column_id': 'Borough code'}, 'textAlign': 'center', 'fontWeight': '600'}
        ],
        page_action='native',
        filter_action='native',
    )

    # Filter columns with "Score" in the name for correlation
    score_cols = [col for col in display_df.columns if 'Score' in col]
    rename_cols = {'Index of Multiple Deprivation (IMD) Score': 'IMD',
                   'Income Score': 'Income',
                   'Employment Score': 'Employment',
                   'Education, Skills and Training Score': 'Education',
                   'Health Deprivation and Disability Score': 'Health',
                   'Crime Score': 'Crime',
                   'Barriers to Housing and Services Score': 'Housing',
                   'Living Environment Score': 'Living'}

    corr_df = display_df[score_cols].rename(columns=rename_cols).corr()

    fig = px.imshow(
        corr_df,
        text_auto='.2f',
        aspect='auto',
        color_continuous_scale='RdBu_r',
        origin='upper',
        title=f'Correlation Matrix of Deprivation Scores at {"LSOA-level" if not "ward" in toggle_value else "Ward-level"}',
        labels=dict(x="Features", y="Features", color="Correlation"),
    )
    fig.update_layout(
        margin=dict(l=40, r=40, t=60, b=40),
        height=700,
        plot_bgcolor='#1e1e2f',  # Dark plot background
        paper_bgcolor='#1e1e2f',  # Dark paper (overall) background
        font=dict(color='white'),  # White font color for text
        xaxis=dict(
            tickangle=45,  # Rotate x-axis labels
            tickfont=dict(color='white'),
            showgrid=False,
            zeroline=False,
            linecolor='white',
            mirror=True,
        ),
        yaxis=dict(
            tickfont=dict(color='white'),
            showgrid=False,
            zeroline=False,
            linecolor='white',
            mirror=True,
        ),
        coloraxis_colorbar=dict(
            title_font=dict(color='white'),
            tickfont=dict(color='white'),
            bgcolor='#1e1e2f',
        )
    )

    corr_graph = html.Div([
        html.Hr(),
        html.H4("Correlation Between Features", className="text-start mb-3"),
        dcc.Graph(figure=fig)])

    return table, corr_graph, {"display": "block"}

@app.callback(
    [
        Output("census-data-table", "children"),
        Output("census-content", "style")
    ],
    [
        Input("btn-census", "n_clicks"),
        Input("census-toggle", "value")
    ],
    prevent_initial_call=True
)
def display_census_data(n_clicks, toggle_value):
    census_df = load_census_data()
    if census_df.empty:
        return html.Div("No data available", className="text-danger"), {"display": "none"}

    is_ward = "ward" in toggle_value
    if is_ward:
        display_df = census_df.groupby(['Ward code', 'Ward name']).sum(numeric_only=True).reset_index()
        display_df["id"] = display_df["Ward code"]  # Set row ID internally
    else:
        display_df = census_df.set_index(['LSOA code', 'LSOA name']).reset_index()

    display_df = display_df.round(2)

    columns = [
        {"name": col, "id": col}
        for col in display_df.columns if col != "id"  # Hide 'id' from display
    ]

    table = dash_table.DataTable(
        id='census-table',
        data=display_df.to_dict('records'),
        columns=columns,
        page_size=5,
        sort_action='native',
        filter_action='native',
        cell_selectable=True,
        row_selectable="single" if is_ward else False,
        selected_row_ids=[] if is_ward else None,  # Optional: provide default
        style_table={
            'overflowX': 'auto',
            'maxWidth': '100%',
            'margin': 'auto',
            'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        },
        style_header={
            'backgroundColor': '#205081',
            'color': '#f0f4f8',
            'fontWeight': '600',
            'fontSize': '15px',
            'border': '1px solid #183b6e',
            'textAlign': 'center',
            'whiteSpace': 'normal',
            'letterSpacing': '0.03em',
        },
        style_cell={
            'backgroundColor': '#e7edf7',
            'color': '#102a54',
            'padding': '10px 14px',
            'fontSize': '14px',
            'border': '1px solid #c1c9de',
            'textAlign': 'left',
            'whiteSpace': 'normal',
            'lineHeight': '1.4',
            'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        },
        style_data_conditional=[
            {'if': {'row_index': 'even'}, 'backgroundColor': '#d7e0f4'},
            {'if': {'state': 'active'}, 'backgroundColor': '#aac4f7', 'border': '1px solid #517acc'},
            {'if': {'state': 'selected'}, 'backgroundColor': '#8aa6e8',
             'border': '1px solid #3f5f9e', 'color': '#f9fafc', 'fontWeight': '600'},
        ],
        style_cell_conditional=[
            {'if': {'column_id': 'LSOA code'}, 'textAlign': 'center', 'fontWeight': '600'},
            {'if': {'column_id': 'Ward code'}, 'textAlign': 'center', 'fontWeight': '600'},
            {'if': {'column_id': 'Borough code'}, 'textAlign': 'center', 'fontWeight': '600'}
        ]
    )

    return table, {"display": "block"}


@app.callback(
    Output("census-visualizations", "children"),
    [
        Input("btn-census", "n_clicks"),
        Input("census-table", "selected_rows")
    ],
    State("census-toggle", "value"),
    prevent_initial_call=True
)
def update_census_visuals(n_clicks, selected_rows, toggle_value):
    census_df = load_census_data()
    if census_df.empty:
        return None

    is_ward = "ward" in toggle_value

    if is_ward:
        grouped_df = census_df.groupby(['Ward code', 'Ward name']).sum(numeric_only=True).reset_index()
    else:
        grouped_df = census_df.set_index(['LSOA code', 'LSOA name']).reset_index()

    total = grouped_df.sum(numeric_only=True)

    def make_grouped_bar(data_selected, data_total, title):
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=data_selected['label'],
            x=data_selected['value'],
            name='Selected Area (%)',
            orientation='h',
            hovertext=data_selected['hover'],
            marker_color='rgba(255,127,80,0.75)'
        ))
        fig.add_trace(go.Bar(
            y=data_total['label'],
            x=data_total['value'],
            name='All Areas (%)',
            orientation='h',
            hovertext=data_total['hover'],
            marker_color='rgba(100,150,250,0.85)'
        ))
        fig.update_layout(
            title=dict(text=title),
            barmode='group',
            xaxis=dict(range=[0, 100]),
            xaxis_title='Percentage (%)',
            yaxis_title='Category',
            plot_bgcolor='#1e1e2f',
            paper_bgcolor='#1e1e2f',
            font=dict(color='#f4f4f4'),
            legend=dict(orientation='h', x=0.6, y=1.1),
            height=350,
            margin=dict(l=120, r=40, t=40, b=40)
        )
        return fig

    def build_comparison(section_cols, title, sel_vals=None):
        total_vals = total[section_cols]
        total_sum = total_vals.sum()
        total_data = pd.DataFrame({
            "label": section_cols,
            "value": (total_vals / total_sum * 100).round(2),
            "hover": total_vals.astype(int).astype(str) + " people"
        })

        if sel_vals is not None:
            sel_sum = sel_vals.sum()
            sel_data = pd.DataFrame({
                "label": section_cols,
                "value": (sel_vals / sel_sum * 100).round(2),
                "hover": sel_vals.astype(int).astype(str) + " people"
            })
        else:
            sel_data = total_data.copy()
            sel_data['value'] = 0
            sel_data['hover'] = ["N/A"] * len(sel_data)

        return dcc.Graph(figure=make_grouped_bar(sel_data, total_data, title))

    # --- Define sections ---
    demography_cols = ['65 years and older', '15 to 64 years', 'Under 15 years']
    household_cols = ['Other household types', 'Single family household',
                      'One-person household: Other', 'One-person household: Aged 66 years and over']
    accommodation_cols = [
        'A caravan or other mobile or temporary structure', 'Flat, maisonette or apartment',
        'Terraced whole house or bungalow', 'Semi-detached whole house or bungalow',
        'Detached whole house or bungalow']
    dwelling_cols = ['Unoccupied dwellings', 'Total: Occupied dwellings']

    sel_vals = None
    if is_ward and selected_rows and len(selected_rows) > 0:
        sel_index = selected_rows[0]
        if sel_index < len(grouped_df):
            sel_row = grouped_df.iloc[sel_index]
            sel_vals = sel_row[total.index]

    selection_note = html.P(
        "Tip: Select a row in the table above to compare that ward against overall figures.",
        className="text-info fst-italic mb-3"
    ) if is_ward else html.P(
        "LSOA-level selection is currently not supported for detailed comparison.",
        className="text-warning fst-italic mb-3"
    )

    return html.Div([
        html.Hr(),
        html.H4("Census Overview by Category (All Areas vs Selected)", className="text-start mb-3"),
        selection_note,
        build_comparison(demography_cols, "Population Demography (%)", sel_vals[demography_cols] if sel_vals is not None else None),
        build_comparison(household_cols, "Household Composition (%)", sel_vals[household_cols] if sel_vals is not None else None),
        build_comparison(accommodation_cols, "Accommodation Types (%)", sel_vals[accommodation_cols] if sel_vals is not None else None),
        build_comparison(dwelling_cols, "Dwelling Occupancy (%)", sel_vals[dwelling_cols] if sel_vals is not None else None),
    ])

# Add callback to control submenu visibility
@app.callback(
    Output("data-explorer-submenu", "style"),
Input("forecast-tabs", "value"),
    Input("url", "pathname")
)
def toggle_data_explorer_submenu(pathname):
    if pathname in ["/data", "/data/crime", "/data/deprivation", "/data/census", "/data/summary"]:
        return {"display": "block"}
    return {"display": "none"}

# FORECASTING & PLANNING CALLBACKS
# TODO: GLOBAL STORAGES
raw_forecasts_df = pd.read_csv('data/processed/sarima_final_forecast_per_ward.csv')
lookup = pd.read_csv('data/lookups/look up LSOA 2021 to ward 2024 merged.csv')
lookup_ward_borough = lookup[['Ward code', 'Ward name']].drop_duplicates()
def prepare_forecast_table(selected_boroughs=None):
    """
    Transforms raw forecast data into a pivoted table format with integer values and ward/borough names.
    Optionally filters by selected boroughs.
    """
    # Pivot the table: rows = ward code, columns = Month, values = mean forecast
    pivot_df = raw_forecasts_df.pivot(index='Ward code', columns='Month', values='mean')

    pivot_df.columns = [f"Predicted Crime Count: {col[:7]}" for col in pivot_df.columns]

    # Replace NaNs (if any) with 0
    pivot_df = pivot_df.fillna(0)

    # Round to nearest integer and ensure non-negative values
    pivot_df = pivot_df.round().astype(int).clip(lower=0)

    # Reset index to bring 'Ward code' back as a column
    pivot_df = pivot_df.reset_index()

    # Merge with ward and borough names
    merged_df = pivot_df.merge(lookup_ward_borough, on='Ward code', how='left')

    # Optional: Reorder columns
    final_df = merged_df.set_index(['Ward code', 'Ward name', 'Borough code', 'Borough name']).reset_index()

    # Filter if boroughs are selected
    if selected_boroughs:
        final_df = final_df[final_df['Borough code'].isin(selected_boroughs)]
        final_df = final_df.sort_values(by=['Borough name', 'Ward name'])
        return final_df

    return None

def prepare_allocation(selected_boroughs=None):
    """
    Loads and optionally filters the ward-hour allocation data by selected boroughs.
    """
    allocation_df = pd.read_csv('data/processed/ward_hour_allocation_LP_method.csv')

    # Rename columns to be more descriptive
    allocation_df.rename(columns={
        'Predicted_Crime_Count': 'Predicted Crime Count: 2025-04',
        'Allocated_Officers_Rounded': 'Allocated Hours (Daily)'
    }, inplace=True)

    # Merge with ward/borough lookup to get readable names
    merged_df = allocation_df.merge(lookup_ward_borough, on=['Ward code', 'Ward name'], how='left')

    # ALlocated officers = allocated hours / 2 (rounded up)
    merged_df['Allocated Police Officers (Daily)'] = np.ceil(merged_df['Allocated Hours (Daily)'] / 2).astype(int)
    # Allow only integer values
    merged_df['Predicted Crime Count: 2025-04'] = merged_df['Predicted Crime Count: 2025-04'].round().astype(int).clip(lower=0)

    # Reorder columns: Borough name, Ward name, then allocation info
    final_df = merged_df[[
        'Ward code', 'Ward name', 'Borough code', 'Borough name',
        'Predicted Crime Count: 2025-04', 'Allocated Hours (Daily)', 'Allocated Police Officers (Daily)'
    ]]

    # Filter by selected boroughs if provided
    if selected_boroughs:
        final_df = final_df[final_df['Borough code'].isin(selected_boroughs)]
        # Sort by Borough name then Ward name
        final_df = final_df.sort_values(by=['Borough name', 'Ward name'])
        return final_df

    return None

@callback(
    Output("forecasting-content", "children"),
    Input("forecast-tabs", "value"),
    Input("borough-dropdown", "value"),
    prevent_initial_call=True
)
def update_forecasting_tables_content(tab_value, selected_boroughs):
    if tab_value == "forecasts":
        filtered_df = prepare_forecast_table(selected_boroughs)

        return html.Div([
            # Download button + download component
            html.Div([
                html.Br(),
                html.Div(
                    html.Button(
                        "Download Table CSV",
                        id="btn-download-csv",
                        n_clicks=0,
                        className="btn btn-primary mb-3"
                    ),
                    style={"textAlign": "left"}  # aligns button to the left
                ),
                dcc.Download(id="download-dataframe-csv")
            ]),


            dash_table.DataTable(
                id='forecast-table',
                data=filtered_df.to_dict('records'),
                columns=[{"name": col, "id": col} for col in filtered_df.columns],
                page_size=10,
                sort_action='native',
                selected_rows=[],
                style_table={'overflowX': 'auto', 'maxWidth': '100%', 'margin': 'auto',
                             'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"},
                style_header={
                    'backgroundColor': '#205081', 'color': '#f0f4f8', 'fontWeight': '600', 'fontSize': '15px',
                    'border': '1px solid #183b6e', 'textAlign': 'center', 'whiteSpace': 'normal', 'letterSpacing': '0.03em'
                },
                style_cell={
                    'backgroundColor': '#e7edf7', 'color': '#102a54', 'padding': '10px 14px', 'fontSize': '14px',
                    'border': '1px solid #c1c9de', 'textAlign': 'left', 'whiteSpace': 'normal',
                    'lineHeight': '1.4', 'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
                },
                style_data_conditional=[
                    {'if': {'row_index': 'even'}, 'backgroundColor': '#d7e0f4'},
                    {'if': {'state': 'active'}, 'backgroundColor': '#aac4f7', 'border': '1px solid #517acc'},
                    {'if': {'state': 'selected'}, 'backgroundColor': '#8aa6e8',
                     'border': '1px solid #3f5f9e', 'color': '#f9fafc', 'fontWeight': '600'},
                ],
                style_cell_conditional=[
                    {'if': {'column_id': 'Ward code'}, 'textAlign': 'center', 'fontWeight': '600'},
                    {'if': {'column_id': 'Borough code'}, 'textAlign': 'center', 'fontWeight': '600'}
                ],
                page_action='native',
                filter_action='native',
                row_selectable='single'
            ),
            html.Hr(),
            html.H4("Forecast Chart", className="text-start mb-3"),
            html.P("Tip: Select a row in the table above to view its 3-month residential burglary forecast based on SARIMA modeling. "
            "The forecast includes a 95% confidence interval to highlight prediction uncertainty.", className="text-info fst-italic text-start mb-3"),
            html.Div(id="forecast-chart-display", className="mt-4")
        ])

    elif tab_value == "allocation":
        allocation_df = prepare_allocation(selected_boroughs)

        return html.Div([
            # Resource limitation context
            html.Div([
                html.H6("Resource Limitations", className="mb-2 text-start"),
                html.Ul([
                    html.Li("Each ward has approximately 100 officers available daily between 06:00 and 22:00.",
                            className="text-start"),
                    html.Li(
                        "Only 2 hours per officer (200 hours/day total) can be dedicated to burglary response, 4 days per week.",
                        className="text-start"),
                    html.Li("Officers cannot operate outside their assigned ward.", className="text-start"),
                    html.Li(
                        "Special operations using additional officers can be scheduled, but no more than once every 4 months.",
                        className="text-start")
                ], style={"listStylePosition": "inside", "paddingLeft": "0"}, className="mb-3 text-muted")
            ], className="text-start"),

            # Download button + download component
            html.Br(),
            html.Div([
                html.Div(
                    html.Button(
                        "Download Table CSV",
                        id="btn-download-csv",
                        n_clicks=0,
                        className="btn btn-primary mb-3"
                    ),
                    style={"textAlign": "left"}  # aligns button to the left
                ),
                dcc.Download(id="download-dataframe-csv")
            ]),

            dash_table.DataTable(
                data=allocation_df.to_dict('records'),
                columns=[{"name": col, "id": col} for col in allocation_df.columns],
                page_size=10,
                sort_action='native',
                style_table={'overflowX': 'auto', 'maxWidth': '100%', 'margin': 'auto',
                             'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"},
                style_header={
                    'backgroundColor': '#205081', 'color': '#f0f4f8', 'fontWeight': '600', 'fontSize': '15px',
                    'border': '1px solid #183b6e', 'textAlign': 'center', 'whiteSpace': 'normal', 'letterSpacing': '0.03em'
                },
                style_cell={
                    'backgroundColor': '#e7edf7', 'color': '#102a54', 'padding': '10px 14px', 'fontSize': '14px',
                    'border': '1px solid #c1c9de', 'textAlign': 'left', 'whiteSpace': 'normal',
                    'lineHeight': '1.4', 'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
                },
                style_data_conditional=[
                    {'if': {'row_index': 'even'}, 'backgroundColor': '#d7e0f4'},
                    {'if': {'state': 'active'}, 'backgroundColor': '#aac4f7', 'border': '1px solid #517acc'},
                    {'if': {'state': 'selected'}, 'backgroundColor': '#8aa6e8',
                     'border': '1px solid #3f5f9e', 'color': '#f9fafc', 'fontWeight': '600'},
                ],
                style_cell_conditional=[
                    {'if': {'column_id': 'Ward code'}, 'textAlign': 'center', 'fontWeight': '600'},
                    {'if': {'column_id': 'Borough code'}, 'textAlign': 'center', 'fontWeight': '600'}
                ],
                page_action='native',
                filter_action='native'
            )
        ])

# TODO: 1 CALLBACK FOR THE FORECASTING TAB CI PLOT

@callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-download-csv", "n_clicks"),
    Input("forecast-tabs", "value"),
    Input("borough-dropdown", "value"),
    prevent_initial_call=True
)
def download_table(n_clicks, tab_value, selected_boroughs):
    triggered_id = ctx.triggered_id

    # Only proceed if the download button was clicked
    if triggered_id != "btn-download-csv" or not n_clicks:
        return dash.no_update

    # Prepare dataframe based on the tab and filter
    if tab_value == "forecasts":
        df = prepare_forecast_table(selected_boroughs)
        filename = "forecast_table.csv"
    elif tab_value == "allocation":
        df = prepare_allocation(selected_boroughs)
        filename = "allocation_table.csv"
    else:
        return dash.no_update

    # Return CSV file download
    return dcc.send_data_frame(df.to_csv, filename, index=False)



# Path to JSON charts
forecast_path = "src/assets/forecast_charts"

@app.callback(
    Output("forecast-chart-display", "children"),
    [
        Input("forecast-table", "derived_virtual_data"),
        Input("forecast-table", "selected_rows")
    ],
    prevent_initial_call=True
)
def display_forecast_chart(rows, selected_rows):
    if not rows or selected_rows is None or len(selected_rows) == 0:
        return None

    selected_row = rows[selected_rows[0]]
    ward_code = selected_row.get("Ward code")  # Adjust if column name differs

    json_filename = f"{ward_code}_forecast.json"
    json_path = os.path.join(forecast_path, json_filename)

    if not os.path.exists(json_path):
        return html.Div(f"No chart found for ward: {ward_code}", className="text-danger")

    with open(json_path, "r") as f:
        chart = pio.from_json(json.dumps(json.load(f)))

    # ✨ Optional: Adjust trace colors for better visibility
    for trace in chart.data:
        name = trace.name.lower() if trace.name else ""
        if 'forecast' in name:
            trace.line.color = "#00cfff"  # bright cyan
        elif 'upper' in name or 'lower' in name:
            trace.line.color = "#ff8800"  # orange for CI bounds
        elif 'actual' in name:
            trace.line.color = "#ffffff"  # white for actual data

    # ✨ Apply dark mode styling
    chart.update_layout(
        plot_bgcolor="#1e1e2f",
        paper_bgcolor="#1e1e2f",
        font=dict(color="#f0f0f0"),
        title_font_size=18,
        margin=dict(t=40, b=40, l=40, r=40),
        xaxis=dict(gridcolor='#333333'),
        yaxis=dict(gridcolor="#333333"),
        legend=dict(
            x=0.99, y=0.99,
            xanchor="right", yanchor="top",
            bgcolor="rgba(30,30,30,0.6)",
            bordercolor="#444444",
            borderwidth=1,
            font=dict(size=12, color="#ffffff")
        )
    )

    return dcc.Graph(figure=chart, config={"displayModeBar": False})


if __name__ == '__main__':
    app.run(debug=False)  # Change debug to False to hide debug messages
