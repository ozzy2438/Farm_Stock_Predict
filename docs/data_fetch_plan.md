# 📊 Data Fetch Plan - Agricultural Stock Risk Index

## Project Purpose

Build a U.S. Agricultural Stock Risk Prediction System (SRI Model) that identifies which crops and states are at higher risk of supply shortages in the upcoming season.

**Key Goals:**
- Predict potential yield drops
- Recommend where to increase stockpiles
- Help policymakers plan import/export adjustments
- Enable farmers to anticipate low-yield seasons

---

## 📋 Core Datasets Required

### 1. Crop Yield Data (Historical Production) ✅ COMPLETED
- **Source**: USDA NASS QuickStats API
- **Endpoint**: `https://quickstats.nass.usda.gov/api/`
- **Variables**: year, state_name, commodity_desc, Value (Yield or Production)
- **Range**: 2010–2024
- **Status**: ✅ Already implemented in `main.py`
- **Output**: `usda_crop_yield_2010_2024.csv`

---

### 2. Weather Data (Real) 🔄 IN PROGRESS
- **Source**: Visual Crossing Weather API
- **Endpoint**: `https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline`
- **Trial**: 14 days free, 1000 queries/day
- **Variables**:
  - Daily temperature (min, max, avg)
  - Precipitation (inches)
  - Growing Degree Days (GDD)
- **Aggregation**: Compute `avg_temp_f` and `total_precip_inches` per state/year
- **API Key**: Get from https://www.visualcrossing.com/sign-up
- **Script**: `fetch_weather_real.py`

**Sample Request:**
```bash
https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/Iowa/2020-01-01/2020-12-31?key=YOUR_API_KEY&include=days&elements=temp,precip
```

---

### 3. Drought Data (Real) 🔄 IN PROGRESS
- **Source**: U.S. Drought Monitor (USDM)
- **Data Portal**: https://droughtmonitor.unl.edu/DmData/DataDownload/DSCI.aspx
- **Variables**:
  - Weekly Drought Severity and Coverage Index (DSCI)
  - Percentage area in D0-D4 categories
- **Range**: 2010–2024
- **Download**: State-level CSV files (available for direct download)
- **Script**: `fetch_drought_real.py`

**Manual Download Option:**
1. Visit: https://droughtmonitor.unl.edu/DmData/DataDownload/ComprehensiveStatistics.aspx
2. Select: "State Statistics"
3. Date Range: 2010-01-01 to 2024-12-31
4. Format: CSV

---

### 4. Economic / Policy Data 🆕 NEW
- **Source**: USDA WASDE Reports (World Agricultural Supply and Demand Estimates)
- **URL**: https://www.usda.gov/oce/commodity/wasde
- **Variables**:
  - Monthly supply estimates
  - Demand projections
  - Ending stocks
  - Production forecasts
- **Use**: Capture market shocks and forecast revisions (ΔEnding Stocks)
- **Format**: PDF/Excel (monthly releases)
- **Script**: `fetch_policy_data.py`

**Available Data:**
- Production (million bushels)
- Total use (million bushels)
- Ending stocks (million bushels)
- Price forecasts ($/bushel)

---

### 5. Spatial Crop Distribution Data 🆕 NEW
- **Source**: CropGRIDS Dataset (Zenodo)
- **URL**: https://zenodo.org/record/4642545
- **Variables**: Crop-specific geographic grid values for 173 crops
- **Resolution**: 5 arc-minute (~10km)
- **Format**: NetCDF or GeoTIFF
- **Use**: Add spatial weights or heatmap layers (crop density per state)
- **Script**: `fetch_spatial_data.py`

**Download:**
```bash
# Direct download link (example)
wget https://zenodo.org/record/4642545/files/cropgrids_maize.nc
wget https://zenodo.org/record/4642545/files/cropgrids_wheat.nc
wget https://zenodo.org/record/4642545/files/cropgrids_soybeans.nc
```

---

## 🗂️ Final Merged Data Structure

