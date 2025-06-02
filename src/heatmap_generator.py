import folium
import geopandas as gpd
import pandas as pd
from branca.element import Figure

def generate_imd_heatmap(gdf_wards, deprivation_df):
    merged = gdf_wards.merge(deprivation_df, left_on="WD24NM", right_on="Ward name")
    merged = merged.to_crs(epsg=4326)
    geojson_data = merged.to_json()

    fig = Figure()
    imd_map = folium.Map(location=[51.5074, -0.1278], zoom_start=10, tiles='cartodbpositron')
    fig.add_child(imd_map)

    folium.Choropleth(
        geo_data=geojson_data,
        name="choropleth",
        data=merged,
        columns=["WD24NM", "Index of Multiple Deprivation (IMD) Score"],
        key_on="feature.properties.WD24NM",
        fill_color="OrRd",
        fill_opacity=0.7,
        line_opacity=0.9,
        legend_name="IMD Score",
    ).add_to(imd_map)

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

    return fig.render()
