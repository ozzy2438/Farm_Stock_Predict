# 📊 Power BI Dashboard Structure - Agricultural Stock Risk Intelligence System

## 🎯 **Dashboard Overview**

**Purpose**: Interactive executive dashboard for agricultural supply chain risk monitoring and decision-making support.

**Target Audience**: C-Level executives, supply chain managers, procurement teams, risk analysts, agricultural specialists.

**Update Frequency**: Annual (October 1st) with year-over-year comparison capabilities.

---

## 📂 **Data Sources & File Structure**

### **Primary Data Files to Import**

| File Name | Purpose | Key Columns | Records |
|-----------|---------|-------------|---------|
| **`sri_results_2025.csv`** | Main dataset - SRI scores & risk analysis | year, state_name, commodity, SRI, risk_category, yield_per_acre, yield_risk, weather_risk, drought_risk, economic_risk, recommendation, avg_temp, total_precip, avg_dsci | 380 rows |
| **`sri_results_2024.csv`** | Previous year comparison | (same structure as 2025) | ~380 rows |
| **`sri_results_2023.csv`** | Historical trend data | (same structure) | ~380 rows |
| **`state_mapping.csv`** | Geographic reference table | state_name, state_code, region, division, lat, lon | 50 rows |
| **`commodity_reference.csv`** | Crop metadata | commodity, category, unit, crop_season, icon | 3 rows |
| **`risk_thresholds.csv`** | Risk categorization rules | risk_level, min_sri, max_sri, color_hex, recommendation_template | 4 rows |

### **How to Prepare Data Files**

**Step 1: Export from Pipeline**
```bash
# Main SRI results (already generated)
/Users/osmanorka/Farm_Stock_Predit/sri_results_2025.csv

# Copy to Power BI data folder
mkdir -p /Users/osmanorka/Farm_Stock_Predit/powerbi_data
cp sri_results_2025.csv powerbi_data/
```

**Step 2: Create Supporting Reference Tables**

Create **`state_mapping.csv`**:
```csv
state_name,state_code,region,division,lat,lon
ALABAMA,AL,South,East South Central,32.806671,-86.791130
ALASKA,AK,West,Pacific,61.370716,-152.404419
ARIZONA,AZ,West,Mountain,33.729759,-111.431221
CALIFORNIA,CA,West,Pacific,36.116203,-119.681564
COLORADO,CO,West,Mountain,39.059811,-105.311104
FLORIDA,FL,South,South Atlantic,27.766279,-81.686783
GEORGIA,GA,South,South Atlantic,33.040619,-83.643074
IDAHO,ID,West,Mountain,44.240459,-114.478828
ILLINOIS,IL,Midwest,East North Central,40.349457,-88.986137
INDIANA,IN,Midwest,East North Central,39.849426,-86.258278
IOWA,IA,Midwest,West North Central,42.011539,-93.210526
KANSAS,KS,Midwest,West North Central,38.526600,-96.726486
KENTUCKY,KY,South,East South Central,37.668140,-84.670067
LOUISIANA,LA,South,West South Central,31.169546,-91.867805
MICHIGAN,MI,Midwest,East North Central,43.326618,-84.536095
MINNESOTA,MN,Midwest,West North Central,45.694454,-93.900192
MISSISSIPPI,MS,South,East South Central,32.741646,-89.678696
MISSOURI,MO,Midwest,West North Central,38.456085,-92.288368
MONTANA,MT,West,Mountain,46.921925,-110.454353
NEBRASKA,NE,Midwest,West North Central,41.125370,-98.268082
NEW JERSEY,NJ,Northeast,Middle Atlantic,40.298904,-74.521011
NEW MEXICO,NM,West,Mountain,34.840515,-106.248482
NEW YORK,NY,Northeast,Middle Atlantic,42.165726,-74.948051
NORTH CAROLINA,NC,South,South Atlantic,35.630066,-79.806419
NORTH DAKOTA,ND,Midwest,West North Central,47.528912,-99.784012
OHIO,OH,Midwest,East North Central,40.388783,-82.764915
OKLAHOMA,OK,South,West South Central,35.565342,-96.928917
SOUTH CAROLINA,SC,South,South Atlantic,33.856892,-80.945007
SOUTH DAKOTA,SD,Midwest,West North Central,44.299782,-99.438828
TEXAS,TX,South,West South Central,31.054487,-97.563461
UTAH,UT,West,Mountain,40.150032,-111.862434
WASHINGTON,WA,West,Pacific,47.400902,-121.490494
WISCONSIN,WI,Midwest,East North Central,44.268543,-89.616508
WYOMING,WY,West,Mountain,42.755966,-107.302490
```

Create **`commodity_reference.csv`**:
```csv
commodity,category,unit,crop_season,icon
CORN,Grain,Bushels,Summer,🌽
SOYBEANS,Oilseed,Bushels,Fall,🫘
WHEAT,Grain,Bushels,Spring/Winter,🌾
```

Create **`risk_thresholds.csv`**:
```csv
risk_level,min_sri,max_sri,color_hex,recommendation_template
Low,0,25,#388e3c,Normal inventory levels
Moderate,25,50,#fbc02d,Monitor closely and consider +5-10% stockpile increase
High,50,75,#f57c00,Increase stockpile by +15-20%
Very High,75,100,#d32f2f,CRITICAL: Increase stockpile by +25% immediately
```

---

## 🔗 **Data Model & Relationships**

### **Star Schema Design**

```
Fact Table (Center):
┌─────────────────────────────┐
│   FactSRI                   │
│  (sri_results_2025.csv)     │
├─────────────────────────────┤
│ SRI_ID (generated)          │ ← Primary Key
│ year                        │
│ state_name                  │ → FK to DimStates
│ commodity                   │ → FK to DimCommodities
│ SRI                         │ ← Main Metric
│ risk_category               │
│ yield_per_acre              │
│ yield_risk                  │
│ weather_risk                │
│ drought_risk                │
│ economic_risk               │
│ recommendation              │
│ avg_temp                    │
│ total_precip                │
│ avg_dsci                    │
└─────────────────────────────┘

Dimension Tables (Surrounding):

┌─────────────────────┐         ┌─────────────────────┐
│   DimStates         │         │  DimCommodities     │
│ (state_mapping)     │         │ (commodity_ref)     │
├─────────────────────┤         ├─────────────────────┤
│ state_name (PK)     │         │ commodity (PK)      │
│ state_code          │         │ category            │
│ region              │         │ unit                │
│ division            │         │ crop_season         │
│ lat                 │         │ icon                │
│ lon                 │         └─────────────────────┘
└─────────────────────┘

┌─────────────────────┐         ┌─────────────────────┐
│  DimRiskLevels      │         │   DimCalendar       │
│ (risk_thresholds)   │         │  (date table)       │
├─────────────────────┤         ├─────────────────────┤
│ risk_level (PK)     │         │ date (PK)           │
│ min_sri             │         │ year                │
│ max_sri             │         │ month               │
│ color_hex           │         │ quarter             │
│ recommendation      │         │ fiscal_year         │
└─────────────────────┘         └─────────────────────┘
```

### **Relationship Configuration in Power BI**

1. **FactSRI → DimStates**
   - Relationship: `FactSRI[state_name]` → `DimStates[state_name]`
   - Cardinality: Many to One (*)
   - Cross-filter direction: Single

2. **FactSRI → DimCommodities**
   - Relationship: `FactSRI[commodity]` → `DimCommodities[commodity]`
   - Cardinality: Many to One (*)
   - Cross-filter direction: Single

3. **FactSRI → DimCalendar**
   - Relationship: `FactSRI[year]` → `DimCalendar[year]`
   - Cardinality: Many to One (*)
   - Cross-filter direction: Both (for year slicing)

4. **DimRiskLevels → FactSRI**
   - Relationship: Use DAX instead of direct relationship (dynamic threshold matching)

---

