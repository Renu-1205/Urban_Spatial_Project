import os
import re
import rasterio
from rasterio.mask import mask
import numpy as np
import geopandas as gpd
from libpysal.weights import Queen

# --- Paths ---
shapefile_path = r"D:\Urban_Spatial_Project\Data\Shapefiles\2011_Dist.shp"
raster_dir = r"D:\Urban_Spatial_Project\Data\Nightlights"
output_csv = r"D:\Urban_Spatial_Project\Data\district_nl_2013_2021_clean.csv"

# --- Load shapefile ---
districts = gpd.read_file(shapefile_path)

# --- Remove islands ---
w = Queen.from_dataframe(districts)
districts = districts.drop(index=w.islands).copy()

# --- Project to equal-area CRS ---
districts_proj = districts.to_crs(epsg=7755)
districts["area_sqkm"] = districts_proj.geometry.area / 1e6

# --- Process rasters ---
raster_files = [f for f in os.listdir(raster_dir) if f.endswith(".tif")]
if not raster_files:
    raise FileNotFoundError(f"No .tif raster files found in {raster_dir}")

nl_cols = []
for f in raster_files:
    year_match = re.search(r'\d{4}', f)
    if year_match:
        year = year_match.group()
        col_name = f"nl_{year}"
        nl_cols.append(col_name)
        results = []

        with rasterio.open(os.path.join(raster_dir, f)) as nl:
            for idx, row in districts.iterrows():
                geom = [row.geometry]
                masked, _ = mask(nl, geom, crop=True)
                data = masked[0]
                data = np.where(data < 0, np.nan, data)
                results.append(np.nanmean(data))

        districts[col_name] = results

# --- Keep relevant columns ---
cols_to_keep = ['DISTRICT', 'ST_NM', 'ST_CEN_CD', 'DT_CEN_CD', 'censuscode', 'geometry', 'area_sqkm'] + nl_cols
districts = districts[cols_to_keep]

# --- Save ---
districts.to_csv(output_csv, index=False)
print("Saved CSV with NL columns included at", output_csv)

import pandas as pd

# Load CSV
df = pd.read_csv(r"D:\Urban_Spatial_Project\Data\district_nl_2013_2021_clean.csv")

# Check first 5 rows
print(df.head())

# Check for missing values
print(df.isna().sum())

# Optional: fill NaNs or keep them
df.fillna(0, inplace=True)  # if you want to replace NaNs with 0
import matplotlib.pyplot as plt

# Example: plot Adilabad
district = df[df['DISTRICT'] == 'Adilabad']
years = [f'nl_{y}' for y in range(2013, 2022)]
values = district[years].values.flatten()

plt.plot(range(2013, 2022), values, marker='o')
plt.title('Nightlight trend: Adilabad')
plt.xlabel('Year')
plt.ylabel('Nightlight Intensity')
plt.show()
import pandas as pd

df = pd.read_csv("D:/Urban_Spatial_Project/Data/district_nl_2013_2021_clean.csv")

df_long = df.melt(
    id_vars=['DISTRICT','ST_NM','area_sqkm'],
    value_vars=[f'nl_{y}' for y in range(2013,2022)],
    var_name='year',
    value_name='nightlight'
)

df_long['year'] = df_long['year'].str.replace('nl_','').astype(int)

df_long.to_csv("D:/Urban_Spatial_Project/Data/nightlight_panel.csv", index=False)