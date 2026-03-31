Urban Spatial Nighttime Lights Analysis
Overview
This project analyzes regional economic activity using nighttime light intensity data across Indian districts from 2013 to 2021. Nighttime lights are used as a proxy for economic activity, urbanization, and infrastructure development, allowing us to study spatial inequality and growth patterns.

Additionally, this project includes panel dataset creation, exploratory data analysis, and visualizations to track temporal trends in economic activity across districts.

Data Sources
District Shapefiles: 2011_Dist.shp – Geospatial boundaries of Indian districts.
Nighttime Light Rasters: Annual .tif satellite files for years 2013–2021.
Output CSVs:
district_nl_2013_2021_clean.csv – Cleaned district-level nighttime light averages.
nightlight_panel.csv – Panel-format dataset for longitudinal analysis.
Methodology
Shapefile Processing
Loaded Indian district shapefile using GeoPandas.
Removed islands and projected geometries to an equal-area CRS.
Calculated district area in square kilometers.
Nighttime Light Processing
Masked and cropped raster data to district boundaries using Rasterio.
Replaced negative or invalid raster values with NaN.
Computed district-level mean nightlight intensity for each year.
Data Cleaning & Panel Creation
Combined nighttime light values with district metadata.
Converted wide-format CSV to long panel format for temporal analysis.
Exploratory Analysis & Visualization
Example: Trend analysis of nightlight intensity for individual districts.
Visualized changes over time using Matplotlib and Seaborn.
Tools & Libraries
Python: Pandas, NumPy, GeoPandas, Rasterio, Matplotlib, Seaborn
Spatial Analysis: PySAL (Queen contiguity weights), raster masking, geospatial projections
Data Handling: CSV generation, panel dataset creation, NaN handling