## 📐 **DAX Measures & Calculated Columns**

### **Essential Measures**

```dax
/* ============================================================================
   KEY PERFORMANCE INDICATORS (KPIs)
   ============================================================================ */

// 1. National Average SRI
National_Avg_SRI = AVERAGE(FactSRI[SRI])

// 2. Total State-Commodity Combinations
Total_Records = COUNTROWS(FactSRI)

// 3. High Risk State Count
High_Risk_States =
CALCULATE(
    DISTINCTCOUNT(FactSRI[state_name]),
    FactSRI[SRI] >= 50
)

// 4. Critical Alert Count
Critical_Alerts =
CALCULATE(
    COUNTROWS(FactSRI),
    FactSRI[SRI] >= 75
)

// 5. States Analyzed
Total_States = DISTINCTCOUNT(FactSRI[state_name])

// 6. Commodities Tracked
Total_Commodities = DISTINCTCOUNT(FactSRI[commodity])


/* ============================================================================
   YEAR-OVER-YEAR COMPARISONS
   ============================================================================ */

// 7. Previous Year Average SRI
Previous_Year_SRI =
CALCULATE(
    [National_Avg_SRI],
    PREVIOUSYEAR(DimCalendar[Date])
)

// 8. YoY Change in SRI
YoY_SRI_Change = [National_Avg_SRI] - [Previous_Year_SRI]

// 9. YoY Change Percentage
YoY_SRI_Change_Pct =
DIVIDE(
    [YoY_SRI_Change],
    [Previous_Year_SRI],
    0
)

// 10. Trend Indicator (Arrow)
Trend_Arrow =
SWITCH(
    TRUE(),
    [YoY_SRI_Change] < -5, "▼▼ Significant Improvement",
    [YoY_SRI_Change] < 0, "▼ Improvement",
    [YoY_SRI_Change] = 0, "― Stable",
    [YoY_SRI_Change] < 5, "▲ Slight Increase",
    "▲▲ Significant Increase"
)


/* ============================================================================
   RISK DISTRIBUTION METRICS
   ============================================================================ */

// 11. Low Risk Count
Low_Risk_Count =
CALCULATE(
    COUNTROWS(FactSRI),
    FactSRI[risk_category] = "Low"
)

// 12. Moderate Risk Count
Moderate_Risk_Count =
CALCULATE(
    COUNTROWS(FactSRI),
    FactSRI[risk_category] = "Moderate"
)

// 13. High Risk Count
High_Risk_Count =
CALCULATE(
    COUNTROWS(FactSRI),
    FactSRI[risk_category] = "High"
)

// 14. Very High Risk Count
Very_High_Risk_Count =
CALCULATE(
    COUNTROWS(FactSRI),
    FactSRI[risk_category] = "Very High"
)

// 15. Risk Distribution % (for specific category)
Risk_Distribution_Pct =
DIVIDE(
    COUNTROWS(FactSRI),
    CALCULATE(COUNTROWS(FactSRI), ALL(FactSRI[risk_category])),
    0
)


/* ============================================================================
   COMPONENT ANALYSIS
   ============================================================================ */

// 16. Average Yield Risk
Avg_Yield_Risk = AVERAGE(FactSRI[yield_risk])

// 17. Average Weather Risk
Avg_Weather_Risk = AVERAGE(FactSRI[weather_risk])

// 18. Average Drought Risk
Avg_Drought_Risk = AVERAGE(FactSRI[drought_risk])

// 19. Average Economic Risk
Avg_Economic_Risk = AVERAGE(FactSRI[economic_risk])

// 20. Weighted Component Contribution (Yield)
Yield_Contribution = [Avg_Yield_Risk] * 0.35

// 21. Weighted Component Contribution (Weather)
Weather_Contribution = [Avg_Weather_Risk] * 0.25

// 22. Weighted Component Contribution (Drought)
Drought_Contribution = [Avg_Drought_Risk] * 0.25

// 23. Weighted Component Contribution (Economic)
Economic_Contribution = [Avg_Economic_Risk] * 0.15


/* ============================================================================
   RANKING & TOP N ANALYTICS
   ============================================================================ */

// 24. State Risk Ranking
State_Risk_Rank =
RANKX(
    ALL(FactSRI[state_name]),
    [National_Avg_SRI],
    ,
    DESC,
    DENSE
)

// 25. Is Top 10 High Risk State
Is_Top10_Risk = IF([State_Risk_Rank] <= 10, "Yes", "No")

// 26. Commodity Average SRI
Commodity_Avg_SRI =
CALCULATE(
    AVERAGE(FactSRI[SRI]),
    ALLEXCEPT(FactSRI, FactSRI[commodity])
)


/* ============================================================================
   CONDITIONAL FORMATTING HELPERS
   ============================================================================ */

// 27. SRI Color Code (for conditional formatting)
SRI_Color =
SWITCH(
    TRUE(),
    [National_Avg_SRI] < 25, "#388e3c",      // Green
    [National_Avg_SRI] < 50, "#fbc02d",      // Yellow
    [National_Avg_SRI] < 75, "#f57c00",      // Orange
    "#d32f2f"                                 // Red
)

// 28. Risk Level Text
Risk_Level_Text =
SWITCH(
    TRUE(),
    [National_Avg_SRI] < 25, "Low Risk",
    [National_Avg_SRI] < 50, "Moderate Risk",
    [National_Avg_SRI] < 75, "High Risk",
    "Very High Risk"
)

// 29. Strategic Recommendation
Strategic_Recommendation =
SWITCH(
    TRUE(),
    [National_Avg_SRI] < 25, "Maintain standard inventory levels",
    [National_Avg_SRI] < 35, "Monitor closely, consider +5% stockpile increase",
    [National_Avg_SRI] < 50, "Increase stockpile by +10-15%",
    [National_Avg_SRI] < 75, "Increase stockpile by +15-20%",
    "CRITICAL: Increase stockpile by +25% immediately"
)


/* ============================================================================
   GEOGRAPHIC ANALYTICS
   ============================================================================ */

// 30. Regional Average SRI
Regional_Avg_SRI =
CALCULATE(
    AVERAGE(FactSRI[SRI]),
    ALLEXCEPT(DimStates, DimStates[region])
)

// 31. States Above National Average
States_Above_Avg =
CALCULATE(
    DISTINCTCOUNT(FactSRI[state_name]),
    FactSRI[SRI] > [National_Avg_SRI]
)


/* ============================================================================
   TIME INTELLIGENCE
   ============================================================================ */

// 32. Multi-Year Average SRI
Multi_Year_Avg_SRI =
CALCULATE(
    AVERAGE(FactSRI[SRI]),
    DATESBETWEEN(
        DimCalendar[Date],
        DATE(YEAR(TODAY())-3, 1, 1),
        DATE(YEAR(TODAY()), 12, 31)
    )
)

// 33. Best Year SRI
Best_Year_SRI =
MINX(
    VALUES(FactSRI[year]),
    [National_Avg_SRI]
)

// 34. Worst Year SRI
Worst_Year_SRI =
MAXX(
    VALUES(FactSRI[year]),
    [National_Avg_SRI]
)
```

### **Calculated Columns**

