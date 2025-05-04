import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

gdf = gpd.read_file("C:/Users/20231937/CBL - project/City of London - crime data/Wards-locations/London-wards-2018_ESRI/London_Ward.shp")

imd_df = pd.read_excel("C:/Users/20231937/CBL - project/City of London - crime data/London wards id2019 summary measures.xlsx")


# Plot
merged = gdf.merge(imd_df, left_on="NAME", right_on="Ward Name")
# Plot IMD heatmap
merged.plot(column="IMD average score", cmap="OrRd", legend=True, edgecolor="black", figsize=(12, 10))
plt.title("IMD Average Score by Ward")
plt.axis("off")
plt.show()