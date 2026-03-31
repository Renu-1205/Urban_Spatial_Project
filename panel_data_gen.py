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
# Remove Spatial Islands
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
# Extract Nightlight Values (SUM OF LIGHTS)
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

                # SUM of lights
                values.append(np.nansum(data))

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
# Load Dataset for Inspection
# -------------------------------------------------------

df = pd.read_csv(clean_csv)

print("\nFirst five rows:")
print(df.head())

print("\nMissing values by column:")
print(df.isna().sum())

df.fillna(0, inplace=True)


# -------------------------------------------------------
# Convert to Panel Dataset
# -------------------------------------------------------

print("Creating panel dataset...")

df_long = df.melt(
    id_vars=["DISTRICT", "ST_NM", "area_sqkm"],
    value_vars=[f"nl_{y}" for y in range(2013, 2022)],
    var_name="year",
    value_name="nightlight_sum",
)

df_long["year"] = df_long["year"].str.replace("nl_", "").astype(int)

# -------------------------------------------------------
# Create Log Variables
# -------------------------------------------------------

df_long["log_nightlight"] = np.log(df_long["nightlight_sum"] + 1)

# -------------------------------------------------------
# Save Panel Dataset
# -------------------------------------------------------

df_long.to_csv(panel_csv, index=False)

print("Panel dataset saved at:", panel_csv)

print("\nPanel dataset preview:")
print(df_long.head())
df.groupby("year").size()
df_long.head()
df_long.groupby("year").size()
nl_density = nightlight_sum / area_sqkm
df = pd.read_csv(r"D:\Urban_Spatial_Project\Data\nightlight_panel.csv")
df.columns
# create nightlight density
df["nl_density"] = df["nightlight_sum"] / df["area_sqkm"]

# log variables
import numpy as np

df["log_nightlight"] = np.log1p(df["nightlight_sum"])
df["log_nl_density"] = np.log1p(df["nl_density"])

# check
print(df.head())

# save
df.to_csv(panel_csv, index=False)

df_long = df.melt(
    id_vars=["censuscode", "DISTRICT", "ST_NM", "area_sqkm"],
    value_vars=[f"nl_{y}" for y in range(2013, 2022)],
    var_name="year",
    value_name="nightlight_sum"
)

df_long["year"] = df_long["year"].str.replace("nl_", "").astype(int)
(df["nl_density"] == 0).sum()
df["nl_density"] = df["nightlight_sum"] / df["area_sqkm"]
df["log_nl_density"] = np.log1p(df["nl_density"])
districts.columns

import pandas as pd
import numpy as np

# -------------------------------------------------------
# Paths
# -------------------------------------------------------

clean_csv = r"D:\Urban_Spatial_Project\Data\district_nl_2013_2021_clean.csv"
panel_csv = r"D:\Urban_Spatial_Project\Data\nightlight_panel.csv"

# -------------------------------------------------------
# Load district dataset (contains censuscode + nl_2013...nl_2021)
# -------------------------------------------------------

districts = pd.read_csv(clean_csv)

# -------------------------------------------------------
# Convert wide → panel
# -------------------------------------------------------

df_panel = districts.melt(
    id_vars=["censuscode","DISTRICT","ST_NM","area_sqkm"],
    value_vars=[f"nl_{y}" for y in range(2013, 2022)],
    var_name="year",
    value_name="nightlight_sum"
)

# extract numeric year
df_panel["year"] = df_panel["year"].str.replace("nl_","").astype(int)

# -------------------------------------------------------
# Create density variable
# -------------------------------------------------------

df_panel["nl_density"] = df_panel["nightlight_sum"] / df_panel["area_sqkm"]

# -------------------------------------------------------
# Create log variables
# -------------------------------------------------------

df_panel["log_nightlight"] = np.log1p(df_panel["nightlight_sum"])
df_panel["log_nl_density"] = np.log1p(df_panel["nl_density"])

# -------------------------------------------------------
# Sort panel by identifier
# -------------------------------------------------------

df_panel = df_panel.sort_values(["censuscode","year"])

# -------------------------------------------------------
# Save panel dataset
# -------------------------------------------------------

df_panel.to_csv(panel_csv, index=False)