```dax
/* ============================================================================
   CALCULATED COLUMNS (Add to FactSRI table)
   ============================================================================ */

// 1. SRI Risk Band (for grouping)
SRI_Band =
SWITCH(
    TRUE(),
    FactSRI[SRI] < 25, "0-25: Low",
    FactSRI[SRI] < 50, "25-50: Moderate",
    FactSRI[SRI] < 75, "50-75: High",
    "75-100: Very High"
)

// 2. Dominant Risk Factor (which component contributes most)
Dominant_Risk_Factor =
VAR YieldWeighted = FactSRI[yield_risk] * 0.35
VAR WeatherWeighted = FactSRI[weather_risk] * 0.25
VAR DroughtWeighted = FactSRI[drought_risk] * 0.25
VAR EconomicWeighted = FactSRI[economic_risk] * 0.15
RETURN
SWITCH(
    TRUE(),
    YieldWeighted = MAX(YieldWeighted, WeatherWeighted, DroughtWeighted, EconomicWeighted), "Yield",
    WeatherWeighted = MAX(YieldWeighted, WeatherWeighted, DroughtWeighted, EconomicWeighted), "Weather",
    DroughtWeighted = MAX(YieldWeighted, WeatherWeighted, DroughtWeighted, EconomicWeighted), "Drought",
    "Economic"
)

// 3. Year-Over-Year SRI Change (requires historical data)
YoY_SRI_Diff =
VAR CurrentYear = FactSRI[year]
VAR CurrentState = FactSRI[state_name]
VAR CurrentCommodity = FactSRI[commodity]
VAR PreviousYearSRI =
    CALCULATE(
        MAX(FactSRI[SRI]),
        FactSRI[year] = CurrentYear - 1,
        FactSRI[state_name] = CurrentState,
        FactSRI[commodity] = CurrentCommodity
    )
RETURN
FactSRI[SRI] - PreviousYearSRI

// 4. Procurement Priority Score (1-100, higher = more urgent)
Procurement_Priority =
(FactSRI[SRI] * 0.7) +
(RANKX(ALL(FactSRI), FactSRI[SRI], , DESC) * 0.3)

// 5. Temperature Risk Flag
Temp_Risk_Flag =
IF(
    FactSRI[avg_temp] > 85 || FactSRI[avg_temp] < 40,
    "⚠️ Temperature Stress",
    "✓ Normal"
)

// 6. Drought Alert Flag
Drought_Alert =
SWITCH(
    TRUE(),
    FactSRI[avg_dsci] >= 75, "🔴 Severe Drought",
    FactSRI[avg_dsci] >= 50, "🟠 Moderate Drought",
    FactSRI[avg_dsci] >= 25, "🟡 Mild Drought",
    "🟢 No Drought"
)
```

---

## 📄 **Dashboard Page Structure** (6 Pages)

### **Page 1: Executive Summary Dashboard** 📊

**Purpose**: High-level KPIs and national overview for C-level executives.

**Layout**: 1920 x 1080 (16:9 aspect ratio)

#### **Visual Elements**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AGRICULTURAL STOCK RISK INTELLIGENCE                  │
│                           Executive Dashboard 2025                       │
├───────────────┬───────────────┬───────────────┬─────────────────────────┤
│  CARD 1       │  CARD 2       │  CARD 3       │  CARD 4                 │
│               │               │               │                         │
│  Nat'l Avg    │  High-Risk    │  States       │  Critical               │
│  SRI          │  States       │  Analyzed     │  Alerts                 │
│               │               │               │                         │
│    23.7       │      0        │     50        │      0                  │
│               │               │               │                         │
│  ▼ -5.2 YoY   │  ▼ -3 YoY     │  ― Same       │  ▼ -15 YoY              │
├───────────────┴───────────────┴───────────────┴─────────────────────────┤
│                                                                          │
│  DONUT CHART: Risk Distribution                                         │
│  ┌──────────────────────────────────────────────────┐                   │
│  │         60% Low Risk (227 records)               │                   │
│  │         40% Moderate Risk (153 records)          │                   │
│  │         0% High Risk                             │                   │
│  │         0% Very High Risk                        │                   │
│  └──────────────────────────────────────────────────┘                   │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  LINE CHART: 3-Year SRI Trend                                           │
│  ┌──────────────────────────────────────────────────┐                   │
│  │  SRI                                             │                   │
│  │  40 ┤                                            │                   │
│  │  35 ┤     ●                                      │                   │
│  │  30 ┤    ╱                                       │                   │
│  │  25 ┤   ╱  ●                                     │                   │
│  │  20 ┤  ●    ╲                                    │                   │
│  │  15 ┤        ●───────●                           │                   │
│  │     └─────────────────────────────────           │                   │
│  │      2021  2022  2023  2024  2025               │                   │
│  └──────────────────────────────────────────────────┘                   │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│  CLUSTERED BAR CHART: Risk Component Breakdown                          │
│  ┌──────────────────────────────────────────────────┐                   │
│  │  Yield Risk        ████████████████ 17.7         │                   │
│  │  Weather Risk      ███ 4.0                       │                   │
│  │  Drought Risk      ▏0.0                          │                   │
│  │  Economic Risk     ██████████████████ 35.0       │                   │
│  └──────────────────────────────────────────────────┘                   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

**Specific Visual Configurations**:

1. **Card Visual #1: National Average SRI**
   - **Data Field**: `[National_Avg_SRI]`
   - **Conditional Formatting**: Text color based on `[SRI_Color]`
   - **Trend Indicator**: Show `[YoY_SRI_Change]` with ▲▼ arrows
   - **Size**: 300x200 px

2. **Card Visual #2: High-Risk States**
   - **Data Field**: `[High_Risk_States]`
   - **Conditional Formatting**: Red if > 5, Yellow if 1-5, Green if 0
   - **Trend Indicator**: `[High_Risk_States] - [Previous_Year_High_Risk]`
   - **Size**: 300x200 px

3. **Card Visual #3: States Analyzed**
   - **Data Field**: `[Total_States]`
   - **Static Value**: Always 50 (or DISTINCTCOUNT)
   - **Size**: 300x200 px

4. **Card Visual #4: Critical Alerts**
   - **Data Field**: `[Critical_Alerts]`
   - **Conditional Formatting**: Blink/pulse if > 0
   - **Size**: 300x200 px

5. **Donut Chart: Risk Distribution**
   - **Legend**: `FactSRI[risk_category]`
   - **Values**: `[Total_Records]`
   - **Colors**:
     - Low = #388e3c (Green)
     - Moderate = #fbc02d (Yellow)
     - High = #f57c00 (Orange)
     - Very High = #d32f2f (Red)
   - **Data Labels**: Show percentage and count
   - **Center Label**: "Total: 380"
   - **Size**: 400x400 px

6. **Line Chart: 3-Year SRI Trend**
   - **X-Axis**: `FactSRI[year]`
   - **Y-Axis**: `[National_Avg_SRI]`
   - **Line Color**: #2c5f2d (dark green)
   - **Data Points**: Show markers
   - **Tooltip**: Show year, SRI, YoY change
   - **Reference Line**: Add horizontal line at 25 (Low/Moderate threshold)
   - **Size**: 800x300 px

7. **Clustered Bar Chart: Risk Component Breakdown**
   - **Y-Axis**: Component names (Yield, Weather, Drought, Economic)
   - **X-Axis**: Average risk scores
   - **Values**:
     - `[Avg_Yield_Risk]`
     - `[Avg_Weather_Risk]`
     - `[Avg_Drought_Risk]`
     - `[Avg_Economic_Risk]`
   - **Data Labels**: Show values
   - **Colors**: Color-code by component
   - **Size**: 800x300 px

8. **Slicer: Year Filter**
   - **Field**: `FactSRI[year]`
   - **Style**: Dropdown or horizontal buttons
   - **Default**: Most recent year (2025)
   - **Position**: Top right corner

---

### **Page 2: Geographic Risk Map** 🗺️

**Purpose**: Interactive map showing risk levels by state with drill-down capabilities.

