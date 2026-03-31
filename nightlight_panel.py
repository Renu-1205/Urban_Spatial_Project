import os
import re
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from libpysal.weights import Queen

# Paths
shapefile_path = r"D:\Urban_Spatial_Project\Data\Shapefiles\2011_Dist.shp"
raster_dir = r"D:\Urban_Spatial_Project\Data\Nightlights"

district_csv = r"D:\Urban_Spatial_Project\Data\district_nl_dataset.csv"
panel_csv = r"D:\Urban_Spatial_Project\Data\nightlight_panel.csv"

# Load shapefile
districts = gpd.read_file(shapefile_path)

# Remove spatial islands
w = Queen.from_dataframe(districts)
districts = districts.drop(index=w.islands).copy()

# Compute district area
districts_proj = districts.to_crs(epsg=7755)
districts["area_sqkm"] = districts_proj.geometry.area / 1e6

# Identify raster files
raster_files = []

for f in os.listdir(raster_dir):
    if f.endswith(".tif"):
        year = re.search(r"\d{4}", f)
        if year:
            raster_files.append((int(year.group()), f))

raster_files = sorted(raster_files)

if len(raster_files) == 0:
    raise ValueError("No raster files detected")

# Extract nightlight values
for year, raster_file in raster_files:

    raster_path = os.path.join(raster_dir, raster_file)
    values = []

    with rasterio.open(raster_path) as nl:

        for _, row in districts.iterrows():

            geom = [row.geometry]
            masked, _ = mask(nl, geom, crop=True)

            data = masked[0]
            data = np.where(data < 0, np.nan, data)

            values.append(np.nanmean(data))

    districts[f"nl_{year}"] = values

print("Nightlight extraction completed")

# Save district dataset
districts.to_csv(district_csv, index=False)
print("District dataset saved")

# Convert to panel format
nl_columns = [c for c in districts.columns if c.startswith("nl_")]

panel = districts.melt(
    id_vars=[
        "DISTRICT",
        "ST_NM",
        "ST_CEN_CD",
        "DT_CEN_CD",
        "censuscode",
        "area_sqkm"
    ],
    value_vars=nl_columns,
    var_name="year",
    value_name="nightlight"
)

panel["year"] = panel["year"].str.replace("nl_", "").astype(int)

# Save panel dataset
panel.to_csv(panel_csv, index=False)

print("Panel dataset created")
print("Rows:", len(panel))
print("Years:", panel["year"].unique())