After downloading and cleaning, merge all sources:

```csv
year | state_name | commodity | yield_value | avg_temp_f | total_precip_inches | drought_index | ending_stocks_change | crop_density
2010 | IOWA       | CORN      | 172.0       | 67.5       | 35.2                | 125.0         | 250                  | 0.85
2010 | ILLINOIS   | CORN      | 165.0       | 68.2       | 33.8                | 110.0         | 250                  | 0.82
...
```

---

## ⚙️ Implementation Plan

### Module Structure

```
/Farm_Stock_Predit/
├── data/                           # Raw data directory
│   ├── yield/
│   ├── weather/
│   ├── drought/
│   ├── policy/
│   └── spatial/
│
├── scripts/
│   ├── fetch_yield_data.py         ✅ Done (main.py)
│   ├── fetch_weather_real.py       🔄 To implement
│   ├── fetch_drought_real.py       🔄 To implement
│   ├── fetch_policy_data.py        🆕 To implement
│   ├── fetch_spatial_data.py       🆕 To implement
│   └── merge_all_datasets.py       🔄 To update
│
└── config/
    └── api_keys.env                # Store API keys securely
```

---

## 🔑 Required API Keys

Create a `.env` file:

```bash
# USDA QuickStats
USDA_API_KEY=2EEF90B1-825E-322B-8B27-098A9C92D575

# Visual Crossing Weather API
VISUAL_CROSSING_API_KEY=YOUR_KEY_HERE
# Get from: https://www.visualcrossing.com/sign-up

# Optional: Weatherbit (if needed)
WEATHERBIT_API_KEY=YOUR_KEY_HERE
# Get from: https://www.weatherbit.io/account/create
```

---

## 📝 Implementation Steps

### Step 1: Visual Crossing Weather API
```python
# fetch_weather_real.py
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('VISUAL_CROSSING_API_KEY')

states = ['Iowa', 'Illinois', 'Nebraska', ...]
years = range(2010, 2025)

for state in states:
    for year in years:
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{state}/{year}-01-01/{year}-12-31"
        params = {
            'key': API_KEY,
            'include': 'days',
            'elements': 'temp,precip,tempmax,tempmin'
        }
        # Fetch and aggregate...
```

### Step 2: US Drought Monitor
```python
# fetch_drought_real.py
# Option 1: Direct CSV download
url = "https://droughtmonitor.unl.edu/data/csv/dsci.csv"
# Option 2: Use their API/web scraping
```

### Step 3: USDA WASDE
```python
# fetch_policy_data.py
# Parse monthly PDF reports or Excel files
# Extract ending stocks, production estimates
```

### Step 4: CropGRIDS
```python
# fetch_spatial_data.py
# Download NetCDF files from Zenodo
# Aggregate by US state boundaries
```

---

## 🎯 Next Actions

1. **Get API Keys**
   - [ ] Visual Crossing Weather API
   - [ ] Optional: Weatherbit API

2. **Implement Real Data Fetchers**
   - [ ] `fetch_weather_real.py`
   - [ ] `fetch_drought_real.py`
   - [ ] `fetch_policy_data.py`
   - [ ] `fetch_spatial_data.py`

3. **Update Pipeline**
   - [ ] Modify `merge_datasets.py` for new columns
   - [ ] Update `sri_model.py` with additional features
   - [ ] Re-run validation with real data

4. **Enhance Model**
   - [ ] Add economic indicators (ending stocks)
   - [ ] Include spatial crop density weights
   - [ ] Improve predictive accuracy

---

## 📚 Resources

- **USDA QuickStats**: https://quickstats.nass.usda.gov/
- **Visual Crossing**: https://www.visualcrossing.com/weather-api
- **US Drought Monitor**: https://droughtmonitor.unl.edu/
- **USDA WASDE**: https://www.usda.gov/oce/commodity/wasde
- **CropGRIDS**: https://zenodo.org/record/4642545

---

**Ready to start?** Let's implement the real data fetchers one by one! 🚀
