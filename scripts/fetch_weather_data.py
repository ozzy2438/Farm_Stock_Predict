import requests
import pandas as pd
import time
from datetime import datetime

print("="*70)
print("🌦️  FETCHING WEATHER & DROUGHT DATA")
print("="*70)

# NOAA Climate Data Online (CDO) API
# You'll need to get a free API key from: https://www.ncdc.noaa.gov/cdo-web/token
# For now, we'll use a placeholder and show you how to get it

NOAA_API_KEY = "YOUR_NOAA_API_KEY_HERE"  # Get from https://www.ncdc.noaa.gov/cdo-web/token

# US Drought Monitor data (public, no key needed)
DROUGHT_MONITOR_URL = "https://droughtmonitor.unl.edu/DmData/DataDownload/DSCI.aspx"

print("\n1️⃣ Fetching US Drought Monitor Data...")
print("-" * 70)

try:
    # Fetch drought severity data
    # The DSCI (Drought Severity and Coverage Index) is available as CSV
    params = {
        'area': 'conus',  # Continental US
        'stats': '2',      # State-level statistics
    }

    # Note: This is a simplified example. Real implementation would need proper date ranges
    print("⚠️  US Drought Monitor data requires manual download or web scraping")
    print("   Visit: https://droughtmonitor.unl.edu/DmData/DataDownload.aspx")
    print("   We'll create a mock dataset for demonstration purposes")

    # Create mock drought data for demonstration
    states = ['ALABAMA', 'ARIZONA', 'ARKANSAS', 'CALIFORNIA', 'COLORADO',
              'ILLINOIS', 'INDIANA', 'IOWA', 'KANSAS', 'KENTUCKY',
              'MICHIGAN', 'MINNESOTA', 'MISSISSIPPI', 'MISSOURI', 'NEBRASKA',
              'NORTH CAROLINA', 'NORTH DAKOTA', 'OHIO', 'OKLAHOMA', 'SOUTH DAKOTA',
              'TENNESSEE', 'TEXAS', 'WISCONSIN']

    years = range(2010, 2026)

    drought_data = []
    import random
    random.seed(42)

    for state in states:
        for year in years:
            # Mock drought severity index (0-500, higher = worse drought)
            # Add some regional patterns
            base_drought = 150
            if state in ['CALIFORNIA', 'ARIZONA', 'TEXAS', 'OKLAHOMA']:
                base_drought = 250  # More drought-prone
            elif state in ['IOWA', 'ILLINOIS', 'INDIANA', 'OHIO']:
                base_drought = 100  # Less drought-prone

            drought_score = base_drought + random.randint(-50, 100)

            drought_data.append({
                'year': year,
                'state_name': state,
                'drought_severity_index': drought_score,
                'drought_category': 'High' if drought_score > 300 else 'Moderate' if drought_score > 200 else 'Low'
            })

    drought_df = pd.DataFrame(drought_data)
    drought_df.to_csv('drought_data_2010_2024.csv', index=False)
    print(f"✓ Created mock drought data: {len(drought_df)} records")
    print(f"  Saved to: drought_data_2010_2024.csv")

except Exception as e:
    print(f"✗ Error fetching drought data: {e}")

print("\n2️⃣ Weather Data (Temperature & Precipitation)")
print("-" * 70)

try:
    # Create mock weather data
    weather_data = []

    for state in states:
        for year in years:
            # Mock temperature (avg growing season temp in F)
            base_temp = 68
            if state in ['ARIZONA', 'TEXAS', 'CALIFORNIA']:
                base_temp = 78
            elif state in ['NORTH DAKOTA', 'MINNESOTA', 'WISCONSIN']:
                base_temp = 62

            temp = base_temp + random.uniform(-5, 5)

            # Mock precipitation (inches during growing season)
            base_precip = 25
            if state in ['ARIZONA', 'CALIFORNIA']:
                base_precip = 8
            elif state in ['IOWA', 'ILLINOIS', 'INDIANA']:
                base_precip = 35

            precip = base_precip + random.uniform(-10, 10)

            weather_data.append({
                'year': year,
                'state_name': state,
                'avg_temp_f': round(temp, 1),
                'total_precip_inches': round(max(0, precip), 1)
            })

    weather_df = pd.DataFrame(weather_data)
    weather_df.to_csv('weather_data_2010_2024.csv', index=False)
    print(f"✓ Created mock weather data: {len(weather_df)} records")
    print(f"  Saved to: weather_data_2010_2024.csv")

except Exception as e:
    print(f"✗ Error creating weather data: {e}")

print("\n" + "="*70)
print("📋 SUMMARY")
print("="*70)
print("✓ Drought data created (mock): drought_data_2010_2024.csv")
print("✓ Weather data created (mock): weather_data_2010_2024.csv")
print("\n⚠️  NOTE: These are mock datasets for demonstration.")
print("   For production, you should:")
print("   1. Get NOAA API key: https://www.ncdc.noaa.gov/cdo-web/token")
print("   2. Download real drought data: https://droughtmonitor.unl.edu")
print("   3. Use NOAA Climate Data Online API for temperature/precipitation")
print("="*70)

print("\n📊 Sample Drought Data:")
print(drought_df.head(10))

print("\n🌡️  Sample Weather Data:")
print(weather_df.head(10))