print(df_panel.head())
print(df_panel.columns)
# remove districts without valid census code
df_panel = df_panel[df_panel["censuscode"] != 0]

# verify
print(df_panel.groupby("year").size())

# save again
df_panel.to_csv(panel_csv, index=False)
df_panel.describe()

df_panel.isna().sum()

df_panel.duplicated(["censuscode","year"]).sum()
df_panel = df_panel.sort_values(["censuscode","year"])

import pandas as pd

panel_path = r"D:\Urban_Spatial_Project\Data\nightlight_panel.csv"
df = pd.read_csv(panel_path)

df = df.sort_values(["censuscode","year"])
df.head()

import numpy as np

# overall variance
overall_var = df["log_nl_density"].var()

# between variance
between_var = df.groupby("censuscode")["log_nl_density"].mean().var()

# within variance
within_var = df.groupby("censuscode")["log_nl_density"].transform(lambda x: x - x.mean()).var()

print("Overall variance:", overall_var)
print("Between variance:", between_var)
print("Within variance:", within_var)

gdf = gdf[gdf["censuscode"].isin(df["censuscode"])]
print(len(gdf))
print(df["censuscode"].nunique())
from libpysal.weights import Queen

w = Queen.from_dataframe(gdf)
w.transform = "r"

print(w.n)      # number of districts
print(w.mean_neighbors)
print(w.islands)

import geopandas as gpd
from libpysal.weights import Queen
from esda.moran import Moran

shp_path = r"D:\Urban_Spatial_Project\Data\Shapefiles\2011_Dist.shp"

gdf = gpd.read_file(shp_path)

for yr in df["year"].unique():
    
    sub = df[df["year"] == yr]
    merged = gdf.merge(sub, on="censuscode")

    mi = Moran(merged["log_nl_density"], w)

    print(yr, mi.I, mi.p_sim)

    
for yr in sorted(df["year"].unique()):
    sub = df[df["year"] == yr]
    merged = gdf.merge(sub, on="censuscode")

    mi = Moran(merged["log_nl_density"], w)

    print(yr, round(mi.I,4), round(mi.p_sim,4))

from spreg import OLS
from libpysal.weights import lag_spatial

# ensure weights are row-standardized
w.transform = "r"

for yr in sorted(df_panel["year"].unique()):
    
    sub = df_panel[df_panel["year"] == yr]
    
    merged = gdf.merge(sub, on="censuscode")
    
    y = merged["log_nl_density"].values.reshape(-1,1)
    
    # constant-only model (diagnostics require an OLS base)
    X = np.ones((len(y),1))
    
    ols = OLS(y, X, w=w, spat_diag=True, name_y="log_nl_density")
    
    print("\nYear:", yr)
    print("LM Lag:", ols.lm_lag)
    print("LM Error:", ols.lm_error)
    print("Robust LM Lag:", ols.rlm_lag)
    print("Robust LM Error:", ols.rlm_error)


import pandas as pd

# Load nightlight panel
nl_panel = pd.read_csv(r"D:\Urban_Spatial_Project\Data\nightlight_panel.csv")

# Load additional regressors
regressors = pd.read_excel(r"D:\Urban_Spatial_Project\Data\More_regressors_file.xlsx")

# Optional: rename district_code to censuscode to match
regressors = regressors.rename(columns={"district_code": "censuscode"})

# Merge datasets on censuscode (and optionally state if needed)
merged_panel = nl_panel.merge(
    regressors,
    on="censuscode",
    how="left",   # keeps all nightlight districts even if some regressors missing
    validate="m:1" # each district in nl_panel matches one row in regressors
)

# Check result
print("Merged panel shape:", merged_panel.shape)
print(merged_panel.head())


# -----------------------------
# Inspect merged data
# -----------------------------
print("Merged panel shape:", merged_panel.shape)
print(merged_panel.head())

# -----------------------------
# Save merged panel
# -----------------------------
merged_panel.to_csv(r"D:\Urban_Spatial_Project\Data\nightlight_panel_merged.csv", index=False)
print("Merged panel saved successfully.")


import numpy as np
import pandas as pd
import geopandas as gpd
from libpysal.weights import Queen
from spreg import Panel_FE_Lag

