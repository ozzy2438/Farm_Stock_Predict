# 🌾 Farm Stock Prediction - Stock Risk Index (SRI) Model

A comprehensive agricultural risk assessment system that combines crop yield data, weather patterns, and drought conditions to predict agricultural commodity risk levels.

## 📊 Project Overview

This project develops a **Stock Risk Index (SRI)** for major agricultural commodities (Corn, Soybeans, Wheat) using:
- USDA crop yield data (2010-2025)
- Weather data (temperature & precipitation)
- Drought severity indices

### Key Features
- ✅ Multi-year historical data analysis (15+ years)
- ✅ State-level granularity across 50 US states
- ✅ Composite risk scoring (0-100 scale)
- ✅ Predictive analytics for yield trends
- ✅ Interactive visualizations and reports

## 🎯 Stock Risk Index (SRI) Components

The SRI is calculated using three weighted components:

### 1. **Yield Risk (40%)**
- Yield volatility (3-year rolling standard deviation)
- Year-over-year yield decline indicators
- Historical yield anomalies

### 2. **Weather Risk (30%)**
- Temperature stress (deviation from optimal growing conditions)
- Precipitation anomalies (excess or deficit)

### 3. **Drought Risk (30%)**
- Drought severity index
- Drought persistence (consecutive high-drought years)

**Formula:**
```
SRI = 0.40 × Yield_Risk + 0.30 × Weather_Risk + 0.30 × Drought_Risk
```

### Risk Classification
- **Low Risk**: SRI < 25
- **Moderate Risk**: 25 ≤ SRI < 50
- **High Risk**: 50 ≤ SRI < 75
- **Very High Risk**: SRI ≥ 75

## 📁 Project Structure

```
Farm_Stock_Predit/
├── main.py                      # Data fetching from USDA QuickStats API
├── fetch_weather_data.py        # Weather & drought data collection
├── merge_datasets.py            # Combine all data sources
├── eda_analysis.py              # Exploratory data analysis
├── visualizations.py            # Create charts and graphs
├── sri_model.py                 # SRI calculation engine
├── validate_sri.py              # Model validation & testing
│
├── Data Files:
├── usda_crop_yield_2010_2024.csv    # Raw crop yield data (12,364 records)
├── weather_data_2010_2024.csv       # Weather metrics
├── drought_data_2010_2024.csv       # Drought severity data
├── merged_farm_data.csv             # Combined dataset
├── sri_results.csv                  # Final SRI scores
│
└── Visualizations:
    ├── crop_yield_analysis.png      # Yield trends & distributions
    ├── corn_yield_heatmap.png       # State-year heatmap
    ├── sri_analysis.png             # SRI component breakdown
    └── sri_validation.png           # Model validation results
```

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.8+
pip install requests pandas matplotlib seaborn scikit-learn scipy
```

### Installation
```bash
# Clone or download the project
cd Farm_Stock_Predit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install requests pandas matplotlib seaborn scikit-learn scipy
```

### Usage

#### 1. Fetch Crop Yield Data
```bash
python main.py
```
Fetches corn, soybeans, and wheat yield data from USDA QuickStats API (2010-2025).

#### 2. Get Weather & Drought Data
```bash
python fetch_weather_data.py
```
Creates weather and drought datasets (note: currently uses mock data for demonstration).

#### 3. Merge Datasets
```bash
python merge_datasets.py
```
Combines crop, weather, and drought data into a unified dataset.

#### 4. Run Exploratory Analysis
```bash
python eda_analysis.py
python visualizations.py
```
Generates statistical summaries and visualizations.

#### 5. Calculate SRI Scores
```bash
python sri_model.py
```
Computes Stock Risk Index for all records.

#### 6. Validate Model
```bash
python validate_sri.py
```
Tests model accuracy and predictive power.

## 📈 Key Findings

### Crop Yield Growth (2010-2024)
- **Corn**: +12.3% (116.4 → 130.6 bushels/acre)
- **Soybeans**: +22.5% (38.2 → 46.9 bushels/acre)
- **Wheat**: +15.2% (56.6 → 65.2 bushels/acre)

### SRI Statistics
- **Mean SRI**: 22.2
- **Range**: 4.6 - 80.7
- **Most at-risk commodity**: CORN (avg SRI: 29.2)
- **Least at-risk commodity**: SOYBEANS (avg SRI: 16.5)

### Top Risk States (2024, CORN)
1. California - SRI: 67.1 (High)
2. Arizona - SRI: 65.2 (High)
3. Missouri - SRI: 55.5 (High)
4. Texas - SRI: 53.5 (High)
5. Arkansas - SRI: 53.4 (High)

### Lowest Risk States (2024, CORN)
1. Tennessee - SRI: 6.1 (Low)
2. Iowa - SRI: 6.8 (Low)
3. Illinois - SRI: 9.1 (Low)
4. Kansas - SRI: 9.7 (Low)

## 🧪 Model Validation

### Test Results (2/4 Passed)
✅ **Historical Validation**: PASS
- SRI during major drops: 41.9
- SRI during normal years: 20.8
- Successfully identifies historical yield failures

✅ **Component Sensitivity**: PASS
- All components contribute meaningfully to final SRI

⚠️ **Correlation Test**: FAIL
- Some unexpected patterns require further investigation

⚠️ **Predictive Power**: FAIL
- Needs refinement with real weather data

### Validation Insights
The model successfully identifies major historical crop failures, with SRI elevated by **21.1 points** during major yield drops. However, predictive accuracy could be improved with:
1. Real weather data (vs. mock data)
2. Additional features (soil quality, farming practices)
3. Machine learning enhancement

## 📊 Data Sources

### Current (Demo)
- **Crop Yields**: USDA QuickStats API (Real data)
- **Weather**: Mock data (demonstration purposes)
- **Drought**: Mock data (demonstration purposes)

### Production Recommendations
For production deployment, replace mock data with:
1. **NOAA Climate Data Online** - Temperature & precipitation
   - API: https://www.ncdc.noaa.gov/cdo-web/
   - Get free API key: https://www.ncdc.noaa.gov/cdo-web/token

2. **US Drought Monitor** - Drought severity indices
   - Website: https://droughtmonitor.unl.edu
   - Data download: https://droughtmonitor.unl.edu/DmData/DataDownload.aspx

## 🔮 Future Enhancements

### Short-term
- [ ] Integrate real NOAA weather data
- [ ] Add soil moisture index
- [ ] Include commodity price correlations
- [ ] Build interactive dashboard (Streamlit/Dash)

### Long-term
- [ ] Machine learning prediction model (LSTM/Random Forest)
- [ ] Real-time data pipeline
- [ ] Multi-year yield forecasting
- [ ] Climate change scenario modeling
- [ ] Integration with commodity trading platforms

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Real-time data integration
- Additional risk factors (pests, diseases)
- Model accuracy improvements
- Dashboard development
- API development

## 📝 License

This project is for educational and research purposes.

## 📧 Contact

For questions or collaboration:
- Project: Farm Stock Prediction
- Focus: Agricultural risk assessment & commodity analysis

## 🙏 Acknowledgments

- **USDA NASS** - For QuickStats API and agricultural data
- **NOAA** - Climate data resources
- **US Drought Monitor** - Drought severity data

---

**Note**: This is a demonstration project. For production use, replace mock weather/drought data with real sources and conduct thorough validation.

Last Updated: October 15, 2025