#### **Visual Elements**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GEOGRAPHIC RISK HEATMAP                          │
│                              United States                               │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  FILLED MAP (Choropleth)                                                │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                                                                  │   │
│  │         [Interactive US Map with color-coded states]            │   │
│  │                                                                  │   │
│  │   Legend:                                                        │   │
│  │   🟢 Low Risk (0-25)                                             │   │
│  │   🟡 Moderate Risk (25-50)                                       │   │
│  │   🟠 High Risk (50-75)                                           │   │
│  │   🔴 Very High Risk (75-100)                                     │   │
│  │                                                                  │   │
│  │   Click state for details →                                     │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
├────────────────────────────────┬─────────────────────────────────────────┤
│  TABLE: Top 15 Risk States     │  CLUSTERED COLUMN: Regional Breakdown   │
│  ┌─────────────────────────┐   │  ┌──────────────────────────────────┐  │
│  │ Rank │ State    │ SRI    │   │  │  SRI                             │  │
│  │  1   │ Texas    │ 36.2   │   │  │  40 ┤                            │  │
│  │  2   │ Wyoming  │ 35.6   │   │  │  30 ┤  ████                      │  │
│  │  3   │ New Mex. │ 35.2   │   │  │  20 ┤  ████  ████  ████  ████    │  │
│  │  4   │ Oklahoma │ 34.6   │   │  │  10 ┤  ████  ████  ████  ████    │  │
│  │  5   │ Colorado │ 34.0   │   │  │     └───────────────────────────  │  │
│  │  ... │ ...      │ ...    │   │  │      West  South Midwest Northeast│  │
│  └─────────────────────────┘   │  └──────────────────────────────────┘  │
│                                │                                        │
└────────────────────────────────┴─────────────────────────────────────────┘
```

**Specific Visual Configurations**:

1. **Filled Map (Choropleth)**
   - **Location**: `DimStates[state_name]`
   - **Value (Color Saturation)**: `FactSRI[SRI]` averaged by state
   - **Color Scale**:
     - Minimum (0): #388e3c (Green)
     - Mid-point (50): #fbc02d (Yellow)
     - Maximum (100): #d32f2f (Red)
   - **Tooltip**:
     - State name
     - Average SRI
     - Risk category
     - Commodities tracked
     - Top risk commodity
   - **Zoom**: Enable map zoom/pan
   - **Size**: 1200x700 px

2. **Table: Top 15 Risk States**
   - **Columns**:
     - Rank: `[State_Risk_Rank]`
     - State: `FactSRI[state_name]`
     - Avg SRI: `[National_Avg_SRI]` (by state)
     - Risk Level: `FactSRI[risk_category]`
     - Primary Commodity: `FactSRI[commodity]` (mode)
   - **Sorting**: By SRI descending
   - **Conditional Formatting**: Color-code SRI column
   - **Top N Filter**: Show only top 15
   - **Size**: 400x700 px

3. **Clustered Column Chart: Regional Breakdown**
   - **X-Axis**: `DimStates[region]` (West, South, Midwest, Northeast)
   - **Y-Axis**: `[Regional_Avg_SRI]`
   - **Color**: By region
   - **Data Labels**: Show values
   - **Reference Line**: National average (23.7)
   - **Size**: 600x400 px

4. **Slicer: Commodity Filter**
   - **Field**: `FactSRI[commodity]`
   - **Style**: Tile (visual buttons with icons 🌽 🫘 🌾)
   - **Multi-select**: Enabled
   - **Position**: Top left

5. **Slicer: Risk Category Filter**
   - **Field**: `FactSRI[risk_category]`
   - **Style**: List with checkboxes
   - **Position**: Right sidebar

---

### **Page 3: Commodity Analysis** 🌽

**Purpose**: Deep dive into individual crop types and their risk profiles.

#### **Visual Elements**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          COMMODITY RISK ANALYSIS                         │
├──────────────────────────────────────────────────────────────────────────┤
│  TILE SLICER: Select Commodity                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                                 │
│  │  🌽     │  │  🫘     │  │  🌾     │                                 │
│  │  CORN   │  │SOYBEANS │  │  WHEAT  │                                 │
│  └─────────┘  └─────────┘  └─────────┘                                 │
├──────────────────────────────────────────────────────────────────────────┤
│  MULTI-ROW CARD: Commodity Stats                                        │
│  ┌────────────────┬────────────────┬────────────────┬─────────────────┐ │
│  │ Avg SRI        │ States Grown   │ Min SRI        │ Max SRI         │ │
│  │   23.8         │      93        │    9.3         │   41.2          │ │
│  └────────────────┴────────────────┴────────────────┴─────────────────┘ │
├───────────────────────────────────┬──────────────────────────────────────┤
│  BOX & WHISKER PLOT               │  SCATTER PLOT: Yield vs SRI         │
│  ┌────────────────────────────┐   │  ┌───────────────────────────────┐  │
│  │  SRI Distribution by State │   │  │  SRI                          │  │
│  │                            │   │  │  100┤                         │  │
│  │      ╭───┬───┬───╮         │   │  │   80┤                         │  │
│  │      │   │ ● │   │         │   │  │   60┤    ●                    │  │
│  │   ───┴───┴───┴───┴───      │   │  │   40┤  ●   ●                  │  │
│  │  Min Q1  Med Q3 Max        │   │  │   20┤● ● ●   ●                │  │
│  │                            │   │  │    0└────────────────          │  │
│  │  Outliers: ●●              │   │  │      0   50  100  150 200     │  │
│  └────────────────────────────┘   │  │      Yield per Acre           │  │
│                                   │  └───────────────────────────────┘  │
├───────────────────────────────────┴──────────────────────────────────────┤
│  WATERFALL CHART: SRI Component Contribution                            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  SRI Score Breakdown                                             │   │
│  │  100┤                                                             │   │
│  │   80┤                                                             │   │
│  │   60┤                                                             │   │
│  │   40┤  ████                                                       │   │
│  │   20┤  ████  +██  +██  +███  = ████                              │   │
│  │    0└──────────────────────────────────────                      │   │
│  │      Yield Weather Drought Econ  Final                           │   │
│  │      17.7   +1.0   +0.0   +5.3  = 23.8                           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
├──────────────────────────────────────────────────────────────────────────┤
│  TABLE: State-Level Details (scrollable)                                │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ State      │ Yield │ SRI  │ Risk Cat │ Recommendation             │   │
│  │ Texas      │ 21.0  │ 41.2 │ Moderate │ +5% stockpile              │   │
│  │ California │ 125.0 │  6.2 │ Low      │ Normal inventory           │   │
│  │ Iowa       │ 222.0 │ 12.4 │ Low      │ Normal inventory           │   │
│  │ ...        │ ...   │ ...  │ ...      │ ...                        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
```

**Specific Visual Configurations**:

1. **Tile Slicer: Commodity Selection**
   - **Field**: `FactSRI[commodity]`
   - **Style**: Tile with icons
   - **Custom Icons**: 🌽 (Corn), 🫘 (Soybeans), 🌾 (Wheat)
   - **Single Select**: Yes
   - **Size**: 3 tiles × 150px width

2. **Multi-Row Card: Commodity Statistics**
   - **Fields**:
     - `[Commodity_Avg_SRI]`
     - COUNT of states (filtered by commodity)
     - MIN of SRI (for this commodity)
     - MAX of SRI (for this commodity)
   - **Style**: Compact, horizontal layout
   - **Size**: 1200x100 px

3. **Box & Whisker Plot: SRI Distribution**
   - **X-Axis**: None (single commodity)
   - **Y-Axis**: `FactSRI[SRI]`
   - **Category**: Filtered by selected commodity
   - **Show Outliers**: Yes
   - **Tooltip**: State name, exact SRI value
   - **Size**: 400x400 px

4. **Scatter Plot: Yield vs SRI**
   - **X-Axis**: `FactSRI[yield_per_acre]`
   - **Y-Axis**: `FactSRI[SRI]`
   - **Values (Bubble Size)**: Optional - use state population or production volume
   - **Color**: By `FactSRI[risk_category]`
   - **Tooltip**: State, yield, SRI, risk category
   - **Trend Line**: Add linear regression line (negative correlation expected)
   - **Size**: 600x400 px