# Load panel
merged_panel_path = r"D:\Urban_Spatial_Project\Data\nightlight_panel_merged.csv"
panel = pd.read_csv(merged_panel_path)
panel = panel.sort_values(["censuscode","year"])
panel["year"] = panel["year"].astype(int)
panel["censuscode"] = panel["censuscode"].astype(int)

# Load shapefile and weights
shapefile_path = r"D:\Urban_Spatial_Project\Data\Shapefiles\2011_Dist.shp"
gdf = gpd.read_file(shapefile_path)
gdf = gdf[gdf["censuscode"].isin(panel["censuscode"].unique())]

w = Queen.from_dataframe(gdf)
w.transform = "r"

# Dependent variable
y = panel["log_nl_density"].values.reshape(-1,1)

# Independent variables
X_vars = ["population","households","density","Literacy"]
X = panel[X_vars].values

# Create spatially lagged X for SDM by year
WX_list = []
for yr in sorted(panel["year"].unique()):
    X_year = panel.loc[panel["year"]==yr, X_vars].values
    WX_year = w.sparse.dot(X_year)
    WX_list.append(WX_year)

WX = np.vstack(WX_list)
X_sdm = np.hstack([X, WX])

# Run Spatial Durbin Panel (as SAR with X + WX)
model = Panel_FE_Lag(
    y=y,
    x=X_sdm,
    w=w,
    name_y="log_nl_density",
    name_x=X_vars + ["W_" + v for v in X_vars]
)

# Print results
print("Spatial Durbin Model (SDM) Results")
print("----------------------------------")


import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.stattools import durbin_watson
import numpy as np

# Load Stata file
data_path = r"D:\Urban_Spatial_Project\Data\log data.dta"
df = pd.read_stata(data_path)

# Select variables
y_var = 'log_nl_density'
X_vars = ['log_population', 'log_density', 'literacy']

# Check for NaN or infinite values
print(df[X_vars + [y_var]].isna().sum())        # missing values
print(np.isinf(df[X_vars + [y_var]]).sum())    # infinite values

# Drop rows with NaN or inf
df_clean = df.replace([np.inf, -np.inf], np.nan).dropna(subset=X_vars + [y_var])

# Prepare X and y
X = df_clean[X_vars]
X = sm.add_constant(X)
y = df_clean[y_var]

# Fit OLS with robust standard errors
model = sm.OLS(y, X).fit(cov_type='HC3')

# Print regression summary
print(model.summary())

# Durbin-Watson statistic
dw_stat = durbin_watson(model.resid)
print(f"Durbin-Watson statistic: {dw_stat:.4f}")


import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.stattools import durbin_watson

# 1. Load Stata file
data_path = r"D:\Urban_Spatial_Project\Data\log data.dta"
df = pd.read_stata(data_path)

# 2. Select variables for regression
y_var = 'log_nl_density'
X_vars = ['log_population', 'log_density', 'literacy']

# 3. Prepare X and y
X = df[X_vars]
X = sm.add_constant(X)  # add intercept
y = df[y_var]

# 4. Fit OLS regression
model = sm.OLS(y, X).fit(cov_type='HC3')  # robust SE

# 5. Print summary
print(model.summary())

# 6. Durbin-Watson statistic
dw_stat = durbin_watson(model.resid)
print(f"Durbin-Watson statistic: {dw_stat:.4f}")



import pandas as pd

# Load full panel
data_path = r"D:\Urban_Spatial_Project\Data\log data.dta"
df = pd.read_stata(data_path)

# Select relevant variables
vars_to_keep = ['censuscode', 'district', 'st_nm', 'log_nl_density', 'log_population', 
                'log_density', 'literacy', 'year']

df = df[vars_to_keep]

# Collapse to cross-section by averaging over years
df_cs = df.groupby(['censuscode', 'district', 'st_nm'], as_index=False).mean()




from spreg import ML_Lag, ML_Error, ML_LagDurbin

# Define dependent and independent variables
y = gdf['log_nl_density'].values.reshape(-1,1)
X = gdf[['log_population', 'log_density', 'literacy']].values

# SAR model (spatial lag)
sar = ML_Lag(y, X, w=w, name_y='log_nl_density', name_x=['log_population','log_density','literacy'])
print(sar.summary)

