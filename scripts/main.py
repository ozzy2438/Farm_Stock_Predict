import requests
import pandas as pd
import os

API_KEY = "2EEF90B1-825E-322B-8B27-098A9C92D575"
url = "https://quickstats.nass.usda.gov/api/api_GET/"

# 3 major crops to fetch
commodities = ["CORN", "SOYBEANS", "WHEAT"]

print("="*70)
print("🌾 FETCHING USDA NASS DATA - Yield + Acreage")
print("="*70)
print(f"\nCommodities: {', '.join(commodities)}")
print(f"Years: 2010-2024")
print(f"Metrics: YIELD + AREA HARVESTED\n")

def fetch_crop_data(commodity, statistic_category, batch_by_year=False):
    """
    Fetch crop data from USDA NASS QuickStats API

    Args:
        commodity: CORN, SOYBEANS, or WHEAT
        statistic_category: YIELD or AREA HARVESTED
        batch_by_year: If True, fetch year-by-year to avoid 413 errors

    Returns:
        DataFrame with cleaned data
    """
    all_data = []

    if batch_by_year:
        # Fetch year by year to avoid 413 errors
        for year in range(2010, 2025):
            params = {
                "key": API_KEY,
                "commodity_desc": commodity,
                "statisticcat_desc": statistic_category,
                "agg_level_desc": "STATE",
                "year": str(year),
                "format": "JSON"
            }

            try:
                r = requests.get(url, params=params, timeout=30)
                if r.status_code == 200:
                    data = r.json().get("data", [])
                    if data:
                        all_data.extend(data)
            except:
                pass
    else:
        # Fetch all years at once
        params = {
            "key": API_KEY,
            "commodity_desc": commodity,
            "statisticcat_desc": statistic_category,
            "agg_level_desc": "STATE",
            "year__GE": "2010",
            "format": "JSON"
        }

        try:
            r = requests.get(url, params=params, timeout=30)
            if r.status_code == 200:
                data = r.json().get("data", [])
                if data:
                    all_data = data
        except:
            pass

    if all_data:
        df = pd.DataFrame(all_data)

        # Filter out "OTHER STATES" aggregates
        df = df[df['state_name'] != 'OTHER STATES']

        df = df[["year", "state_name", "Value"]]
        df["commodity"] = commodity

        # Clean the Value column
        df["Value"] = (
            df["Value"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        # Remove disclosure codes
        df = df[~df["Value"].isin(["(D)", "(NA)", "(Z)", "(X)", ""])]

        # Convert to numeric
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
        df = df.dropna(subset=["Value"])

        return df

    return None

# Fetch YIELD data
print("📊 Fetching YIELD data...")
yield_frames = []

for commodity in commodities:
    print(f"  {commodity}...", end=" ")
    df = fetch_crop_data(commodity, "YIELD")

    if df is not None and len(df) > 0:
        yield_frames.append(df)
        print(f"✓ {len(df)} records")
    else:
        print("✗ No data")

# Fetch AREA HARVESTED data (batch by year to avoid 413 errors)
print("\n📊 Fetching AREA HARVESTED data...")
acreage_frames = []

for commodity in commodities:
    print(f"  {commodity}...", end=" ")
    df = fetch_crop_data(commodity, "AREA HARVESTED", batch_by_year=True)

    if df is not None and len(df) > 0:
        acreage_frames.append(df)
        print(f"✓ {len(df)} records")
    else:
        print("✗ No data")

# Combine yield and acreage data
if yield_frames and acreage_frames:
    # Combine yield data
    yield_df = pd.concat(yield_frames, ignore_index=True)
    yield_df = yield_df.rename(columns={"Value": "yield_per_acre"})

    # Combine acreage data
    acreage_df = pd.concat(acreage_frames, ignore_index=True)
    acreage_df = acreage_df.rename(columns={"Value": "acres_harvested"})

    # Merge yield and acreage on year, state, commodity
    final_df = pd.merge(
        yield_df,
        acreage_df,
        on=["year", "state_name", "commodity"],
        how="outer"
    )

    # Calculate total production (yield × acres)
    final_df["total_production"] = (
        final_df["yield_per_acre"] * final_df["acres_harvested"]
    )

    # Sort by commodity, year, state
    final_df = final_df.sort_values(
        ["commodity", "year", "state_name"]
    ).reset_index(drop=True)

    # Save to data/ folder
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    output_file = os.path.join(data_dir, "usda_crop_yield_2010_2024.csv")
    final_df.to_csv(output_file, index=False)

    print(f"\n{'='*70}")
    print(f"💾 Data saved to: {output_file}")
    print(f"   Total records: {len(final_df):,}")
    print(f"   Years: {final_df['year'].min()} - {final_df['year'].max()}")
    print(f"   States: {final_df['state_name'].nunique()}")
    print(f"   Commodities: {', '.join(final_df['commodity'].unique())}")
    print(f"{'='*70}\n")

    # Show summary statistics
    print("📊 Dataset Summary:")
    print("-" * 70)
    print(f"Records with YIELD data: {final_df['yield_per_acre'].notna().sum():,}")
    print(f"Records with ACREAGE data: {final_df['acres_harvested'].notna().sum():,}")
    print(f"Records with BOTH: {((final_df['yield_per_acre'].notna()) & (final_df['acres_harvested'].notna())).sum():,}")
    print("")

    # Show sample data
    print("Sample data (first 5 rows):")
    print("-" * 70)
    print(final_df.head(5).to_string(index=False))

    print(f"\n✅ Dataset ready for analysis!")
    print("   - yield_per_acre: Bushels per acre")
    print("   - acres_harvested: Total acres harvested")
    print("   - total_production: yield × acres (total bushels)")

else:
    print("\n✗ No data collected. Please check API key and parameters.")
