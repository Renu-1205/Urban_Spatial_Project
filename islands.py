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

print("Total districts in shapefile:", len(districts))

# -------------------------------------------------------
# Build Spatial Weights (Queen Contiguity)
# -------------------------------------------------------

print("Constructing spatial weights matrix...")
w = Queen.from_dataframe(districts)

print("Total spatial units:", w.n)
print("Average neighbors:", w.mean_neighbors)

# -------------------------------------------------------
# Identify Spatial Islands
# -------------------------------------------------------

print("\nDetecting spatial islands...")

island_indices = w.islands
print("Number of islands:", len(island_indices))

if len(island_indices) > 0:

    island_districts = districts.iloc[island_indices][
        ["DISTRICT", "ST_NM", "censuscode"]
    ]

    print("\nIsland districts:")
    print(island_districts)

    # save for inspection
    island_districts.to_csv(
        r"D:\Urban_Spatial_Project\Data\spatial_islands.csv",
        index=False
    )

else:
    print("No spatial islands detected.")

# -------------------------------------------------------
# OPTIONAL: Remove Islands (after inspection)
# -------------------------------------------------------

remove_islands = False   # change to True if you want to drop them

if remove_islands and len(island_indices) > 0:

    print("\nRemoving spatial islands from dataset...")
    districts = districts.drop(index=island_indices).copy()

    print("Districts remaining:", len(districts))

    # rebuild weights after removal
    w = Queen.from_dataframe(districts)

    print("New spatial units:", w.n)
    print("New average neighbors:", w.mean_neighbors)

print("\nSpatial preprocessing complete.")


import geopandas as gpd
import matplotlib.pyplot as plt
from libpysal.weights import Queen

# -------------------------------------------------------
# Load shapefile
# -------------------------------------------------------
shp_path = r"D:\Urban_Spatial_Project\Data\Shapefiles\2011_Dist.shp"
gdf = gpd.read_file(shp_path)

# -------------------------------------------------------
# Locate Kandhamal
# -------------------------------------------------------
kandhamal = gdf[gdf["DISTRICT"] == "Kandhamal"]

print("Kandhamal record:")
print(kandhamal[["DISTRICT", "ST_NM", "censuscode"]])

# -------------------------------------------------------
# Plot Kandhamal to visually inspect borders
# -------------------------------------------------------
fig, ax = plt.subplots(figsize=(8,8))
gdf.plot(ax=ax, color="lightgrey", edgecolor="black")
kandhamal.plot(ax=ax, color="red")
plt.title("Kandhamal District Spatial Check")
plt.show()

# -------------------------------------------------------
# Check districts touching Kandhamal
# -------------------------------------------------------
neighbors = gdf[gdf.touches(kandhamal.geometry.iloc[0])]

print("\nDistricts touching Kandhamal:")
print(neighbors[["DISTRICT", "ST_NM", "censuscode"]])

# -------------------------------------------------------
# Check geometry validity
# -------------------------------------------------------
print("\nGeometry valid:", kandhamal.is_valid.values)

# -------------------------------------------------------
# Fix topology issues if present
# -------------------------------------------------------
gdf["geometry"] = gdf.buffer(0)

# rebuild spatial weights
w = Queen.from_dataframe(gdf)

print("\nSpatial islands after topology fix:")
print(w.islands)

# -------------------------------------------------------
# Check why Kandhamal is detected as a spatial island
# -------------------------------------------------------

import geopandas as gpd

# load shapefile
shp_path = r"D:\Urban_Spatial_Project\Data\Shapefiles\2011_Dist.shp"
gdf = gpd.read_file(shp_path)

# locate Kandhamal district
kandhamal = gdf[gdf["DISTRICT"] == "Kandhamal"]

print("Kandhamal geometry loaded:")
print(kandhamal[["DISTRICT","ST_NM","censuscode"]])

# -------------------------------------------------------
# 1. Check Queen-type neighbours (shared boundary/vertex)
# -------------------------------------------------------

neighbors_touch = gdf[gdf.geometry.touches(kandhamal.geometry.iloc[0])]

print("\nDistricts sharing boundary with Kandhamal:")
print(neighbors_touch[["DISTRICT","ST_NM","censuscode"]])

# -------------------------------------------------------
# 2. Check near districts (detect topology gaps)
# -------------------------------------------------------

near_districts = gdf[gdf.geometry.distance(kandhamal.geometry.iloc[0]) < 0.01]

print("\nDistricts within small distance of Kandhamal:")
print(near_districts[["DISTRICT","ST_NM","censuscode"]])

# -------------------------------------------------------
# 3. Visual confirmation
# -------------------------------------------------------

ax = gdf.plot(edgecolor="grey", figsize=(8,8))
kandhamal.plot(ax=ax)
neighbors_touch.plot(ax=ax)

print("\nMap plotted: Kandhamal and its touching neighbors.")


import geopandas as gpd
import matplotlib.pyplot as plt

shp_path = r"D:\Urban_Spatial_Project\Data\Shapefiles\2011_Dist.shp"
gdf = gpd.read_file(shp_path)

# select Kandhamal
k = gdf[gdf["DISTRICT"]=="Kandhamal"].copy()

print("Kandhamal row:")
print(k[["DISTRICT","ST_NM","censuscode"]])

# check geometry validity
print("\nGeometry valid:", k.geometry.is_valid.values)

# find nearest districts
distances = gdf.distance(k.geometry.iloc[0])
nearest = gdf.loc[distances.nsmallest(10).index]

print("\nNearest districts by distance:")
print(nearest[["DISTRICT","ST_NM","censuscode"]])

# visualize
ax = gdf.plot(edgecolor="gray", figsize=(8,8))
k.plot(ax=ax)
nearest.plot(ax=ax)

plt.title("Kandhamal and nearest districts")
plt.show()

import geopandas as gpd
from libpysal.weights import Queen
import matplotlib.pyplot as plt

# -------------------------------------------------------
# Load shapefile
# -------------------------------------------------------
shapefile_path = r"D:\Urban_Spatial_Project\Data\Shapefiles\2011_Dist.shp"
gdf = gpd.read_file(shapefile_path)

# -------------------------------------------------------
# Build Queen contiguity weights
# -------------------------------------------------------
w = Queen.from_dataframe(gdf)

# -------------------------------------------------------
# Identify islands (districts with no neighbors)
# -------------------------------------------------------
island_indices = w.islands  # returns list of integer indices
islands = gdf.iloc[island_indices]

print("Spatial islands detected:")
print(islands[["censuscode","DISTRICT","ST_NM"]])

# -------------------------------------------------------
# Plot all districts and highlight islands
# -------------------------------------------------------
ax = gdf.plot(color="lightgray", edgecolor="black", figsize=(10,10))
if not islands.empty:
    islands.plot(ax=ax, color="red", edgecolor="black")

plt.title("Districts with zero neighbors (Spatial Islands)")
plt.show()



neighbors = w.neighbors[272]  # index of Kandhamal in gdf
print("Kandhamal neighbors indices:", neighbors)

# Kandhamal index in your gdf
k_index = gdf[gdf["DISTRICT"] == "Kandhamal"].index[0]

# List neighbors according to Queen weights
print("Kandhamal neighbors indices:", w.neighbors.get(k_index, []))

# List neighbor district names
neighbor_indices = w.neighbors.get(k_index, [])
if neighbor_indices:
    print(gdf.iloc[neighbor_indices][["DISTRICT","ST_NM","censuscode"]])
else:
    print("No neighbors detected by Queen contiguity.")