# SEM model (spatial error)
sem = ML_Error(y, X, w=w, name_y='log_nl_density', name_x=['log_population','log_density','literacy'])
print(sem.summary)

# SDM model (Spatial Durbin Model)
sdm = ML_LagDurbin(y, X, w=w, name_y='log_nl_density', name_x=['log_population','log_density','literacy'])
print(sdm.summary)


import numpy as np

# Drop NaNs in y or X
df_cs_clean = df_cs.dropna(subset=['log_nl_density', 'log_population', 'log_density', 'literacy'])

y = df_cs_clean['log_nl_density'].values.reshape(-1,1)
X = df_cs_clean[['log_population', 'log_density', 'literacy']].values


gdf_clean = gdf.merge(df_cs_clean[['censuscode']], on='censuscode', how='inner')
# Re-create spatial weights
from libpysal.weights import Queen
w = Queen.from_dataframe(gdf_clean)
w.transform = 'r'


from spreg import ML_Lag, ML_Error

# SAR
sar = ML_Lag(y, X, w=w, name_y='log_nl_density', name_x=['log_population','log_density','literacy'])
print(sar.summary)

# SEM
sem = ML_Error(y, X, w=w, name_y='log_nl_density', name_x=['log_population','log_density','literacy'])
print(sem.summary)

import rasterio
import matplotlib.pyplot as plt
from rasterio.windows import Window

path = r"D:\Urban_Spatial_Project\Data\Nightlights\VNL_v2_npp_2021_global_vcmslcfg_c202203152300.average_masked.tif"

with rasterio.open(path) as src:
    img = src.read(1, window=Window(0,0,2000,2000))   # small preview

plt.imshow(img)
plt.colorbar()
plt.show()


import rasterio
import matplotlib.pyplot as plt
import numpy as np
from rasterio.windows import Window

path = r"D:\Urban_Spatial_Project\Data\Nightlights\VNL_v2_npp_2021_global_vcmslcfg_c202203152300.average_masked.tif"

with rasterio.open(path) as src:
    img = src.read(1, window=Window(0,0,2000,2000))

# remove negative noise
img = np.where(img < 0, 0, img)

# percentile stretch
vmin, vmax = np.percentile(img, (2, 98))

plt.imshow(img, vmin=vmin, vmax=vmax, cmap="inferno")
plt.colorbar()
plt.show()






import pandas as pd
import matplotlib.pyplot as plt

# load data
path = r"D:\Urban_Spatial_Project\Data\nightlight_panel_merged.csv"
df = pd.read_csv(path)

# districts of interest
districts = ["Hisar", "Delhi", "Jhansi"]

df_sub = df[df["DISTRICT"].isin(districts)]

# choose variable for trend
var = "nl_density"     # alternative: nightlight_sum or log_nl_density

# plot
plt.figure(figsize=(8,5))

for d in districts:
    temp = df_sub[df_sub["DISTRICT"] == d]
    plt.plot(temp["year"], temp[var], marker="o", label=d)

plt.xlabel("Year")
plt.ylabel(var)
plt.title("Night Light Trend: Hisar vs Delhi vs Jhansi")
plt.legend()
plt.grid(True)

plt.show()


import pandas as pd

path = r"D:\Urban_Spatial_Project\Data\nightlight_panel_merged.csv"
df = pd.read_csv(path)

print(df[df["ST_NM"] == "Delhi"]["DISTRICT"].unique())



import pandas as pd
import matplotlib.pyplot as plt

path = r"D:\Urban_Spatial_Project\Data\nightlight_panel_merged.csv"
df = pd.read_csv(path)

plt.figure()

# Hisar
hisar = df[df["DISTRICT"] == "Hisar"]
plt.plot(hisar["year"], hisar["nl_density"], marker="o", label="Hisar")

# Jhansi
jhansi = df[df["DISTRICT"] == "Jhansi"]
plt.plot(jhansi["year"], jhansi["nl_density"], marker="o", label="Jhansi")

# Delhi (aggregate across districts in NCT of Delhi)
delhi = df[df["ST_NM"] == "NCT of Delhi"]
delhi_trend = delhi.groupby("year")["nl_density"].mean()

plt.plot(delhi_trend.index, delhi_trend.values, marker="o", label="Delhi")

