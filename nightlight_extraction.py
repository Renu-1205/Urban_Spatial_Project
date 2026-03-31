# -------------------------------------------------------
# Urban Spatial Project: District Nightlight Extraction
# -------------------------------------------------------

import os
import re
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from libpysal.weights import Queen
import matplotlib.pyplot as plt


# -------------------------------------------------------
# Paths
# -------------------------------------------------------

shapefile_path = r"D:\Urban_Spatial_Project\Data\Shapefiles\2011_Dist.shp"
raster_dir = r"D:\Urban_Spatial_Project\Data\Nightlights"

clean_csv = r"D:\Urban_Spatial_Project\Data\district_nl_2013_2021_clean.csv"
panel_csv = r"D:\Urban_Spatial_Project\Data\nightlight_panel.csv"


# -------------------------------------------------------
# Load District Shapefile
# -------------------------------------------------------

print("Loading district shapefile...")
districts = gpd.read_file(shapefile_path)


# -------------------------------------------------------
# Remove Spatial Islands (districts without neighbors)
# -------------------------------------------------------

print("Removing spatial islands...")
w = Queen.from_dataframe(districts)
districts = districts.drop(index=w.islands).copy()


# -------------------------------------------------------
# Compute District Area (sq km)
# -------------------------------------------------------

print("Computing district area...")
districts_proj = districts.to_crs(epsg=7755)
districts["area_sqkm"] = districts_proj.geometry.area / 1e6


# -------------------------------------------------------
# Identify Nightlight Raster Files
# -------------------------------------------------------

print("Detecting raster files...")

raster_files = [f for f in os.listdir(raster_dir) if f.endswith(".tif")]

if len(raster_files) == 0:
    raise FileNotFoundError("No nightlight raster files found")

raster_files.sort()

nl_cols = []


# -------------------------------------------------------
# Extract Nightlight Values by District
# -------------------------------------------------------

print("Extracting nightlight values...")

for raster_file in raster_files:

    year_match = re.search(r"\d{4}", raster_file)

    if year_match:

        year = year_match.group()
        col_name = f"nl_{year}"
        nl_cols.append(col_name)

        raster_path = os.path.join(raster_dir, raster_file)

        values = []

        with rasterio.open(raster_path) as nl:

            for _, row in districts.iterrows():

                geom = [row.geometry]

                masked, _ = mask(nl, geom, crop=True)

                data = masked[0]

                data = np.where(data < 0, np.nan, data)

                values.append(np.nanmean(data))

        districts[col_name] = values

        print(f"Finished {year}")


# -------------------------------------------------------
# Keep Relevant Columns
# -------------------------------------------------------

cols_to_keep = [
    "DISTRICT",
    "ST_NM",
    "ST_CEN_CD",
    "DT_CEN_CD",
    "censuscode",
    "geometry",
    "area_sqkm",
] + nl_cols

districts = districts[cols_to_keep]


# -------------------------------------------------------
# Save District-Level Dataset
# -------------------------------------------------------

print("Saving district dataset...")
districts.to_csv(clean_csv, index=False)

print("District-level dataset saved")


# -------------------------------------------------------
# Inspect Dataset
# -------------------------------------------------------

df = pd.read_csv(clean_csv)

print("\nFirst five rows:")
print(df.head())

print("\nMissing values by column:")
print(df.isna().sum())

df.fillna(0, inplace=True)


# -------------------------------------------------------
# Example Visualization
# -------------------------------------------------------

print("Creating example plot...")

district = df[df["DISTRICT"] == "Adilabad"]

years = [f"nl_{y}" for y in range(2013, 2022)]
values = district[years].values.flatten()

plt.figure()

plt.plot(range(2013, 2022), values, marker="o")

plt.title("Nightlight Trend: Adilabad")
plt.xlabel("Year")
plt.ylabel("Nightlight Intensity")

plt.show()


# -------------------------------------------------------
# Convert to Panel Format
# -------------------------------------------------------

print("Converting to panel format...")

df_long = df.melt(
    id_vars=["DISTRICT", "ST_NM", "area_sqkm"],
    value_vars=[f"nl_{y}" for y in range(2013, 2022)],
    var_name="year",
    value_name="nightlight",
)

df_long["year"] = df_long["year"].str.replace("nl_", "").astype(int)


# -------------------------------------------------------
# Save Panel Dataset
# -------------------------------------------------------

df_long.to_csv(panel_csv, index=False)

print("Panel dataset saved at:", panel_csv)

print(df_long.head())