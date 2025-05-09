import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import os
import mapclassify
from shapely.geometry import MultiPolygon


# Load ward shapefile
file_path = "data/boundaries/ward boundaries 2018/London_Ward.shp"
wards = gpd.read_file(file_path)

base_dir = "data/crime 2022-2025"

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

import folium
from folium.plugins import HeatMap

top_ward_names = top10["NAME"].tolist()

for ward_name in top_ward_names:
    ward_geom = wards[wards["NAME"] == ward_name].geometry.values[0]
    
    ward_points = burglary_gdf[burglary_gdf.within(ward_geom)]
    
    if not ward_points.empty:
        print(f"\n--- Heatmap for {ward_name} ---")
        m = folium.Map(
            location=[ward_points["Latitude"].mean(), ward_points["Longitude"].mean()],
            zoom_start=14
        )
        HeatMap(ward_points[["Latitude", "Longitude"]].values.tolist(), radius=10).add_to(m)
        display(m)
    else:
        print(f"{ward_name}: No burglary points found.")

import matplotlib.pyplot as plt

yearly_data = {
    "2022": [0]*12,
    "2023": [0]*12,
    "2024": [0]*12,
    "2025": [0]*12,
}

for year in range(2022, 2026):
    for month in range(1, 13):
        month_str = f"{year}-{month:02d}"
        city_file = os.path.join(base_path, month_str, f"{month_str}-city-of-london-street.csv")
        metro_file = os.path.join(base_path, month_str, f"{month_str}-metropolitan-street.csv")
        monthly_count = 0

        for file in [city_file, metro_file]:
            if os.path.exists(file):
                df = pd.read_csv(file)
                df = df[df["Crime type"].str.lower() == "burglary"]
                monthly_count += len(df)

        yearly_data[str(year)][month - 1] = monthly_count

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

for year, counts in yearly_data.items():
    plt.figure(figsize=(10, 5))
    plt.bar(months, counts, color="darkorange")
    plt.title(f"Burglary Counts per Month – {year}")
    plt.xlabel("Month")
    plt.ylabel("Number of Burglaries")
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()