5. **Waterfall Chart: Component Contribution**
   - **Category**: Component names
   - **Values**:
     - Start: 0
     - Yield: `[Avg_Yield_Risk]`
     - Weather: `[Avg_Weather_Risk]`
     - Drought: `[Avg_Drought_Risk]`
     - Economic: `[Avg_Economic_Risk]`
     - Total: `[Commodity_Avg_SRI]`
   - **Colors**: Green for positive contribution, red for negative
   - **Data Labels**: Show values
   - **Size**: 1200x350 px

6. **Table: State-Level Commodity Details**
   - **Columns**:
     - State: `FactSRI[state_name]`
     - Yield: `FactSRI[yield_per_acre]`
     - SRI: `FactSRI[SRI]`
     - Risk Category: `FactSRI[risk_category]`
     - Recommendation: `FactSRI[recommendation]`
   - **Filters**: Auto-filtered by commodity slicer
   - **Sorting**: By SRI descending
   - **Conditional Formatting**:
     - SRI column: Color scale
     - Risk Category: Background color
   - **Size**: 1200x300 px (scrollable)

---

### **Page 4: Risk Component Deep Dive** ⚖️

**Purpose**: Analyze the four risk components (Yield, Weather, Drought, Economic) in detail.

#### **Visual Elements**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        RISK COMPONENT ANALYSIS                           │
├──────────────────────────────────────────────────────────────────────────┤
│  GAUGE CHARTS (4 Side-by-Side)                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                    │
│  │ Yield   │  │ Weather │  │ Drought │  │Economic │                    │
│  │  Risk   │  │  Risk   │  │  Risk   │  │  Risk   │                    │
│  │         │  │         │  │         │  │         │                    │
│  │   17.7  │  │   4.0   │  │   0.0   │  │  35.0   │                    │
│  │  (35%)  │  │  (25%)  │  │  (25%)  │  │  (15%)  │                    │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘                    │
├──────────────────────────────────────────────────────────────────────────┤
│  STACKED BAR CHART: Component Breakdown by State (Top 20)               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ Texas     ████████████████████░░░░░░ 36.2                        │   │
│  │ Wyoming   ███████████████████░░░░░░░ 35.6                        │   │
│  │ New Mex.  ██████████████████░░░░░░░░ 35.2                        │   │
│  │ Oklahoma  █████████████████░░░░░░░░░ 34.6                        │   │
│  │ ...       ...                                                    │   │
│  │                                                                  │   │
│  │ Legend: ■ Yield ■ Weather ■ Drought ■ Economic                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
├───────────────────────────────────┬──────────────────────────────────────┤
│  LINE CHART: Component Trends     │  MATRIX: State × Component Scores    │
│  ┌────────────────────────────┐   │  ┌───────────────────────────────┐  │
│  │  Risk Score                │   │  │     Yield Weather Drought Econ│  │
│  │  40┤                       │   │  │ TX   100.0   4.0     0.0  35.0│  │
│  │  30┤  Yield ●──●──●        │   │  │ WY    95.8   4.0     0.0  35.0│  │
│  │  20┤  Econ  ●──●──●        │   │  │ NM    92.0   4.0     0.0  35.0│  │
│  │  10┤  Weather●──●──●       │   │  │ ...   ...    ...     ...  ... │  │
│  │   0┤  Drought●──●──●       │   │  │                               │  │
│  │    └───────────────        │   │  │ Color scale: Red→Yellow→Green │  │
│  │     2023  2024  2025       │   │  └───────────────────────────────┘  │
│  └────────────────────────────┘   │                                     │
├───────────────────────────────────┴──────────────────────────────────────┤
│  RIBBON CHART: Dominant Risk Factor by State Over Time                  │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  [Flowing ribbon chart showing which component dominates]        │   │
│  │  2023: Mostly Yield ████████ (60% states)                        │   │
│  │  2024: Mix of Yield/Economic ████░░░░                            │   │
│  │  2025: Mostly Economic ░░░░████                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
```

**Specific Visual Configurations**:

1. **Gauge Charts (4 Components)**
   - **Values**:
     - Gauge 1: `[Avg_Yield_Risk]`
     - Gauge 2: `[Avg_Weather_Risk]`
     - Gauge 3: `[Avg_Drought_Risk]`
     - Gauge 4: `[Avg_Economic_Risk]`
   - **Maximum**: 100 for all gauges
   - **Color Ranges**:
     - 0-25: Green
     - 25-50: Yellow
     - 50-75: Orange
     - 75-100: Red
   - **Callout Value**: Show weight percentage in subtitle
   - **Size**: 250x250 px each

2. **100% Stacked Bar Chart: Component Breakdown**
   - **Y-Axis**: `FactSRI[state_name]` (Top 20 by SRI)
   - **X-Axis**: Stacked percentages (100% total)
   - **Values**:
     - `[Yield_Contribution]`
     - `[Weather_Contribution]`
     - `[Drought_Contribution]`
     - `[Economic_Contribution]`
   - **Colors**: Distinct for each component
   - **Data Labels**: Show percentage contribution
   - **Tooltip**: Absolute values + percentages
   - **Size**: 1200x500 px

3. **Line Chart: Component Trends (Multi-Year)**
   - **X-Axis**: `FactSRI[year]`
   - **Y-Axis**: Risk scores
   - **Lines (4)**:
     - Line 1: `[Avg_Yield_Risk]` (Red)
     - Line 2: `[Avg_Weather_Risk]` (Orange)
     - Line 3: `[Avg_Drought_Risk]` (Yellow)
     - Line 4: `[Avg_Economic_Risk]` (Blue)
   - **Data Markers**: Show points
   - **Legend**: Bottom of chart
   - **Size**: 600x400 px

4. **Matrix: State × Component Heatmap**
   - **Rows**: `FactSRI[state_name]`
   - **Columns**: Component names (Yield, Weather, Drought, Economic)
   - **Values**: Individual risk scores
   - **Conditional Formatting**:
     - Color scale: Red (high) → Green (low)
     - Data bars in cells
   - **Filters**: Top 15 states by SRI
   - **Size**: 600x400 px

5. **Ribbon Chart: Dominant Factor Over Time**
   - **X-Axis**: `FactSRI[year]`
   - **Ribbon Thickness**: Count of states
   - **Ribbon Color**: By `Dominant_Risk_Factor` (calculated column)
   - **Categories**: Yield, Weather, Drought, Economic
   - **Tooltip**: Year, factor, state count
   - **Size**: 1200x300 px

---

### **Page 5: Time Series & Trends** 📈

**Purpose**: Historical analysis and year-over-year trend identification.

#### **Visual Elements**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     HISTORICAL TRENDS & FORECASTING                      │
├──────────────────────────────────────────────────────────────────────────┤
│  AREA CHART: SRI Evolution (2020-2025)                                  │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  SRI                                                             │   │
│  │  50┤                                                             │   │
│  │  40┤     ╱▔▔▔╲                                                   │   │
│  │  30┤    ╱     ╲                                                  │   │
│  │  20┤   ╱       ╲___                                              │   │
│  │  10┤  ╱            ╲___                                          │   │
│  │   0└──────────────────────────────                              │   │
│  │     2020  2021  2022  2023  2024  2025                          │   │
│  │                                                                  │   │
│  │  Shaded area by risk level                                      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────────────────┤
│  COMBO CHART: YoY Change Analysis                                       │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  SRI Value │                          │ % Change                │   │
│  │  40┤                                  ┤ +20%                    │   │
│  │  30┤  ████          ████               ┤  0%                     │   │
│  │  20┤  ████   ████   ████   ████        ┤ -20%                    │   │
│  │  10┤  ████   ████   ████   ████        ┤ -40%                    │   │
│  │   0└──────────────────────────────     ┤                         │   │
│  │     2021   2022   2023   2024   2025   └─────────────            │   │
│  │     Bars: SRI Value | Line: % Change                            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
├───────────────────────────────────┬──────────────────────────────────────┤
│  DECOMPOSITION TREE               │  KEY INFLUENCERS VISUAL             │
│  ┌────────────────────────────┐   │  ┌───────────────────────────────┐  │
│  │ 2025 SRI: 23.7             │   │  │ What influences SRI?          │  │
│  │  ├─ Region                 │   │  │                               │  │
│  │  │  ├─ South: 28.4         │   │  │ 1. State = Texas (+12.5)     │  │
│  │  │  ├─ West: 21.2          │   │  │ 2. Commodity = Soybeans (+8) │  │
│  │  │  └─ Midwest: 18.9       │   │  │ 3. Year = 2022 (+5.3)        │  │
│  │  ├─ Commodity              │   │  │ 4. Drought > 25 (+4.8)       │  │
│  │  │  ├─ Soybeans: 23.7      │   │  │                               │  │
│  │  │  ├─ Corn: 23.8          │   │  │ Decreases SRI:               │  │
│  │  │  └─ Wheat: 23.8         │   │  │ 1. Yield > 150 (-8.2)        │  │
│  │  └─ Risk Cat.              │   │  │ 2. Precipitation > 40 (-5.1) │  │
│  └────────────────────────────┘   │  └───────────────────────────────┘  │
├───────────────────────────────────┴──────────────────────────────────────┤
│  SPARKLINE TABLE: State Trend Indicators                                │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ State      │ 2025 │ Trend (2020-2025)         │ Direction        │   │
│  │ Texas      │ 36.2 │ ●─●─●─●─●─● (increasing)  │ ▲ Worsening     │   │
│  │ California │  8.3 │ ●─●─●─●─●─● (stable)      │ ― Stable         │   │
│  │ Iowa       │ 12.4 │ ●─●─●─●─●─● (decreasing)  │ ▼ Improving     │   │
│  │ ...        │ ...  │ ...                       │ ...              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
```

