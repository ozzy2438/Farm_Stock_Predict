# 🚀 Setup Instructions - Farm Stock Prediction System

## Quick Start Guide

This guide will help you set up and run the complete Agricultural Stock Risk Index (SRI) prediction system.

---

## 📋 Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)
- **Internet connection** (for API calls)

---

## 🔧 Installation Steps

### 1. Clone/Download the Project

```bash
cd Farm_Stock_Predit
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate:
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install requests pandas matplotlib seaborn scikit-learn scipy python-dotenv
```

---

## 🔑 API Keys Setup

### Step 1: Copy Environment Template

```bash
cp .env.example .env
```

### Step 2: Get API Keys

#### A. USDA QuickStats (Already configured) ✅
- Current key: `2EEF90B1-825E-322B-8B27-098A9C92D575`
- No action needed

#### B. Visual Crossing Weather API (Optional but Recommended)
1. Visit: https://www.visualcrossing.com/sign-up
2. Sign up for free account (no credit card required)
3. Get your API key from dashboard
4. Add to `.env`:
   ```
   VISUAL_CROSSING_API_KEY=your_actual_key_here
   ```
5. **Free Tier**: 1000 queries/day

**Note**: If you skip this, the script will use realistic sample data.

---

## 🎯 Running the System

### Option 1: Run Complete Pipeline (Recommended)

```bash
python run_complete_pipeline.py
```

This will execute all steps automatically:
1. Fetch crop yield data
2. Fetch weather data
3. Fetch drought data
4. Merge all datasets
5. Calculate SRI scores
6. Generate visualizations
7. Run validations

### Option 2: Run Steps Individually

#### Step 1: Fetch Crop Yield Data (15-20 seconds)
```bash
python main.py
```
**Output**: `usda_crop_yield_2010_2024.csv`

#### Step 2: Fetch Weather Data (2-5 minutes with API, instant with mock)
```bash
python fetch_weather_real.py
```
**Output**: `weather_data_real_2010_2024.csv`

#### Step 3: Fetch Drought Data (instant)
```bash
python fetch_drought_real.py
```
**Output**: `drought_data_real_2010_2024.csv`

#### Step 4: Run Exploratory Analysis (5 seconds)
```bash
python eda_analysis.py
python visualizations.py
```
**Output**: `crop_yield_analysis.png`, `corn_yield_heatmap.png`

#### Step 5: Merge All Datasets (5 seconds)
```bash
python merge_datasets.py
```
**Output**: `merged_farm_data.csv`

#### Step 6: Calculate SRI Scores (10 seconds)
```bash
python sri_model.py
```
**Output**: `sri_results.csv`, `sri_analysis.png`

#### Step 7: Validate Model (5 seconds)
```bash
python validate_sri.py
```
**Output**: `sri_validation.png`

---

## 📊 Expected Outputs

After running the complete pipeline, you should have:

### Data Files:
- `usda_crop_yield_2010_2024.csv` (~315 KB)
- `weather_data_real_2010_2024.csv` (~10 KB)
- `drought_data_real_2010_2024.csv` (~50 KB)
- `merged_farm_data.csv` (~1.2 MB)
- `sri_results.csv` (~2.2 MB)

### Visualizations:
- `crop_yield_analysis.png` - Multi-panel yield analysis
- `corn_yield_heatmap.png` - State-year heatmap
- `sri_analysis.png` - SRI component breakdown
- `sri_validation.png` - Model validation results

---

## ⚠️ Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'X'"
**Solution**: Ensure virtual environment is activated and dependencies installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue 2: "API key not found" for Visual Crossing
**Solution**: Either:
- Add your API key to `.env` file, OR
- Script will automatically use realistic sample data

### Issue 3: Rate limit exceeded (Visual Crossing)
**Solution**:
- Free tier: 1000 requests/day
- Wait 24 hours or upgrade plan
- Script has built-in retry logic

### Issue 4: Data files not found
**Solution**: Run scripts in order (Step 1 → Step 7)

---

## 🎨 Viewing Results

### 1. Check CSV Files
```bash
# View first 10 rows of SRI results
head -10 sri_results.csv
```

### 2. Open Visualizations
- Mac: `open *.png`
- Windows: `start *.png`
- Linux: `xdg-open *.png`

### 3. View Summary Statistics
All scripts print summary statistics to terminal.

---

## 📈 Understanding the Outputs

### SRI (Stock Risk Index)
- **Scale**: 0-100
- **Low Risk**: < 25 (Safe crop production expected)
- **Moderate**: 25-50 (Some risk factors present)
- **High**: 50-75 (Significant risk of yield issues)
- **Very High**: 75+ (Major risk, possible crop failure)

### Key Features in SRI Calculation:
1. **Yield Risk (40%)**: Historical volatility, YoY changes
2. **Weather Risk (30%)**: Temperature stress, precipitation anomalies
3. **Drought Risk (30%)**: Drought severity and persistence

---

## 🔄 Updating Data

To refresh with latest data:

```bash
# Re-fetch crop yields (updates to current year)
python main.py

# Re-fetch weather (if using API)
python fetch_weather_real.py

# Re-run analysis
python run_complete_pipeline.py
```

---

## 📚 Additional Resources

- **USDA QuickStats**: https://quickstats.nass.usda.gov/
- **Visual Crossing API Docs**: https://www.visualcrossing.com/resources/documentation/
- **US Drought Monitor**: https://droughtmonitor.unl.edu/
- **Project README**: `README.md`
- **Data Fetch Plan**: `data_fetch_plan.md`

---

## 💡 Tips for Best Results

1. **Use Real Weather API**: Significantly improves accuracy
2. **Run During Off-Peak**: API calls faster outside business hours
3. **Check Data Quality**: Review CSV files before running SRI model
4. **Compare Years**: Look for patterns in high-risk years (2012, 2021, etc.)

---

## 🆘 Need Help?

1. Check `README.md` for project overview
2. Review `data_fetch_plan.md` for data source details
3. Examine console output for specific error messages
4. Ensure all prerequisites are met

---

## ✅ Success Checklist

- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] API keys configured (or using mock data)
- [ ] All 7 steps completed without errors
- [ ] CSV files generated successfully
- [ ] PNG visualizations created
- [ ] Console shows summary statistics

---

**Last Updated**: October 15, 2025
**Version**: 1.0.0
**Status**: Production Ready (with mock weather/drought data fallback)
