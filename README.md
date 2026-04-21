# Urban Spatial Nighttime Lights Analysis

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Geospatial](https://img.shields.io/badge/Geospatial-Analysis-orange.svg)](https://geopandas.org/)

## Overview

This project analyzes regional economic activity using nighttime light intensity data across Indian districts from **2013 to 2021**. Nighttime lights serve as a powerful proxy for economic activity, urbanization, and infrastructure development, enabling the study of spatial inequality and growth patterns across India's administrative districts.

The analysis includes panel dataset creation, exploratory data analysis (EDA), and comprehensive visualizations to track temporal trends in economic activity across districts.

## Key Features

- **Multi-year Analysis**: Process 9 years of satellite nighttime light data (2013-2021)
- **Spatial Processing**: Handle complex geospatial operations with Indian district boundaries
- **Panel Dataset**: Generate ready-to-use panel data for longitudinal analysis
- **Visual Analytics**: Create time-series visualizations of economic activity trends
- **Spatial Inequality**: Identify patterns of regional development disparities

## Data Sources

| Data Type | File Name | Description |
|-----------|-----------|-------------|
| Shapefile | `2011_Dist.shp` | Geospatial boundaries of Indian districts |
| Raster Data | `*.tif` (2013-2021) | Annual nighttime light satellite imagery |
| Output Data | `district_nl_2013_2021_clean.csv` | Cleaned district-level light intensity averages |
| Output Data | `nightlight_panel.csv` | Panel-format dataset for longitudinal analysis |

## Methodology

### 1. Shapefile Processing
- Load Indian district boundaries using GeoPandas
- Remove island territories for focused mainland analysis
- Project geometries to equal-area CRS (EPSG:7755)
- Calculate district areas in square kilometers

### 2. Nighttime Light Processing
- Mask and crop raster data to district boundaries using Rasterio
- Replace negative/invalid raster values (e.g., -9999) with NaN
- Compute district-level mean nightlight intensity per year
- Handle missing data and edge cases

### 3. Data Cleaning & Panel Creation
- Merge nighttime light values with district metadata (names, codes, areas)
- Transform wide-format data to long panel format
- Create balanced/unbalanced panel for econometric analysis

### 4. Exploratory Analysis & Visualization
- Trend analysis of nightlight intensity for individual districts
- Regional comparisons and growth trajectory mapping
- Time-series visualization using Matplotlib and Seaborn
- Spatial autocorrelation analysis (optional)

## Installation

### Prerequisites
- Python 3.8 or higher
- GDAL/Fiona (required for GeoPandas)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/urban-spatial-nighttime-lights.git
cd urban-spatial-nighttime-lights

# Install dependencies
pip install -r requirements.txt

# Or install with conda (recommended for geospatial packages)
conda env create -f environment.yml
conda activate nightlight-analysis