**Specific Visual Configurations**:

1. **Area Chart: SRI Evolution**
   - **X-Axis**: `FactSRI[year]` (2020-2025)
   - **Y-Axis**: `[National_Avg_SRI]`
   - **Area Fill**: Gradient color based on risk level
   - **Reference Lines**: Add at 25, 50, 75 (risk thresholds)
   - **Forecast**: Enable Power BI forecasting for 2026-2027
   - **Tooltip**: Year, SRI, YoY change, risk level
   - **Size**: 1200x400 px

2. **Combo Chart: SRI Value + % Change**
   - **X-Axis**: `FactSRI[year]`
   - **Primary Y-Axis (Column)**: `[National_Avg_SRI]` (bars)
   - **Secondary Y-Axis (Line)**: `[YoY_SRI_Change_Pct]` (line)
   - **Column Colors**: By risk level
   - **Line Color**: Red if positive, green if negative
   - **Data Labels**: Show on both
   - **Size**: 1200x400 px

3. **Decomposition Tree: Hierarchical Breakdown**
   - **Explain**: `FactSRI[SRI]`
   - **Hierarchies**:
     - Level 1: `DimStates[region]`
     - Level 2: `FactSRI[commodity]`
     - Level 3: `FactSRI[risk_category]`
     - Level 4: `FactSRI[state_name]`
   - **Analysis**: Show which segments drive highest/lowest SRI
   - **Size**: 600x500 px

4. **Key Influencers Visual: AI-Powered Insights**
   - **Analyze**: `FactSRI[SRI]`
   - **Explain By**:
     - `FactSRI[state_name]`
     - `FactSRI[commodity]`
     - `FactSRI[year]`
     - `FactSRI[avg_temp]` (binned)
     - `FactSRI[total_precip]` (binned)
     - `FactSRI[avg_dsci]` (binned)
   - **Target**: What increases SRI / What decreases SRI
   - **Size**: 600x500 px

5. **Table with Sparklines: State Trends**
   - **Columns**:
     - State: `FactSRI[state_name]`
     - 2025 SRI: `FactSRI[SRI]` (filtered to 2025)
     - Trend Sparkline: Mini line chart (2020-2025 SRI values)
     - Direction: Arrow indicator (▲▼―)
     - 3-Year Change: Difference between 2025 and 2022
   - **Conditional Formatting**:
     - Sparklines colored by trend direction
     - Direction arrows colored (red=worsening, green=improving)
   - **Sorting**: By 2025 SRI descending
   - **Size**: 1200x400 px

---

### **Page 6: Strategic Recommendations** 🎯

**Purpose**: Actionable insights and procurement guidance for decision-makers.

#### **Visual Elements**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      STRATEGIC PROCUREMENT GUIDANCE                      │
├──────────────────────────────────────────────────────────────────────────┤
│  PRIORITY MATRIX (Scatter + Bubbles)                                    │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  SRI Risk Score                                                  │   │
│  │  100┤                        ┌─────────────────┐                 │   │
│  │     │                        │ High Priority   │                 │   │
│  │  75 ┤                        │ (High Risk +    │                 │   │
│  │     │                        │ High Volume)    │                 │   │
│  │  50 ┤ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤                 │                 │   │
│  │     │                        │                 │                 │   │
│  │  25 ┤  ●●●                   │  ●              │                 │   │
│  │     │ ●●●●●     Monitor      │  Action         │                 │   │
│  │   0 └──────────────────────────────────────────                 │   │
│  │      0   25   50   75  100  125  150  175  200                  │   │
│  │              Production Volume (millions)                        │   │
│  │                                                                  │   │
│  │  Bubble size = Stockpile recommendation %                        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────────────────┤
│  CARD MATRIX: Risk-Based Actions                                        │
│  ┌────────────────┬────────────────┬────────────────┬──────────────┐    │
│  │ 🟢 Low Risk    │ 🟡 Moderate    │ 🟠 High Risk   │ 🔴 Critical  │    │
│  │                │                │                │              │    │
│  │ 227 States     │ 153 States     │ 0 States       │ 0 States     │    │
│  │                │                │                │              │    │
│  │ ✓ Normal       │ ⚠ Monitor      │ 🚨 +15-20%     │ 🆘 +25%      │    │
│  │   Inventory    │   +5-10%       │   Stockpile    │   Immediate  │    │
│  └────────────────┴────────────────┴────────────────┴──────────────┘    │
├──────────────────────────────────────────────────────────────────────────┤
│  TABLE: Top 10 Action Items (Prioritized)                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ Priority│State  │Commodity│SRI │Volume│Action               │Est $│   │
│  │    1    │Texas  │Soybeans │41.2│ 120M │+10% stockpile       │$12M│   │
│  │    2    │Wyoming│Wheat    │35.6│  45M │+5% stockpile        │$2.2M│  │
│  │    3    │NM     │Wheat    │35.2│  38M │Monitor closely      │ - │   │
│  │   ...   │ ...   │ ...     │... │ ... │ ...                 │...│   │
│  └──────────────────────────────────────────────────────────────────┘   │
├───────────────────────────────────┬──────────────────────────────────────┤
│  CLUSTERED BAR: Stockpile Cost    │  GAUGE: Overall Portfolio Health    │
│  ┌────────────────────────────┐   │  ┌───────────────────────────────┐  │
│  │ Commodity│ Recommended $  │   │  │         Portfolio SRI         │  │
│  │ Corn     │ $8.5M          │   │  │                               │  │
│  │ Soybeans │ $15.2M         │   │  │           23.7                │  │
│  │ Wheat    │ $4.8M          │   │  │         ╱      ╲              │  │
│  │ TOTAL    │ $28.5M         │   │  │      🟢  Healthy  🟢          │  │
│  └────────────────────────────┘   │  └───────────────────────────────┘  │
└───────────────────────────────────┴──────────────────────────────────────┘
```

**Specific Visual Configurations**:

1. **Priority Matrix (Scatter Chart with Bubbles)**
   - **X-Axis**: Production volume (calculated from yield × acreage)
   - **Y-Axis**: `FactSRI[SRI]`
   - **Bubble Size**: Recommended stockpile percentage
   - **Bubble Color**: By `FactSRI[risk_category]`
   - **Quadrants**:
     - Add constant lines at X=median, Y=50
     - Label quadrants (Monitor / Low Priority / Action / High Priority)
   - **Tooltip**: State, commodity, SRI, volume, recommendation, estimated cost
   - **Size**: 1200x500 px

2. **Card Matrix: Risk-Based Action Summary**
   - **4 Cards** (one per risk category)
   - **Each Card Shows**:
     - Risk level icon and color
     - Count of state-commodity combinations
     - Standard recommendation
   - **Conditional Formatting**: Background color by risk level
   - **Size**: 4 cards × 250px width

3. **Table: Top 10 Priority Action Items**
   - **Columns**:
     - Priority Rank: Calculated (SRI × Volume)
     - State: `FactSRI[state_name]`
     - Commodity: `FactSRI[commodity]`
     - SRI: `FactSRI[SRI]`
     - Volume: Production estimate
     - Action: `FactSRI[recommendation]`
     - Estimated Cost: Calculated (Volume × Price × Stockpile %)
   - **Sorting**: By priority rank descending
   - **Conditional Formatting**:
     - SRI column: Color scale
     - Estimated Cost column: Data bars
   - **Top N Filter**: Show only top 10
   - **Size**: 1200x400 px

4. **Clustered Bar Chart: Stockpile Cost Breakdown**
   - **Y-Axis**: `FactSRI[commodity]`
   - **X-Axis**: Total recommended stockpile cost (calculated)
   - **Data Labels**: Show dollar amounts
   - **Total Line**: Add reference line for total budget
   - **Colors**: By commodity (matching theme)
   - **Size**: 600x400 px

5. **Gauge: Overall Portfolio Health**
   - **Value**: `[National_Avg_SRI]`
   - **Maximum**: 100
   - **Target**: 25 (Low Risk threshold)
   - **Color Ranges**:
     - 0-25: Green ("Healthy")
     - 25-50: Yellow ("Monitor")
     - 50-75: Orange ("Caution")
     - 75-100: Red ("Critical")
   - **Callout Label**: Risk level text
   - **Size**: 600x400 px

6. **Text Box: Executive Summary**
   - **Content**: Dynamic text card with DAX
   ```dax
   Executive_Summary =
   "📊 PORTFOLIO ASSESSMENT " & YEAR(TODAY()) & "

   ✓ National Risk: " & [Risk_Level_Text] & " (" & FORMAT([National_Avg_SRI], "0.0") & ")
   ✓ High-Risk States: " & [High_Risk_States] & " require attention
   ✓ Total Investment Needed: $" & FORMAT([Total_Stockpile_Cost], "#,##0.00M") & "

   📈 YoY Change: " & [Trend_Arrow] & " (" & FORMAT([YoY_SRI_Change_Pct], "0.0%") & ")

   🎯 STRATEGIC RECOMMENDATION:
   " & [Strategic_Recommendation] & "

   ⚠️ PRIORITY ACTIONS:
   1. " & TOPN(1, VALUES(FactSRI[state_name]), [National_Avg_SRI], DESC) & " - " & CALCULATE(MAX(FactSRI[recommendation]), TOPN(1, VALUES(FactSRI[state_name]), [National_Avg_SRI], DESC))
   "
   ```
   - **Style**: Large font, color-coded by risk level
   - **Position**: Top of page
   - **Size**: 1200x200 px

---

## 🎨 **Design Theme & Color Palette**

### **Color Scheme**

```css
/* Primary Branding Colors */
--primary-dark-green: #2c5f2d
--primary-medium-green: #4a7c59
--primary-light-green: #7cb342