plt.xlabel("Year")
plt.ylabel("Nightlight Density")
plt.title("Night Light Trend")
plt.legend()
plt.grid(True)

plt.show()


import pandas as pd
import matplotlib.pyplot as plt

path = r"D:\Urban_Spatial_Project\Data\nightlight_panel_merged.csv"
df = pd.read_csv(path)

plt.figure()

# Delhi (aggregate all districts in NCT of Delhi)
delhi = df[df["ST_NM"] == "NCT of Delhi"]
delhi_trend = delhi.groupby("year")["nl_density"].mean()

plt.plot(delhi_trend.index, delhi_trend.values, marker="o", label="Delhi")

# Mumbai (check correct district name)
mumbai = df[df["DISTRICT"].str.contains("Mumbai", case=False, na=False)]
mumbai_trend = mumbai.groupby("year")["nl_density"].mean()

plt.plot(mumbai_trend.index, mumbai_trend.values, marker="o", label="Mumbai")

plt.xlabel("Year")
plt.ylabel("Nightlight Density")
plt.title("Night Light Trend: Delhi vs Mumbai")
plt.legend()
plt.grid(True)

plt.show()
\


import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# load shapefile
districts = gpd.read_file(r"D:\Urban_Spatial_Project\Data\district_shapefile.shp")

# load nightlight data
df = pd.read_csv(r"D:\Urban_Spatial_Project\Data\nightlight_panel_merged.csv")

# select year
df2021 = df[df["year"]==2021]

# merge
gdf = districts.merge(df2021, left_on="DISTRICT", right_on="DISTRICT")

# plot
gdf.plot(column="nl_density", cmap="inferno", legend=True)

plt.title("Nightlight Density Map (2021)")
plt.show()


from libpysal.weights import Queen
from esda.moran import Moran
import splot.esda as esdaplot

# spatial weights
w = Queen.from_dataframe(gdf)
w.transform = "r"

# variable
y = gdf["nl_density"]

moran = Moran(y, w)

esdaplot.moran_scatterplot(moran)
plt.show()


from esda.moran import Moran_Local
import splot.esda as esdaplot

lisa = Moran_Local(y, w)

esdaplot.lisa_cluster(lisa, gdf)
plt.show()



import pandas as pd

# Load data
data_path = r"D:\Urban_Spatial_Project\Data\log data.dta"
df = pd.read_stata(data_path)

# Sort by nightlight density (highest first)
top5 = df.sort_values(by="nl_density", ascending=False)

# Select top 5 districts
top5_cities = top5[["district", "st_nm", "nl_density"]].head(5)

print(top5_cities)




import pandas as pd

# Load dataset
data_path = r"D:\Urban_Spatial_Project\Data\log data.dta"
df = pd.read_stata(data_path)

# Tier-1 districts
tier1_districts = [
    "Mumbai",
    "New Delhi",
    "Central",
    "Bengaluru Urban",
    "Chennai",
    "Hyderabad",
    "Kolkata",
    "Pune",
    "Ahmedabad"
]

# Filter districts
tier1_df = df[df["district"].isin(tier1_districts)]

# Ensure Delhi state name is correct
tier1_df = tier1_df[tier1_df["st_nm"].isin([
    "Maharashtra",
    "NCT of Delhi",
    "Karnataka",
    "Tamil Nadu",
    "Telangana",
    "West Bengal",
    "Gujarat"
])]

# Average nightlight density
tier1_nl = (
    tier1_df
    .groupby(["district", "st_nm"])["nl_density"]
    .mean()
    .reset_index()
)

# Sort highest to lowest
tier1_nl = tier1_nl.sort_values(by="nl_density", ascending=False)

print(tier1_nl)



import matplotlib.pyplot as plt

# Sort again to ensure correct order
tier1_nl = tier1_nl.sort_values(by="nl_density", ascending=False)

# Create bar graph
plt.figure()

plt.bar(tier1_nl["district"], tier1_nl["nl_density"])

plt.xlabel("City / District")
plt.ylabel("Nightlight Density")
plt.title("Night-Time Light Intensity Across Major Indian Cities")

plt.xticks(rotation=45)

plt.tight_layout()

plt.show()