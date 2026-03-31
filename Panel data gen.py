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

districts = gpd.read_file(shapefile_path)

# -------------------------------------------------------
# Remove Spatial Islands (districts with no neighbors)
# -------------------------------------------------------

w = Queen.from_dataframe(districts)
districts = districts.drop(index=w.islands).copy()

# -------------------------------------------------------
# Compute District Area (sq km)
# -------------------------------------------------------

districts_proj = districts.to_crs(epsg=7755)
districts["area_sqkm"] = districts_proj.geometry.area / 1e6

# -------------------------------------------------------
# Identify Nightlight Raster Files
# -------------------------------------------------------

raster_files = [f for f in os.listdir(raster_dir) if f.endswith(".tif")]

if not raster_files:
    raise FileNotFoundError("No nightlight raster files found")

nl_cols = []

# -------------------------------------------------------
# Extract Nightlight Values by District
# -------------------------------------------------------

for raster_file in raster_files:

    year_match = re.search(r'\d{4}', raster_file)

    if year_match:

        year = year_match.group()
        col_name = f"nl_{year}"
        nl_cols.append(col_name)

        results = []

        raster_path = os.path.join(raster_dir, raster_file)

        with rasterio.open(raster_path) as nl:

            for idx, row in districts.iterrows():

                geom = [row.geometry]

                masked, _ = mask(nl, geom, crop=True)

                data = masked[0]

                data = np.where(data < 0, np.nan, data)

                results.append(np.nanmean(data))

        districts[col_name] = results

# -------------------------------------------------------
# Keep Relevant Columns
# -------------------------------------------------------

cols_to_keep = [
    'DISTRICT',
    'ST_NM',
    'ST_CEN_CD',
    'DT_CEN_CD',
    'censuscode',
    'geometry',
    'area_sqkm'
] + nl_cols

districts = districts[cols_to_keep]

# -------------------------------------------------------
# Save Clean District Dataset
# -------------------------------------------------------

districts.to_csv(clean_csv, index=False)

print("District-level dataset saved")

# -------------------------------------------------------
# Load Dataset for Inspection
# -------------------------------------------------------

df = pd.read_csv(clean_csv)

print("\nFirst five rows:")
print(df.head())

print("\nMissing values by column:")
print(df.isna().sum())

# Optional handling of missing values
df.fillna(0, inplace=True)

# -------------------------------------------------------
# Example Visualization: Adilabad Nightlight Trend
# -------------------------------------------------------

district = df[df['DISTRICT'] == 'Adilabad']

years = [f'nl_{y}' for y in range(2013, 2022)]

values = district[years].values.flatten()

plt.figure()

plt.plot(range(2013, 2022), values, marker='o')

plt.title('Nightlight Trend: Adilabad')

plt.xlabel('Year')

plt.ylabel('Nightlight Intensity')

plt.show()

# -------------------------------------------------------
# Convert Wide Dataset to Panel Format
# -------------------------------------------------------

df_long = df.melt(
    id_vars=['DISTRICT', 'ST_NM', 'area_sqkm'],
    value_vars=[f'nl_{y}' for y in range(2013, 2022)],
    var_name='year',
    value_name='nightlight'
)

df_long['year'] = df_long['year'].str.replace('nl_', '').astype(int)

# -------------------------------------------------------
# Save Panel Dataset
# -------------------------------------------------------

df_long.to_csv(panel_csv, index=False)

print("Panel dataset saved:", panel_csv)

import pandas as pd

# assume your dataframe name is districts
panel = districts.melt(
    id_vars=["DISTRICT","ST_NM","ST_CEN_CD","DT_CEN_CD","censuscode","area_sqkm"],
    value_vars=["nl_2013","nl_2014","nl_2015","nl_2016","nl_2017","nl_2018","nl_2019","nl_2020","nl_2021"],
    var_name="year",
    value_name="nightlight"
)

panel["year"] = panel["year"].str.replace("nl_","").astype(int)

print(panel.head())