/* Risk Level Colors (Consistent Across All Visuals) */
--risk-low: #388e3c        /* Green */
--risk-moderate: #fbc02d   /* Yellow */
--risk-high: #f57c00       /* Orange */
--risk-critical: #d32f2f   /* Red */

/* Supporting Colors */
--info-blue: #1976d2
--warning-amber: #ff6f00
--background-light: #f8f9fa
--text-dark: #2d3436
--text-light: #636e72

/* Gradient for Advanced Visuals */
background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
```

### **Typography**

- **Title Font**: Segoe UI Bold, 24-32pt
- **Body Font**: Segoe UI Regular, 10-12pt
- **Data Labels**: Segoe UI Semibold, 9-11pt
- **Card Values**: Segoe UI Bold, 36-48pt

### **Visual Consistency Rules**

1. **All SRI values** use same color scale (green→yellow→orange→red)
2. **All cards** have rounded corners (5px radius)
3. **All charts** have subtle drop shadows for depth
4. **All tooltips** show:
   - Primary metric
   - YoY comparison
   - Rank/percentile
   - Context (e.g., "Top 10%")

### **Page Layout Template**

```
┌─────────────────────────────────────────────────────────────┐
│  LOGO  │  Page Title                    │  Date: Oct 2025  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Filter Panel - Left Sidebar (200px width)]                │
│  • Year Slicer                                               │
│  • Commodity Slicer                                          │
│  • State Slicer                                              │
│  • Risk Category Slicer                                      │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  [Main Content Area (1720px width)]                         │
│  • Dynamic visualizations based on page                     │
│  • Responsive to slicer selections                          │
│  • Cross-filtering enabled                                  │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  Footer: Last Updated: Oct 18, 2025 | Data Source: SRI     │
│  Pipeline v2.0 | Contact: data@agcompany.com                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 **Interactivity & Drillthrough Features**

### **Cross-Filtering Configuration**

1. **All visuals cross-filter each other** (except cards)
2. **Slicers filter all pages** (use Edit Interactions to exempt specific visuals)
3. **Map click** → filters tables and charts to selected state
4. **Chart selection** → highlights related data across page

### **Drillthrough Pages**

**Create 2 Hidden Drillthrough Pages**:

**Drillthrough 1: State Deep Dive**
- **Trigger**: Right-click any state in any visual
- **Content**:
  - State name + flag
  - 3-year SRI trend line
  - Commodity breakdown table
  - Risk component radar chart
  - Historical comparison chart
  - Weather statistics card
  - Recommendation text box

**Drillthrough 2: Commodity Deep Dive**
- **Trigger**: Right-click any commodity
- **Content**:
  - Commodity icon + name
  - State-level distribution map
  - Top/bottom 10 states table
  - Yield distribution histogram
  - Risk factors waterfall
  - Year-over-year comparison

### **Bookmarks for Scenarios**

Create 5 bookmarks for quick navigation:

1. **"Overview"** → Executive Summary page with default filters
2. **"High Risk Alert"** → Filters to SRI ≥ 50, sorted by urgency
3. **"Corn Focus"** → Commodity = Corn across all pages
4. **"Regional View"** → Groups by region instead of state
5. **"Historical Trend"** → Multi-year view on Time Series page

---

## 📊 **Sample DAX for Advanced Calculations**

```dax
/* ============================================================================
   ADVANCED ANALYTICS MEASURES
   ============================================================================ */

// Risk Score Percentile (What % of states have lower SRI?)
SRI_Percentile =
VAR CurrentSRI = AVERAGE(FactSRI[SRI])
RETURN
DIVIDE(
    COUNTROWS(FILTER(ALL(FactSRI), FactSRI[SRI] <= CurrentSRI)),
    COUNTROWS(ALL(FactSRI))
) * 100

// Moving Average (3-Year)
SRI_MA3 =
AVERAGEX(
    DATESINPERIOD(DimCalendar[Date], LASTDATE(DimCalendar[Date]), -3, YEAR),
    [National_Avg_SRI]
)

// Volatility Index (Standard deviation of SRI over time)
SRI_Volatility =
STDEVX.P(
    VALUES(FactSRI[year]),
    [National_Avg_SRI]
)

// Risk-Adjusted Volume (Higher number = bigger concern)
Risk_Adjusted_Volume =
SUMX(
    FactSRI,
    FactSRI[yield_per_acre] * (FactSRI[SRI] / 100)
)

// Forecast Next Year SRI (Simple linear trend)
SRI_Forecast_NextYear =
VAR AvgYoYChange = AVERAGE(FactSRI[YoY_SRI_Diff])
RETURN
[National_Avg_SRI] + AvgYoYChange

// Recommendation Compliance Score (are we following recommendations?)
Compliance_Score =
DIVIDE(
    CALCULATE(COUNTROWS(FactSRI), FactSRI[recommendation] <> "Normal inventory"),
    COUNTROWS(FactSRI)
) * 100
```

