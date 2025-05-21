import dash
from dash import html
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import os
from datetime import datetime


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

def load_demographic_data():
    try:
        file_path = 'data/processed/lsoa level/deprivation_11_to_21_london.csv'
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            print(f"File not found: {file_path}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error loading demographic data: {str(e)}")
        return pd.DataFrame()

def load_census_data():
    try:
        file_path = 'data/processed/ward level/census_by_ward.csv'
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            print(f"File not found: {file_path}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error loading census data: {str(e)}")
        return pd.DataFrame()

# Store initial data in memory
crime_df = load_crime_data()
demographic_df = load_demographic_data()
census_df = load_census_data()

# Sidebar menu


# Main content area
def homepage():
    return dbc.Card([
        dbc.CardBody([
            html.H1("Automated Police Demand Forecasting", className="card-title"),
            html.P("Welcome to the Police Demand Forecasting Dashboard.", className="card-text"),
            html.H2("Problem Description", className="mb-4 mt-4"),

            # Problem Items
            html.Div([
                html.Div([
                    html.Span("1", className="badge-number me-3"),
                    html.Span([
                        html.B("High Prevalence: "),
                        "Residential burglary accounts for 4.5% of all crimes in Greater London."
                    ])
                ], className="problem-box mb-3"),

                html.Div([
                    html.Span("2", className="badge-number me-3"),
                    html.Span([
                        html.B("Low Resolution Rate: "),
                        "82% of residential burglaries went unsolved in 2022/2023, highlighting gaps in current policing effectiveness."
                    ])
                ], className="problem-box mb-3"),

                html.Div([
                    html.Span("3", className="badge-number me-3"),
                    html.Span([
                        html.B("Eroding Public Trust: "),
                        "The combination of frequency and lack of resolution undermines public confidence in police protection and safety."
                    ])
                ], className="problem-box mb-3"),
            ]),

            html.Hr(),

            # London Image
            html.Img(src="/assets/london_image.jpg", style={"width": "100%", "maxWidth": "800px", "margin": "20px auto", "display": "block"}),

            html.Hr(),

            # Contributors
            html.Div([
                html.H5("Contributors"),
                html.Ul([
                    html.Li("Niki Panayotov"),
                    html.Li("Team members from Trinity College London"),
                ])
            ]),

            html.Footer("Project developed by Niki Panayotov and team", 
                        style={"fontSize": "0.85rem", "color": "#aaa", "marginTop": "2rem", "textAlign": "center"})
        ])
    ])

