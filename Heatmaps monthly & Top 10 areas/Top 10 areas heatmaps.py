import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import os
import mapclassify
from shapely.geometry import MultiPolygon


# Load ward shapefile
file_path = r"C:\Users\20230920\OneDrive - TU Eindhoven\TUE\Year 2\4rth Quarter\Multidiciplinary CBL\statistical-gis-boundaries-london\statistical-gis-boundaries-london\ESRI\London_Ward.shp"
wards = gpd.read_file(file_path)

base_dir = "C:/Users/20230920/OneDrive - TU Eindhoven/TUE/Year 2/4rth Quarter/Multidiciplinary CBL/Metropolitan and city of london 22-25"

# Get all folder names inside that directory (e.g., '2022-03', '2022-04', ...)
folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
folders.sort()
# Load and combine burglary CSVs (as before)
dfs = []
for folder in folders:
    for file in [f"{folder}-city-of-london-street.csv", f"{folder}-metropolitan-street.csv"]:
        path = os.path.join(base_dir, folder, file)
        if os.path.exists(path):
            df = pd.read_csv(path)
            df = df[df["Crime type"].str.lower() == "burglary"]
            dfs.append(df)

# Combine all burglaries
burglary_df = pd.concat(dfs, ignore_index=True).dropna(subset=["Latitude", "Longitude"])
# Convert to GeoDataFrame
wards = wards.to_crs("EPSG:4326")
geometry = [Point(xy) for xy in zip(burglary_df["Longitude"], burglary_df["Latitude"])]
burglary_gdf = gpd.GeoDataFrame(burglary_df, geometry=geometry, crs="EPSG:4326")
# Spatial join: match burglary points to wards
joined = gpd.sjoin(burglary_gdf, wards, how="inner", predicate="intersects")

# Count burglaries per ward
counts = joined.groupby("NAME").size().reset_index(name="burglary_count")

# Merge with shapefile
wards = wards.merge(counts, left_on="NAME", right_on="NAME", how="left")
wards["burglary_count"] = wards["burglary_count"].fillna(0)
wards["grouped_name"] = wards["NAME"]
wards.loc[wards["GSS_CODE"].str.startswith("E050092"), "grouped_name"] = "City of London"
print(wards[wards["GSS_CODE"].str.startswith("E050092")][["NAME", "burglary_count"]])

grouped = wards.dissolve(
    by="grouped_name",
    aggfunc={"burglary_count": "sum"} # avoids grouped_name becoming the index
).reset_index()
grouped.loc[grouped["grouped_name"] == "City of London", "geometry"] = grouped.loc[
    grouped["grouped_name"] == "City of London", "geometry"
].unary_union


# Plot choropleth
ax = grouped.plot(
    column="burglary_count",
    cmap="OrRd",
    legend=True,
    edgecolor="black",
    scheme="quantiles",
    figsize=(12, 10)
)

# Add label for City of London
city_geom = grouped[grouped["grouped_name"] == "City of London"].geometry
x, y = city_geom.centroid.iloc[0].x, city_geom.centroid.iloc[0].y
ax.text(x, y, "City of London", fontsize=10, ha="center")

ax.set_title("Burglaries by Ward (City of London grouped)")
ax.axis("off")
plt.show()

#^^Nikolas code

# Show top 10 wards with the most burglaries
top10 = counts.sort_values(by="burglary_count", ascending=False).head(10)
print("\nTop 10 wards with most burglaries:\n")
print(top10.to_string(index=False))