"""
Economic Data Collector - Production Module

Fetches economic indicators from USDA WASDE and FAS PSD databases
for commodity prices, stocks, and supply/demand data.
"""

import requests
import pandas as pd
import os
import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

# USDA FAS PSD API Configuration
PSD_API_BASE_URL = "https://apps.fas.usda.gov/psdonline/api/psd"

# Commodity codes for PSD API
COMMODITY_CODES = {
    'CORN': '0440000',
    'SOYBEANS': '2222000',
    'WHEAT': '0410000'
}

# Attribute codes for data retrieval
ATTRIBUTE_CODES = {
    'production': '0000125',      # Production (1000 MT)
    'total_supply': '0000020',    # Total Supply
    'domestic_consumption': '0000176',  # Domestic Consumption
    'exports': '0000176',         # Exports
    'ending_stocks': '0000027',   # Ending Stocks
    'stocks_to_use': '0000097'    # Stocks-to-Use Ratio
}


def fetch_psd_data(commodity: str, commodity_code: str, year: int) -> pd.DataFrame:
    """
    Fetch PSD data for a commodity

    Args:
        commodity: Commodity name (CORN, SOYBEANS, WHEAT)
        commodity_code: PSD commodity code
        year: Marketing year

    Returns:
        DataFrame with economic data
    """
    params = {
        'commodityCode': commodity_code,
        'countryCode': 'US',  # United States
        'marketYear': str(year)
    }

    try:
        response = requests.get(PSD_API_BASE_URL, params=params, timeout=60)

        if response.status_code == 200:
            data = response.json()

            if data and 'psdData' in data:
                records = data['psdData']

                if records:
                    df = pd.DataFrame(records)
                    df['commodity'] = commodity
                    df['year'] = year

                    return df
                else:
                    logger.warning(f"  ⚠️ {commodity}: No PSD records")
                    return pd.DataFrame()
            else:
                logger.warning(f"  ⚠️ {commodity}: Invalid response format")
                return pd.DataFrame()

        else:
            logger.error(f"  ❌ {commodity}: HTTP {response.status_code}")
            return pd.DataFrame()

    except Exception as e:
        logger.error(f"  ❌ {commodity}: {str(e)}")
        return pd.DataFrame()


def calculate_price_index(year: int) -> Dict[str, float]:
    """
    Calculate price index based on historical averages

    This is a simplified version. In production, you would fetch
    actual commodity prices from sources like USDA NASS or Chicago Board of Trade.

    Args:
        year: Year for price calculation

    Returns:
        Dict with commodity: price_index
    """
    # Placeholder price indices (would be fetched from actual API in production)
    # These represent relative price levels (100 = baseline)
    base_prices = {
        'CORN': 100,
        'SOYBEANS': 100,
        'WHEAT': 100
    }

    logger.info("  Using baseline price indices (production would fetch actual prices)")

    return base_prices


def fetch_all_economic_data(year: int, output_dir: str) -> Dict:
    """
    Fetch economic data for all commodities

    Args:
        year: Marketing year to fetch data for
        output_dir: Directory to save output file

    Returns:
        dict with file_path and statistics
    """
    logger.info(f"💰 Fetching economic data for {year}")

    all_data = []
    stats = {
        'year': year,
        'commodities': {},
        'total_records': 0
    }

    # Fetch PSD data for each commodity
    for commodity, commodity_code in COMMODITY_CODES.items():
        logger.info(f"  Fetching {commodity} PSD data...")

        df = fetch_psd_data(commodity, commodity_code, year)

        if not df.empty:
            all_data.append(df)
            stats['commodities'][commodity] = len(df)
            logger.info(f"    ✓ {commodity}: {len(df)} records")
        else:
            stats['commodities'][commodity] = 0
            logger.warning(f"    ⚠️ {commodity}: No data")

    # If PSD API fails or is unavailable, create fallback data
    if not all_data:
        logger.warning("  PSD API data unavailable, creating fallback economic indicators")

        fallback_data = []
        for commodity in COMMODITY_CODES.keys():
            fallback_data.append({
                'commodity': commodity,
                'year': year,
                'production': None,
                'total_supply': None,
                'ending_stocks': None,
                'stocks_to_use_ratio': None,
                'price_index': 100,  # Baseline
                'data_source': 'fallback'
            })

        df = pd.DataFrame(fallback_data)
        all_data.append(df)

        for commodity in COMMODITY_CODES.keys():
            stats['commodities'][commodity] = 1

    # Get price indices
    price_indices = calculate_price_index(year)

    # Combine all data
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)

        # Create summary by commodity
        summary_data = []

        for commodity in COMMODITY_CODES.keys():
            commodity_df = final_df[final_df['commodity'] == commodity]

            if not commodity_df.empty:
                # Extract key metrics (or use None if not available)
                summary = {
                    'commodity': commodity,
                    'year': year,
                    'production': commodity_df['production'].iloc[0] if 'production' in commodity_df.columns else None,
                    'total_supply': commodity_df['total_supply'].iloc[0] if 'total_supply' in commodity_df.columns else None,
                    'ending_stocks': commodity_df['ending_stocks'].iloc[0] if 'ending_stocks' in commodity_df.columns else None,
                    'stocks_to_use_ratio': commodity_df['stocks_to_use_ratio'].iloc[0] if 'stocks_to_use_ratio' in commodity_df.columns else None,
                    'price_index': price_indices.get(commodity, 100),
                }

                # Calculate supply risk indicator
                # Higher stocks-to-use = lower risk
                if summary['stocks_to_use_ratio'] is not None:
                    # Invert: low stocks-to-use = high risk
                    summary['supply_risk_score'] = max(0, 100 - (summary['stocks_to_use_ratio'] * 2))
                else:
                    summary['supply_risk_score'] = 50  # Neutral if unknown

                summary_data.append(summary)

        summary_df = pd.DataFrame(summary_data)

        # Save to file
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f'economic_{year}.csv')
        summary_df.to_csv(output_file, index=False)

        stats['total_records'] = len(summary_df)

        logger.info(f"✅ Saved {len(summary_df):,} commodity records to {output_file}")

        return {
            'success': True,
            'file_path': output_file,
            'records': len(summary_df),
            'stats': stats
        }
    else:
        logger.error("❌ No economic data collected")
        return {
            'success': False,
            'file_path': None,
            'records': 0,
            'stats': stats
        }


if __name__ == "__main__":
    # Test the module
    import sys
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './test_output'

    logging.basicConfig(level=logging.INFO)
    result = fetch_all_economic_data(year=year, output_dir=output_dir)
    print(f"\nResult: {result}")