---

## 🚀 **Publishing & Sharing Strategy**

### **Power BI Service Setup**

1. **Create Workspace**: "Agricultural Risk Intelligence"
2. **Upload Dataset**: Scheduled refresh every October 2nd (day after pipeline runs)
3. **Create App**: Package dashboard for distribution
4. **Security**: Row-level security by region if needed

### **Refresh Schedule**

```python
# Power BI Dataset Refresh Configuration
Refresh_Schedule = {
    "frequency": "Annual",
    "date": "October 2",
    "time": "06:00 AM UTC",
    "source": "sri_results_{YEAR}.csv",
    "incremental_refresh": True,  # Keep last 3 years
    "partitions": "By Year"
}
```

### **Distribution Methods**

1. **Email Subscription**: Automated daily snapshot to stakeholders
2. **Embedded Dashboard**: iFrame in company portal
3. **Mobile App**: Power BI mobile app optimized layout
4. **Export Options**:
   - PDF report (all 6 pages)
   - PowerPoint (slide deck export)
   - Excel workbook (raw data + pivot tables)

---

## ✅ **Checklist: Building the Dashboard**

### **Phase 1: Data Preparation** (30 minutes)
- [ ] Create `/powerbi_data/` folder
- [ ] Copy `sri_results_2025.csv` to folder
- [ ] Create `state_mapping.csv`
- [ ] Create `commodity_reference.csv`
- [ ] Create `risk_thresholds.csv`
- [ ] Verify all CSVs have correct encoding (UTF-8)

### **Phase 2: Power BI Setup** (1 hour)
- [ ] Open Power BI Desktop
- [ ] Get Data → CSV → Import all 5 files
- [ ] Build data model (create relationships)
- [ ] Create DimCalendar table (DAX: `CALENDARAUTO()`)
- [ ] Add all calculated columns to FactSRI
- [ ] Create all 34 measures

### **Phase 3: Page 1 - Executive Summary** (2 hours)
- [ ] Create blank page, rename "Executive Summary"
- [ ] Add background image/gradient
- [ ] Create 4 KPI cards (Avg SRI, High-Risk States, etc.)
- [ ] Add donut chart (risk distribution)
- [ ] Add line chart (3-year trend)
- [ ] Add bar chart (component breakdown)
- [ ] Add year slicer (top right)
- [ ] Test cross-filtering

### **Phase 4: Page 2 - Geographic Map** (2 hours)
- [ ] Create page "Geographic Risk Map"
- [ ] Add filled map visual (choropleth)
- [ ] Configure state-level mapping
- [ ] Add color scale (green→red)
- [ ] Create Top 15 states table
- [ ] Add regional breakdown chart
- [ ] Add commodity slicer
- [ ] Test map interactivity

### **Phase 5: Page 3 - Commodity Analysis** (2 hours)
- [ ] Create page "Commodity Analysis"
- [ ] Add tile slicer (commodity selection)
- [ ] Add multi-row card (commodity stats)
- [ ] Create box & whisker plot
- [ ] Create scatter plot (yield vs SRI)
- [ ] Add waterfall chart (components)
- [ ] Create state-level detail table
- [ ] Test commodity filtering

### **Phase 6: Page 4 - Risk Components** (2 hours)
- [ ] Create page "Risk Component Deep Dive"
- [ ] Add 4 gauge charts (one per component)
- [ ] Create 100% stacked bar (component breakdown)
- [ ] Add line chart (multi-year trends)
- [ ] Create matrix (state × component heatmap)
- [ ] Add ribbon chart (dominant factor)
- [ ] Configure conditional formatting

### **Phase 7: Page 5 - Time Series** (2 hours)
- [ ] Create page "Historical Trends"
- [ ] Add area chart (SRI evolution)
- [ ] Create combo chart (value + % change)
- [ ] Add decomposition tree
- [ ] Add key influencers visual
- [ ] Create sparkline table (state trends)
- [ ] Enable forecasting on area chart

### **Phase 8: Page 6 - Recommendations** (2 hours)
- [ ] Create page "Strategic Recommendations"
- [ ] Add priority matrix (scatter + bubbles)
- [ ] Create 4-card risk action summary
- [ ] Build Top 10 action items table
- [ ] Add stockpile cost chart
- [ ] Create portfolio health gauge
- [ ] Add executive summary text box
- [ ] Format with dynamic DAX text

### **Phase 9: Drillthrough & Interactivity** (1 hour)
- [ ] Create "State Deep Dive" drillthrough page
- [ ] Create "Commodity Deep Dive" drillthrough page
- [ ] Configure cross-filtering (Edit Interactions)
- [ ] Create 5 bookmarks
- [ ] Test all navigation paths
- [ ] Add buttons for bookmark navigation

### **Phase 10: Design & Polish** (1 hour)
- [ ] Apply consistent color theme (all pages)
- [ ] Add company logo (all pages)
- [ ] Format all chart titles (bold, consistent size)
- [ ] Align visual elements (use snap-to-grid)
- [ ] Add page navigation buttons
- [ ] Create footer (data source, last updated)
- [ ] Test mobile layout (View → Mobile Layout)
- [ ] Add tooltips to all visuals

### **Phase 11: Testing & Validation** (30 minutes)
- [ ] Test all slicers (verify filtering works)
- [ ] Click through all pages (check loading speed)
- [ ] Test drillthrough (right-click states/commodities)
- [ ] Verify all DAX measures calculate correctly
- [ ] Check data labels (no truncation)
- [ ] Test on different screen sizes
- [ ] Review accessibility (high contrast mode)

### **Phase 12: Publish & Share** (30 minutes)
- [ ] Save `.pbix` file with version number
- [ ] Publish to Power BI Service
- [ ] Set up scheduled refresh (October 2nd)
- [ ] Create Power BI App
- [ ] Configure access permissions
- [ ] Share with stakeholders
- [ ] Send user guide/training video

**Total Estimated Time**: 14.5 hours spread over 2-3 days

---

## 📝 **Key Takeaways**

### **What Makes This Dashboard Dynamic?**

1. **Cross-Filtering**: Click anywhere, everything updates
2. **Drillthrough**: Deep dive into any state or commodity
3. **Year Slider**: Compare 2023 vs 2024 vs 2025 instantly
4. **Bookmarks**: One-click access to preset scenarios
5. **AI Insights**: Key Influencers auto-detects patterns
6. **Forecasting**: Predicts next year's SRI trend

### **What Makes This Dashboard Professional?**

1. **Consistent Design**: Same colors, fonts, layout across all pages
2. **KPI Cards**: C-level executives see key numbers immediately
3. **Storytelling**: 6 pages tell complete risk story (overview → detail → action)
4. **Conditional Formatting**: Red/yellow/green instantly shows risk
5. **Tooltips**: Hover for context without cluttering visuals
6. **Mobile-Optimized**: Works on tablets and phones

### **Business Impact**

- **5-minute executive briefing** (Page 1 only)
- **15-minute deep dive** (Pages 1-3)
- **1-hour strategic planning session** (All 6 pages)
- **Data-driven procurement decisions** (Page 6 recommendations)
- **Early warning system** (YoY trends on Page 5)

---

This structure gives you a **complete blueprint** to build a world-class Power BI dashboard. Every visual is specified with exact X/Y axes, colors, and configurations. Just follow the checklist step-by-step! 🚀📊

