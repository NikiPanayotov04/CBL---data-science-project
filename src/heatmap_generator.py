import folium
import geopandas as gpd
import pandas as pd
from branca.element import Figure

def generate_transport_stops_scatter(transport_stops_df):
    """
    Returns a folium FeatureGroup containing all transport stops as scatter markers.
    """
    # Create a feature group layer to hold all transport stop markers
    stops_layer = folium.FeatureGroup(name="Transport Stops")

    # Loop through each transport stop and add it as a blue CircleMarker with a tooltip
    for _, row in transport_stops_df.iterrows():
        tooltip = str(row["CommonName"]) if pd.notnull(row["CommonName"]) else "Unknown"
        
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=2,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.7,
            tooltip=tooltip  # Show stop name on hover
        ).add_to(stops_layer)

    return stops_layer

def generate_base_ward_map(gdf_wards, stops_df):
    """
    Generates a folium map showing London wards and transport stops.
    """
    # Convert ward geometries to WGS84 (lat/lon) for folium
    geojson_data = gdf_wards.to_crs(epsg=4326).to_json()

    # Create the base map and attach it to a Figure for rendering
    fig = Figure()
    wards_map = folium.Map(location=[51.5074, -0.1278], zoom_start=10, tiles='cartodbpositron')
    fig.add_child(wards_map)
    
    # Overlay ward boundaries with tooltip info
    folium.GeoJson(
        geojson_data,
        name="Wards",
        tooltip=folium.GeoJsonTooltip(
            fields=["WD24CD", "WD24NM"],
            aliases=["Ward code:", "Ward Name:"],
            localize=True
        ),
        style_function=lambda x: {"fillOpacity": 0, "color": "black", "weight": 0.5},
    ).add_to(wards_map)

    # Add transport stops as a separate layer
    stops_layer = generate_transport_stops_scatter(stops_df)
    stops_layer.add_to(wards_map)

    # Add layer control for toggling wards/stops
    folium.LayerControl(position="topright", collapsed=False).add_to(wards_map)

    return fig.render()

def generate_imd_heatmap(gdf_wards, deprivation_df, stops_df):
    """
    Creates a folium choropleth map visualizing Index of Multiple Deprivation (IMD) scores across wards,
    overlaid with transport stops.
    """
    # Merge ward shapes with deprivation data on ward name
    merged = gdf_wards.merge(deprivation_df, left_on="WD24NM", right_on="Ward name")
    merged = merged.to_crs(epsg=4326)
    geojson_data = merged.to_json()

    # Create map and attach to Figure
    fig = Figure()
    imd_map = folium.Map(location=[51.5074, -0.1278], zoom_start=10, tiles='cartodbpositron')
    fig.add_child(imd_map)

    # Add IMD choropleth
    folium.Choropleth(
        geo_data=geojson_data,
        name="IMD Heatmap",
        data=merged,
        columns=["WD24NM", "Index of Multiple Deprivation (IMD) Score"],
        key_on="feature.properties.WD24NM",
        fill_color="OrRd",
        fill_opacity=0.7,
        line_opacity=0.9,
        legend_name="IMD Score",
    ).add_to(imd_map)

    # Tooltip for showing hover data
    folium.GeoJson(
        geojson_data,
        name="Wards",
        tooltip=folium.GeoJsonTooltip(
            fields=["WD24CD", "Ward name", "Index of Multiple Deprivation (IMD) Score"],
            aliases=["Ward code:", "Ward Name:", "IMD Score:"],
            localize=True
        ),
        style_function=lambda x: {"fillOpacity": 0, "color": "black", "weight": 0.5},
    ).add_to(imd_map)
    
    # Add transport stops layer
    stops_layer = generate_transport_stops_scatter(stops_df)
    stops_layer.add_to(imd_map)

    # Add layer control for toggling wards/stops
    folium.LayerControl(position="topright", collapsed=False).add_to(imd_map)

    return fig.render()

def generate_forecasted_crime_counts_heatmap(gdf_wards, forecasted_crime_counts_df, stops_df):
    """
    Creates a folium choropleth map visualizing forecasted crime counts across wards,
    overlaid with transport stops.
    """
    # Merge ward shapes with forecasted crime data
    merged = gdf_wards.merge(forecasted_crime_counts_df, left_on="WD24NM", right_on="Ward name")
    merged = merged.to_crs(epsg=4326)
    geojson_data = merged.to_json()

    # Create map and attach to Figure
    fig = Figure()
    forecasted_crime_counts_map = folium.Map(location=[51.5074, -0.1278], zoom_start=10, tiles='cartodbpositron')
    fig.add_child(forecasted_crime_counts_map)

    # Add choropleth showing crime predictions
    folium.Choropleth(
        geo_data=geojson_data,
        name="choropleth",
        data=merged,
        columns=["WD24NM", "Predicted_Crime_Count"],
        key_on="feature.properties.WD24NM",
        fill_color="OrRd",
        fill_opacity=0.7,
        line_opacity=0.9,
        legend_name="Forecasted Crime Count",
    ).add_to(forecasted_crime_counts_map)

    # Tooltip for showing hover data
    folium.GeoJson(
        geojson_data,
        name="Wards",
        tooltip=folium.GeoJsonTooltip(
            fields=["WD24CD", "Ward name", "Predicted_Crime_Count"],
            aliases=["Ward code:", "Ward Name:", "Forecasted Crime Count:"],
            localize=True
        ),
        style_function=lambda x: {"fillOpacity": 0, "color": "black", "weight": 0.5},
    ).add_to(forecasted_crime_counts_map)
    
    # Add transport stops layer
    stops_layer = generate_transport_stops_scatter(stops_df)
    stops_layer.add_to(forecasted_crime_counts_map)

    # Add layer control for toggling wards/stops
    folium.LayerControl(position="topright", collapsed=False).add_to(forecasted_crime_counts_map)

    return fig.render()

