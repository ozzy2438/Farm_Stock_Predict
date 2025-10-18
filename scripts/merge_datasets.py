import pandas as pd
import numpy as np

print("="*70)
print("🔗 MERGING CROP YIELD, WEATHER & DROUGHT DATA")
print("="*70)

# Load all datasets
print("\n📂 Loading datasets...")
crop_df = pd.read_csv('usda_crop_yield_2010_2024.csv')
weather_df = pd.read_csv('weather_data_2010_2024.csv')
drought_df = pd.read_csv('drought_data_2010_2024.csv')

print(f"  ✓ Crop yield data: {len(crop_df):,} records")
print(f"  ✓ Weather data: {len(weather_df):,} records")
print(f"  ✓ Drought data: {len(drought_df):,} records")

# Merge datasets on year and state_name
print("\n🔀 Merging datasets...")

# First merge crop with weather
merged = pd.merge(crop_df, weather_df, on=['year', 'state_name'], how='left')
print(f"  ✓ Merged crop + weather: {len(merged):,} records")

# Then merge with drought
merged = pd.merge(merged, drought_df, on=['year', 'state_name'], how='left')
print(f"  ✓ Merged all datasets: {len(merged):,} records")

# Check for missing values
print("\n🔍 Data quality check:")
print("-" * 70)
missing = merged.isnull().sum()
print(missing[missing > 0] if any(missing > 0) else "  ✓ No missing values!")

# Add calculated features for risk modeling
print("\n🧮 Calculating derived features...")

# 1. Yield anomaly (deviation from state average)
state_avg = merged.groupby(['state_name', 'commodity'])['Value'].transform('mean')
merged['yield_anomaly'] = ((merged['Value'] - state_avg) / state_avg * 100)

# 2. Year-over-year yield change
merged = merged.sort_values(['state_name', 'commodity', 'year'])
merged['yield_yoy_change'] = merged.groupby(['state_name', 'commodity'])['Value'].pct_change() * 100

# 3. Temperature stress indicator (deviation from optimal)
# Optimal growing temp ~70F for most crops
merged['temp_stress'] = abs(merged['avg_temp_f'] - 70)

# 4. Precipitation adequacy (deviation from state average)
state_precip_avg = merged.groupby('state_name')['total_precip_inches'].transform('mean')
merged['precip_anomaly'] = ((merged['total_precip_inches'] - state_precip_avg) / state_precip_avg * 100)

# 5. Drought risk score (normalized 0-100)
merged['drought_risk_score'] = (merged['drought_severity_index'] / 500) * 100

print("  ✓ yield_anomaly: % deviation from state average")
print("  ✓ yield_yoy_change: % change from previous year")
print("  ✓ temp_stress: deviation from optimal temperature")
print("  ✓ precip_anomaly: % deviation from state average")
print("  ✓ drought_risk_score: normalized 0-100")

# Save merged dataset
output_file = 'merged_farm_data.csv'
merged.to_csv(output_file, index=False)

print(f"\n💾 Saved merged dataset: {output_file}")
print(f"   Total records: {len(merged):,}")
print(f"   Features: {len(merged.columns)}")

print("\n📊 Sample of merged data:")
print("-" * 70)
print(merged.head(10).to_string(index=False))

print("\n📈 Feature statistics:")
print("-" * 70)
feature_cols = ['Value', 'avg_temp_f', 'total_precip_inches', 'drought_severity_index',
                'yield_anomaly', 'temp_stress', 'precip_anomaly', 'drought_risk_score']
print(merged[feature_cols].describe().round(2))

print("\n" + "="*70)
print("✓ Dataset merge complete!")
print("  Ready for SRI (Stock Risk Index) modeling")
print("="*70)
