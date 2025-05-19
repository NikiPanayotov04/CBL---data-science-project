import pandas as pd
import geopandas as gpd
import folium


def main():
    df = pd.read_csv('../data/processed/ward level/census_by_ward.csv')
    gdf = gpd.read_file('../data/boundaries/ward boundaries 2018/London_Ward_CityMerged.shp')

    # Show user the available columns and ask for input
    print("Available columns to visualize:")
    for col in df.columns:
        if col != 'Ward code':
            print(f"- {col}")

    value_col = input("\nEnter the name of the column to display on the map: ")

    if value_col not in df.columns:
        print(f"Error: '{value_col}' is not a valid column name.")
        return

    # merge
    merged = gdf.merge(df, left_on='GSS_CODE', right_on='Ward code')

    # create interactive map
    m = folium.Map(location=[51.5074, -0.1278], zoom_start=10, tiles='cartodbpositron')

    join_col_shp = 'GSS_CODE'
    folium.Choropleth(
        geo_data=merged,
        data=merged,
        columns=['Ward code', value_col],
        key_on=f'feature.properties.{join_col_shp}',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=value_col
    ).add_to(m)

    # Save and display
    output_file = "../outputs/html/census_map.html"
    m.save(output_file)
    print(f"\nMap saved to {output_file}")


if __name__ == "__main__":
    main()