def data_explorer():
    return dbc.Card([
        dbc.CardBody([
            html.H1("Data Explorer", className="card-title"),
            html.P("Welcome to the Data Explorer section. Here you can access and analyze various datasets related to police demand forecasting in London.", className="card-text text-center"),
            html.P("Our datasets include:", className="card-text mt-4 text-center"),
            html.Div([
                html.Ul([
                    html.Li("Crime Data: Monthly burglary statistics across London boroughs from 2022 to 2025", className="text-center"),
                    html.Li("Demographic Data: Information about population, household composition, and dwelling occupancy", className="text-center"),
                    html.Li("Census Data: Ward-level demographic information from the latest census", className="text-center")
                ], className="card-text mb-4", style={"listStyle": "none", "padding": "0"})
            ], className="d-flex justify-content-center"),
            html.P("Select a dataset below to begin exploring:", className="card-text text-center"),
            html.Div([
                dbc.Button("Crime Data", href="/data/crime", color="primary", className="me-3"),
                dbc.Button("Demographic Data", href="/data/demographic", color="primary", className="me-3"),
                dbc.Button("Census Data", href="/data/census", color="primary", className="me-3"),
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
                        if not (year == 2022 and month < 4) and not (year == 2025 and month > 2)  # Only show from Apr 2022 to Feb 2025
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

def demographic_data():
    return dbc.Card([
        dbc.CardBody([
            html.H1("Demographic Data", className="card-title"),
            html.P("Explore different demographic datasets for London:", className="card-text text-center mb-4"),
            
            # Tabs for different datasets
            dbc.Tabs([
                # Deprivation Tab
                dbc.Tab([
                    html.Div([
                        html.H4("Deprivation Indices (2011-2021)", className="mt-3 text-center"),
                        html.P("This dataset contains deprivation indices for London areas from 2011 to 2021, including income, employment, health, education, and living environment indicators.", className="card-text text-center"),
                        html.Div([
                            dbc.Button("Show Deprivation Data", id="btn-deprivation", color="primary", className="mt-3")
                        ], className="text-center"),
                        html.Div(id="deprivation-data-table", className="mt-3")
                    ], className="p-3")
                ], label="Deprivation Indices", label_style={"textAlign": "center"}),
                
                # Household Composition Tab
                dbc.Tab([
                    html.Div([
                        html.H4("Household Composition", className="mt-3 text-center"),
                        html.P("Data about household structures in London, including family types, household sizes, and living arrangements.", className="card-text text-center"),
                        html.Div([
                            dbc.Button("Show Household Data", id="btn-household", color="primary", className="mt-3")
                        ], className="text-center"),
                        html.Div(id="household-data-table", className="mt-3")
                    ], className="p-3")
                ], label="Household Composition", label_style={"textAlign": "center"}),
                
                # Dwelling Occupancy Tab
                dbc.Tab([
                    html.Div([
                        html.H4("Dwelling Occupancy", className="mt-3 text-center"),
                        html.P("Information about housing occupancy patterns, including occupancy status, property types, and tenure.", className="card-text text-center"),
                        html.Div([
                            dbc.Button("Show Dwelling Data", id="btn-dwelling", color="primary", className="mt-3")
                        ], className="text-center"),
                        html.Div(id="dwelling-data-table", className="mt-3")
                    ], className="p-3")
                ], label="Dwelling Occupancy", label_style={"textAlign": "center"})
            ], className="mt-3")
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
                    html.Li("Population demographics and age distribution", className="text-center"),
                    html.Li("Ethnic composition and cultural diversity", className="text-center"),
                    html.Li("Economic activity and employment status", className="text-center"),
                    html.Li("Education levels and qualifications", className="text-center"),
                    html.Li("Housing characteristics and tenure", className="text-center")
                ], className="card-text mb-4", style={"listStylePosition": "inside", "paddingLeft": "0"}),
                
                # Centered button
                html.Div([
                    dbc.Button("Show Census Data", id="btn-census", color="primary", className="mt-3")
                ], className="text-center"),
                
                # Data table container
                html.Div(id="census-data-table", className="mt-3")
            ], className="p-3")
        ])
    ])

def forecasting():
    return dbc.Card([
        dbc.CardBody([
            html.H1("Forecasting", className="card-title"),
            html.P("Predicted demand and resource allocation.", className="card-text")
        ])
    ])

def map_view():
    return dbc.Card([
        dbc.CardBody([
            html.H1("Map View", className="card-title"),
            html.P("Geospatial analysis of crime patterns.", className="card-text")
        ])
    ])

def about():
    return dbc.Card([
        dbc.CardBody([
            html.H1("About", className="card-title"),
            html.P("Project developed by Niki Panayotov and team.", className="card-text")
        ])
    ])


sidebar = dbc.Col([
    html.H4("Menu", className="text-white mt-4"),
    html.Hr(),
    dbc.Nav([
        dbc.NavLink("Home", href="/", active="exact", className="nav-link"),
        dbc.NavLink("Data Explorer", href="/data", active="exact", className="nav-link"),
        dbc.NavLink("Crime Data", href="/data/crime", active="exact", className="nav-link ms-3"),
        dbc.NavLink("Demographic Data", href="/data/demographic", active="exact", className="nav-link ms-3"),
        dbc.NavLink("Census Data", href="/data/census", active="exact", className="nav-link ms-3"),
        dbc.NavLink("Forecasting", href="/forecast", active="exact", className="nav-link"),
        dbc.NavLink("Map View", href="/map", active="exact", className="nav-link"),
        dbc.NavLink("About", href="/about", active="exact", className="nav-link")
    ], vertical=True, pills=True),
], width=2, className="sidebar")

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
    elif pathname == "/data/demographic":
        return demographic_data()
    elif pathname == "/data/census":
        return census_data()
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
            if (year == 2022 and month_num < 4) or year < 2022 or (year == 2025 and month_num > 2) or year > 2025:
                return None, "Selected month is out of range. Please select a month between April 2022 and February 2025."
            
            # Load data for selected month
            df = load_crime_data(month)
            
            if not df.empty:
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
                            df.head(10),
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
     Output("household-data-table", "children"),
     Output("dwelling-data-table", "children")],
    [Input("btn-deprivation", "n_clicks"),
     Input("btn-household", "n_clicks"),
     Input("btn-dwelling", "n_clicks")],
    prevent_initial_call=True
)
def display_demographic_data(deprivation_clicks, household_clicks, dwelling_clicks):
    # Initialize all outputs as None
    deprivation_output = None
    household_output = None
    dwelling_output = None
    
    # Check which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        return None, None, None
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    n_clicks = ctx.triggered[0]['value']
    
    # Only show data on odd clicks
    if n_clicks and n_clicks % 2 == 1:
        try:
            if button_id == "btn-deprivation":
                df = pd.read_csv('data/processed/lsoa level/deprivation_11_to_21_london.csv')
                if not df.empty:
                    deprivation_output = dbc.Table.from_dataframe(
                        df.head(10),
                        striped=True,
                        bordered=True,
                        hover=True,
                        responsive=True,
                        className="table-dark"
                    )
            elif button_id == "btn-household":
                df = pd.read_csv('data/processed/lsoa level/household_composition_london.csv')
                if not df.empty:
                    household_output = dbc.Table.from_dataframe(
                        df.head(10),
                        bordered=True,
                        hover=True,
                        responsive=True,
                        className="table-dark"
                    )
            elif button_id == "btn-dwelling":
                df = pd.read_csv('data/processed/lsoa level/dwelling_occupancy_london.csv')
                if not df.empty:
                    dwelling_output = dbc.Table.from_dataframe(
                        df.head(10),
                        striped=True,
                        bordered=True,
                        hover=True,
                        responsive=True,
                        className="table-dark"
                    )
        except Exception as e:
            return html.Div(f"Error loading data: {str(e)}", className="text-danger"), None, None
    
    return deprivation_output, household_output, dwelling_output

@app.callback(
    Output("census-data-table", "children"),
    Input("btn-census", "n_clicks"),
    prevent_initial_call=True
)
def display_census_data(n_clicks):
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

if __name__ == '__main__':
    app.run(debug=False)  # Change debug to False to hide debug messages
