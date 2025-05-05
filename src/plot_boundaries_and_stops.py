# == Import ==
import geopandas as gpd
import folium
from pathlib import Path
import pandas as pd
from shapely.geometry import Point

# == Paths ==
ROOT_DIR = Path('../data/boundaries')
GREATER_LONDON_DIR = ROOT_DIR / 'greater london boundary'
BOROUGH_DIR = ROOT_DIR / 'borough boundaries 2011'
WARD_DIR = ROOT_DIR / 'ward boundaries 2018'
LSOA_DIR = ROOT_DIR / 'lsoa boundaries 2021'
STOPS_PATH = Path('../data/additional/processed/stops_london.csv')
OUTPUT_DIR = Path('../outputs/html')

# == Load shapefiles ==
# load the Greater London boundary shapefile
gdf_gl = gpd.read_file(GREATER_LONDON_DIR / 'London_GLA_Boundary.shp')

# load the borough boundaries shapefile
gdf_boroughs = gpd.read_file(BOROUGH_DIR / 'London_Borough_Excluding_MHW.shp')

# load the ward shapefile (with City of London merged)
gdf_wards = gpd.read_file(WARD_DIR / 'London_Ward_CityMerged.shp')

# simplify the geometry to speed up rendering
gdf_gl_simplified = gdf_gl.simplify(0.001)
gdf_boroughs_simplified = gdf_boroughs.simplify(0.001)
gdf_wards_simplified = gdf_wards.simplify(0.001)

# == Load CSV and convert to GeoDataFrame ==
df_stops = pd.read_csv(STOPS_PATH)
geometry = [Point(xy) for xy in zip(df_stops['Longitude'], df_stops['Latitude'])]
gdf_stops = gpd.GeoDataFrame(df_stops, geometry=geometry, crs="EPSG:4326")

# == Create map ==
# create folium map centered on London
m = folium.Map(location=[51.5074, -0.1278], zoom_start=9, tiles="cartodbpositron")

# load and add all lsoa files for each borough
for lsoa_shp in LSOA_DIR.glob('*.shp'):
    gdf_lsoa = gpd.read_file(lsoa_shp)

    # simplify the LSOA boundaries for faster rendering
    gdf_lsoa_simplified = gdf_lsoa.simplify(0.001)

    # add LSOA boundaries to the map
    folium.GeoJson(
        gdf_lsoa_simplified,
        name=f"LSOA Boundaries - {lsoa_shp.stem}",
        style_function=lambda x: {
            'fillColor': 'lightyellow',
            'color': 'orange',
            'weight': 1,
            'fillOpacity': 0.2
        }
    ).add_to(m)

# add wards with city of london merged
folium.GeoJson(
    gdf_wards_simplified,
    name="Wards (City of London merged)",
    style_function=lambda x: {
        'fillColor': 'lightgreen',
        'color': 'green',
        'weight': 1,
        'fillOpacity': 0.3
    }
).add_to(m)

# add borough boundaries
folium.GeoJson(
    gdf_boroughs_simplified,
    name="Borough Boundaries",
    style_function=lambda x: {
        'fillColor': 'lightcoral',
        'color': 'red',
        'weight': 2,
        'fillOpacity': 0.3
    }
).add_to(m)

# add greater london boundary
folium.GeoJson(
    gdf_gl_simplified,
    name="Greater London Boundary",
    style_function=lambda x: {
        'fillColor': 'lightblue',
        'color': 'blue',
        'weight': 2,
        'fillOpacity': 0.2
    }
).add_to(m)

# add transport access stops as markers
stops_group = folium.FeatureGroup(name="Transport Access Nodes", show=True)
columns_to_include = ['CommonName', 'NptgLocalityCode', 'LocalityName', 'Status']
for _, row in gdf_stops.iterrows():
    popup_html = "<br>".join([f"<b>{col}:</b> {row[col]}" for col in columns_to_include])
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=0.3,
        color='purple',
        fill=True,
        fill_opacity=0.4,
        popup=folium.Popup(popup_html, max_width=300)
    ).add_to(stops_group)

stops_group.add_to(m)

# add layer control to toggle between different layers
folium.LayerControl().add_to(m)

# display the map
m

# save the map to an HTML file
m.save(OUTPUT_DIR / 'boundaries_and_stops_map.html')