import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

gdf = gpd.read_file("data/boundaries/ward boundaries 2018/London_Ward_CityMerged.shp")

imd_df = pd.read_excel("data/processed/processed/London wards id2019 summary measures.xlsx")


# Plot
merged = gdf.merge(imd_df, left_on="NAME", right_on="Ward Name")
# Plot IMD heatmap
merged.plot(column="IMD average score", cmap="OrRd", legend=True, edgecolor="black", figsize=(12, 10))
plt.title("IMD Average Score by Ward")
plt.axis("off")
plt.show()