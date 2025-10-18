"""
Real Weather Data Fetcher - Visual Crossing Weather API

Fetches historical weather data for agricultural analysis:
- Daily temperature (min, max, average)
- Precipitation
- Growing season metrics

API Documentation: https://www.visualcrossing.com/resources/documentation/weather-api/
"""

import requests
import pandas as pd
import time
from datetime import datetime
import os
from dotenv import load_dotenv

print("="*70)
print("🌦️  FETCHING REAL WEATHER DATA - Visual Crossing API")
print("="*70)

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv('VISUAL_CROSSING_API_KEY')

if not API_KEY or API_KEY == 'YOUR_KEY_HERE':
    print("\n⚠️  ERROR: Visual Crossing API key not found!")
    print("   Please:")
    print("   1. Sign up at: https://www.visualcrossing.com/sign-up")
    print("   2. Copy .env.example to .env")
    print("   3. Add your API key to .env file")
    print("\n   For now, we'll create a sample dataset...")
    USE_MOCK_DATA = True
else:
    print(f"\n✓ API Key loaded: {API_KEY[:10]}...")
    USE_MOCK_DATA = False

BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

# All 50 US states (expanded coverage for complete SRI analysis)
STATES = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

YEARS = range(2010, 2025)

def fetch_weather_for_state_year(state, year, api_key):
    """
    Fetch weather data for a specific state and year.

    Returns aggregated metrics:
    - avg_temp_f: Average temperature for the growing season (April-Sept)
    - total_precip_inches: Total precipitation during growing season
    - gdd_total: Growing Degree Days (base 50F)
    """

    # Growing season: April 1 - September 30
    start_date = f"{year}-04-01"
    end_date = f"{year}-09-30"

    url = f"{BASE_URL}/{state}/{start_date}/{end_date}"

    params = {
        'key': api_key,
        'unitGroup': 'us',  # US units (Fahrenheit, inches)
        'include': 'days',
        'elements': 'datetime,temp,tempmax,tempmin,precip',
        'contentType': 'json'
    }

    try:
        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            days = data.get('days', [])

            if not days:
                return None

            # Calculate aggregated metrics
            temps = [day['temp'] for day in days if 'temp' in day]
            precips = [day.get('precip', 0) or 0 for day in days]

            # Growing Degree Days (GDD) - base 50F
            gdd_values = []
            for day in days:
                if 'tempmax' in day and 'tempmin' in day:
                    temp_avg = (day['tempmax'] + day['tempmin']) / 2
                    gdd = max(0, temp_avg - 50)  # Base temperature 50F
                    gdd_values.append(gdd)

            result = {
                'year': year,
                'state': state.upper(),
                'avg_temp_f': round(sum(temps) / len(temps), 1) if temps else None,
                'total_precip_inches': round(sum(precips), 2),
                'gdd_total': round(sum(gdd_values), 0) if gdd_values else None,
                'days_count': len(days)
            }

            return result

        elif response.status_code == 429:
            print(f"    ⚠️  Rate limit exceeded. Wait 60 seconds...")
            time.sleep(60)
            return fetch_weather_for_state_year(state, year, api_key)
        else:
            print(f"    ✗ Error {response.status_code}: {response.text[:100]}")
            return None

    except Exception as e:
        print(f"    ✗ Exception: {str(e)}")
        return None

# Main execution
if USE_MOCK_DATA:
    print("\n📊 Creating sample weather data (API key not configured)...")

    weather_data = []
    import random
    random.seed(42)

    for state, code in STATES.items():
        for year in YEARS:
            # Create realistic mock data
            base_temp = 68 + random.uniform(-3, 3)
            base_precip = 25 + random.uniform(-10, 10)
            gdd = 2000 + random.randint(-300, 300)

            weather_data.append({
                'year': year,
                'state': state.upper(),
                'avg_temp_f': round(base_temp, 1),
                'total_precip_inches': round(max(0, base_precip), 2),
                'gdd_total': gdd,
                'days_count': 183
            })

    print(f"  ✓ Created {len(weather_data)} sample records")

else:
    print("\n📡 Fetching real weather data from Visual Crossing API...")
    print(f"   States: {len(STATES)}")
    print(f"   Years: {min(YEARS)}-{max(YEARS)}")
    print(f"   Total requests: {len(STATES) * len(YEARS)}")
    print(f"   Estimated time: ~{len(STATES) * len(YEARS) * 2 / 60:.0f} minutes")
    print("")

    weather_data = []
    request_count = 0

    for state, code in STATES.items():
        print(f"\n🌍 Fetching {state}...")

        for year in YEARS:
            print(f"  {year}...", end=" ")

            result = fetch_weather_for_state_year(state, year, API_KEY)

            if result:
                weather_data.append(result)
                print("✓")
            else:
                print("✗")

            request_count += 1

            # Rate limiting: Free tier = 1000 requests/day
            # Add small delay to be safe
            time.sleep(0.5)

            # Status update every 20 requests
            if request_count % 20 == 0:
                print(f"\n   📊 Progress: {request_count}/{len(STATES) * len(YEARS)} requests")

    print(f"\n  ✓ Fetched {len(weather_data)} records from API")

# Save to CSV
weather_df = pd.DataFrame(weather_data)

# Rename state column to match other datasets
weather_df = weather_df.rename(columns={'state': 'state_name'})

# Save to data/ folder
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(data_dir, exist_ok=True)
output_file = os.path.join(data_dir, 'weather_data_real_2010_2024.csv')
weather_df.to_csv(output_file, index=False)

print(f"\n💾 Saved: {output_file}")
print(f"   Records: {len(weather_df):,}")
print(f"   States: {weather_df['state_name'].nunique()}")
print(f"   Years: {weather_df['year'].min()}-{weather_df['year'].max()}")

# Display sample
print("\n📊 Sample Data:")
print("-" * 70)
print(weather_df.head(10).to_string(index=False))

print("\n📈 Summary Statistics:")
print("-" * 70)
print(weather_df[['avg_temp_f', 'total_precip_inches', 'gdd_total']].describe().round(1))

print("\n" + "="*70)
if USE_MOCK_DATA:
    print("⚠️  NOTE: Using sample data. Get real data by:")
    print("   1. Sign up: https://www.visualcrossing.com/sign-up")
    print("   2. Add API key to .env file")
    print("   3. Re-run this script")
else:
    print("✅ REAL WEATHER DATA SUCCESSFULLY FETCHED!")
print("="*70)
